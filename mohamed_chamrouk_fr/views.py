import urllib
import math
import git
import httpagentparser
import json
import hashlib
from mohamed_chamrouk_fr.database import (create_session,
                                          update_or_create_page,
                                          select_all_sessions,
                                          select_num_sessions,
                                          select_num_countries,
                                          select_num_cities)
from flask_login import login_required
from flask import (render_template, session, request)
from markdown import markdown
from datetime import datetime
from mohamed_chamrouk_fr import app, conn, cache
from mohamed_chamrouk_fr.auth import auth
from mohamed_chamrouk_fr.blog import blog


app.register_blueprint(auth)
app.register_blueprint(blog)

userOS = None
userIP = None
userCity = None
userBrowser = None
userCountry = None
userContinent = None
sessionID = None


@cache.cached(timeout=3600, key_prefix='all_comments')
def get_git_log(branch):
    g = git.Git("/home/mohamed_chamrouk_fr")
    sha = g.log('--pretty=format:%h')
    message = g.log('--pretty=format:%B')
    author = g.log('--pretty=format:%aN')
    date = g.log('--pretty=format:%cD')
    dict_log_list = []
    j = 0
    for i in range(len(sha.split('\n'))):
        if message.split('\n')[i] != '':
            dict_log_list.append({})
            dict_log_list[j]['sha'] = sha.split('\n')[i]
            dict_log_list[j]['message'] = message.split('\n')[i]
            dict_log_list[j]['author'] = author.split('\n')[i]
            dict_log_list[j]['date'] = date.split('\n')[i]
            j += 1
    return dict_log_list


def parseVisitor(data):
    update_or_create_page(conn, data)


def getAnalyticsData():
    global userOS, userBrowser, userIP, userContinent, userCity, userCountry, sessionID
    userInfo = httpagentparser.detect(request.headers.get('User-Agent'))
    userOS = userInfo['platform']['name']
    userBrowser = userInfo['browser']['name']
    userIP = '157.159.42.21' if request.remote_addr == '127.0.0.1' else request.remote_addr
    api = "https://www.iplocate.io/api/lookup/" + userIP
    try:
        resp = urllib.request.urlopen(api)
        result = resp.read()
        result = json.loads(result.decode("utf-8"))
        userCountry = result["country"]
        userContinent = result["continent"]
        userCity = result["city"]
    except:
        print("Could not find: ", userIP)
        userCountry = "unknown"
        userContinent = "unknown"
        userCity = "unknown"
    userCountry = "unknown" if userCountry is None else userCountry
    userCity = "unknown" if userCity is None else userCity
    userContinent = "unknown" if userContinent is None else userContinent
    getSession()


def getSession():
    global sessionID
    time = datetime.now().replace(microsecond=0)
    if 'user' not in session:
        lines = (str(time)+userIP).encode('utf-8')
        session['user'] = hashlib.md5(lines).hexdigest()
        sessionID = session['user']
        data = [userIP, userContinent, userCountry,
                userCity, userOS, userBrowser, sessionID, time]
        create_session(conn, data)
    else:
        sessionID = session['user']


def get_all_sessions():
    data = []
    dbRows = select_all_sessions(conn)
    for row in dbRows:
        data.append({
            'ip': row['ip'],
            'continent': row['continent'],
            'country': row['country'],
            'city': row['city'],
            'os': row['os'],
            'browser': row['browser'],
            'session': row['session'],
            'time': row['created_at']
        })
    return data[::-1]


def get_num_sessions():
    dates = []
    values = []
    dbRows = select_num_sessions(conn)
    for row in dbRows:
        dates.append(row['created_at'].strftime("%d-%m-%Y"))
        values.append(row['count'])
    return dates, values


def get_num_countries(limit):
    countries = []
    values = []
    dbRows = select_num_countries(conn)
    dbRowsReduc = dbRows[len(dbRows)-limit:] if limit > 0 and limit < len(dbRows) else dbRows
    for row in dbRowsReduc:
        countries.append(str(row['country']))
        values.append(row['count'])
    if limit > 0 and limit < len(dbRows):
        countries.insert(0, 'others')
        values.insert(0, sum(item['count'] for item in dbRows[:len(dbRows)-limit]))
    return countries, values


def get_num_cities(limit):
    cities = []
    values = []
    dbRows = select_num_cities(conn)
    dbRowsReduc = dbRows[len(dbRows)-limit:] if limit > 0 and limit < len(dbRows) else dbRows
    for row in dbRowsReduc:
        cities.append(str(row['city']))
        values.append(row['count'])
    if limit > 0 and limit < len(dbRows):
        cities.insert(0, 'others')
        values.insert(0, sum(item['count'] for item in dbRows[:len(dbRows)-limit]))
    return cities, values


@app.route("/portfolio/")
def portfolio():
    getAnalyticsData()
    return render_template('portfolio.html')


@app.route("/")
def home():
    getAnalyticsData()
    with conn.connect() as connection:
        posts = connection.execute(
            'SELECT p.id, title, body, created, hide, author_id, username, u.name'
            ' FROM post p JOIN public."user" u ON p.author_id = u.id'
            ' ORDER BY created DESC').fetchall()
    total_page = math.ceil(len(posts)/5)
    page = request.args.get("page")

    if page:
        if int(page) > total_page:
            page = total_page
        else:
            page = int(page)
        last_post = 5+5*(page-1) if len(posts) >= 5+5*(page-1) else len(posts)
    else:
        page = 1
        last_post = len(posts)-1 if total_page > 1 else len(posts)

    git_log = get_git_log('main')
    return render_template('blog/blog.html', posts=posts[(page-1)*5:last_post],
                           markdown=markdown, current_page=page,
                           total_page=total_page, git_log=git_log,
                           length=len(git_log)+1)


@app.route("/dashboard")
@login_required
def dashboard():
    getAnalyticsData()
    dates, values_d = get_num_sessions()
    countries, values_co = get_num_countries(8)
    cities, values_ci = get_num_cities(12)
    return render_template('dashboard/dashboard.html', get_all_sessions=
                           get_all_sessions, len=len, min=min,
                           dates=dates[max(0, len(dates)-7):],
                           countries=countries, cities=cities,
                           values=values_d[max(0, len(values_d)-7):],
                           values_co=values_co,
                           values_ci=values_ci)


if __name__ == '__main__':
    app.run(debug=True)
