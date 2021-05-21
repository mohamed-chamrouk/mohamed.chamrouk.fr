import urllib
import math
import git
import httpagentparser
import json
import hashlib
from mohamed_chamrouk_fr.database import (create_session, update_or_create_page,
                                          select_all_sessions)
from flask_login import login_required
from flask import (render_template, session, request)
from markdown import markdown
from datetime import datetime
from mohamed_chamrouk_fr import app, conn, c
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


def get_git_log(branch):
    g = git.Git("/home/snow/mohamed_chamrouk_fr")
    sha = g.log('--pretty=format:%h')
    message = g.log('--pretty=format:%B')
    author = g.log('--pretty=format:%aN')
    date = g.log('--pretty=format:%cD')
    dict_log_list = []
    for i in range(len(sha.split('\n'))):
        dict_log_list.append({})
        dict_log_list[i]['sha'] = sha.split('\n')[i]
        dict_log_list[i]['message'] = message.split('\n')[i]
        dict_log_list[i]['author'] = author.split('\n')[i]
        dict_log_list[i]['date'] = date.split('\n')[i]
    app.logger.info(dict_log_list)
    return dict_log_list


def monitoring_main():
    global conn, c


def parseVisitor(data):
    update_or_create_page(c, data)


@app.before_request
def getAnalyticsData():
    global userOS, userBrowser, userIP, userContinent, userCity, userCountry, sessionID
    userInfo = httpagentparser.detect(request.headers.get('User-Agent'))
    userOS = userInfo['platform']['name']
    userBrowser = userInfo['browser']['name']
    userIP = "212.111.40.134" if request.remote_addr == '127.0.0.1' else request.remote_addr
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
        create_session(c, data)
    else:
        sessionID = session['user']


def get_all_sessions():
    data = []
    dbRows = select_all_sessions(c)
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
    return data


@app.route("/portfolio/")
def portfolio():
    return render_template('portfolio.html')


@app.route("/")
def home():
    with conn.connect() as connection:
        posts = connection.execute(
            'SELECT p.id, title, body, created, author_id, username, u.name'
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
                           total_page=total_page, git_log=git_log)


@app.route("/dashboard")
@login_required
def dashboard():
    return render_template('dashboard/dashboard.html', get_all_sessions=
                           get_all_sessions, len=len, min=min)


if __name__ == '__main__':
    monitoring_main()
    app.run(debug=True)
