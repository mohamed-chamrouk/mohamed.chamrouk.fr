import datetime
import functools
import os
import re
import urllib
import math
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import current_user, login_user, LoginManager, login_required, UserMixin, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask import (Flask, abort, flash, redirect, render_template,
                   request, url_for, has_request_context, request)
from markdown import markdown
from markdown.extensions import fenced_code
from sqlalchemy.dialects import postgresql
from sqlalchemy import create_engine
from werkzeug.exceptions import abort
from flask.logging import default_handler
import logging
from logging.config import dictConfig
from flask import Flask, render_template, request, session, jsonify
from datetime import datetime
import httpagentparser
import json
import os
import hashlib
from databaseTrafficMonitoring import create_connection, create_session, update_or_create_page, select_all_sessions, select_all_user_visits, select_all_pages
app = Flask(__name__)

app.config.from_envvar('WEBSITE_SETTINGS')

conn = create_connection(app, 'website_db')
c = conn
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login_manager = LoginManager()
login_manager.init_app(app)
# new_user = User(username="snow", name="snow", password=generate_password_hash("", method='sha256'))
# db.session.add(new_user)
# db.session.commit()

userOS = None
userIP = None
userCity = None
userBrowser = None
userCountry = None
userContinent = None
sessionID = None


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # primary keys are required by SQLAlchemy
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))


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


@login_manager.user_loader
def load_user(user_id):
    # since the user_id is just the primary key of our user table,
    # use it in the query for the user
    return User.query.get(int(user_id))


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
    return render_template('blog/blog.html', posts=posts[(page-1)*5:last_post],
                           markdown=markdown, current_page=page,
                           total_page=total_page)


@app.route("/dashboard")
@login_required
def dashboard():
    return render_template('dashboard/dashboard.html', get_all_sessions=
                           get_all_sessions, len=len, min=min)


@app.route("/blog/<int:id>")
def detail(id):
    post = get_post(id)
    app.logger.info(post)
    return render_template('blog/blog_solo.html', post=post, markdown=markdown)


@app.route('/blog/create/', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        app.logger.info(request)
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Titre requis.'

        if error is not None:
            flash(error)
        else:
            with conn.connect() as connection:
                connection.execute(
                    'INSERT INTO post (title, body, author_id)'
                    ' VALUES (%s, %s, %s)',
                    title, body, current_user.get_id()
                )
            db.session.commit()
            return redirect(url_for('home'))

    return render_template('blog/create.html')


def get_post(id, check_author=True):
    with conn.connect() as connection:
        post = connection.execute(
            'SELECT p.id, title, body, created, author_id, username, u.name'
            ' FROM post p JOIN public."user" u ON p.author_id = u.id'
            ' WHERE p.id = %s',
            (id,)
        ).fetchone()

    if post is None:
        abort(404, f"Le Post d'id {id} n'existe pas.")

    if check_author and current_user is None and post['author_id'] != \
       int(current_user.get_id()):
        app.logger.info('auteur : '+str(post['author_id'])+', utilisateur : '
                                   + current_user.get_id())
        abort(403)

    return post


@app.route('/blog/update/<int:id>/', methods=('GET', 'POST'))
@login_required
def update(id):
    post = get_post(id)

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            with conn.connect() as connection:
                connection.execute(
                    'UPDATE post SET title = %s, body = %s'
                    ' WHERE id = %s',
                    (title, body, id)
                )
            db.session.commit()
            return redirect(url_for('home'))

    return render_template('blog/update.html', post=post)


@app.route('/blog/delete/<int:id>/', methods=('POST',))
@login_required
def delete(id):
    get_post(id)
    with conn.connect() as connection:
        connection.execute('DELETE FROM post WHERE id = %s', (id,))
    db.session.commit()
    return redirect(url_for('home'))


@app.route('/login', methods=['POST'])
def login_post():
    username = request.form.get('username')
    password = request.form.get('password')

    user = User.query.filter_by(username=username).first()

    # check if the user actually exists
    # take the user-supplied password, hash it, and compare it to the
    # hashed password in the database
    if not user or not check_password_hash(user.password, password):
        flash('Veuillez vérifier vos informations et réessayer.')
        return redirect(url_for('home'))
    # if the above check passes, then we know the user
    # has the right credentials
    flash('logged in')
    login_user(user)
    return redirect(url_for('home'))


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))


if __name__ == '__main__':
    monitoring_main()
    app.run(debug=True)
