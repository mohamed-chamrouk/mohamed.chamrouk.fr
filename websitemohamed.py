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


app = Flask(__name__)

db = SQLAlchemy(app)
migrate = Migrate(app, db)
login_manager = LoginManager()
login_manager.init_app(app)


class RequestFormatter(logging.Formatter):
    def format(self, record):
        if has_request_context():
            record.url = request.url
            record.remote_addr = request.remote_addr
        else:
            record.url = None
            record.remote_addr = None

        return super().format(record)


formatter = RequestFormatter(
    '[%(asctime)s] %(remote_addr)s requested %(url)s\n'
    '%(levelname)s in %(module)s: %(message)s'
)
default_handler.setFormatter(formatter)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # primary keys are required by SQLAlchemy
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))


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
    app.logger.info('Processing default request at URL : '+request.url+' \
    from addr : '+request.remote_addr)
    with engine.connect() as connection:
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
    return render_template('dashboard/dashboard.html')


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
            with engine.connect() as connection:
                connection.execute(
                    'INSERT INTO post (title, body, author_id)'
                    ' VALUES (%s, %s, %s)',
                    title, body, current_user.get_id()
                )
            db.session.commit()
            return redirect(url_for('home'))

    return render_template('blog/create.html')


def get_post(id, check_author=True):
    with engine.connect() as connection:
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


@app.route('/blog/<int:id>/update/', methods=('GET', 'POST'))
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
            with engine.connect() as connection:
                connection.execute(
                    'UPDATE post SET title = %s, body = %s'
                    ' WHERE id = %s',
                    (title, body, id)
                )
            db.session.commit()
            return redirect(url_for('home'))

    return render_template('blog/update.html', post=post)


@app.route('/blog/<int:id>/delete/', methods=('POST',))
@login_required
def delete(id):
    get_post(id)
    with engine.connect() as connection:
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
    app.run(debug=True)
