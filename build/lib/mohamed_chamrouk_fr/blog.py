from flask_login import login_required, current_user
from flask import (flash, redirect, request, url_for, Blueprint,
                   render_template, abort)
from mohamed_chamrouk_fr import app, conn
from markdown import markdown

blog = Blueprint('blog', __name__)


@blog.route("/blog/<int:id>")
def detail(id):
    post = get_post(id)
    return render_template('blog/blog_solo.html', post=post, markdown=markdown)


@blog.route('/blog/create/', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        try:
            hidden = request.form['hide']
        except KeyError:
            hidden = 'False'
        error = None

        if not title:
            error = 'Titre requis.'

        if error is not None:
            flash(error)
        else:
            with conn.connect() as connection:
                connection.execute(
                    'INSERT INTO post (title, body, author_id, hide)'
                    ' VALUES (%s, %s, %s, %s)',
                    title, body, current_user.get_id(), hidden
                )
            return redirect(url_for('home'))

    return render_template('blog/create.html')


def get_post(id, check_author=True):
    with conn.connect() as connection:
        post = connection.execute(
            'SELECT p.id, title, body, created, hide, author_id, username, u.name'
            ' FROM post p JOIN public."user" u ON p.author_id = u.id'
            ' WHERE p.id = %s',
            (id,)
        ).fetchone()

    if post is None:
        abort(404, f"Le Post d'id {id} n'existe pas.")

    if check_author and current_user is None and post['author_id'] != \
       int(current_user.get_id()):
        abort(403)

    return post


@blog.route('/blog/update/<int:id>/', methods=('GET', 'POST'))
@login_required
def update(id):
    post = get_post(id)

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        try:
            hidden = request.form['hide']
        except KeyError:
            hidden = 'False'
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            with conn.connect() as connection:
                connection.execute(
                    'UPDATE post SET title = %s, body = %s, hide = %s'
                    ' WHERE id = %s',
                    (title, body, hidden, id)
                )
            return redirect(url_for('home'))

    return render_template('blog/update.html', post=post)


@blog.route('/blog/delete/<int:id>/', methods=('POST',))
@login_required
def delete(id):
    get_post(id)
    with conn.connect() as connection:
        connection.execute('DELETE FROM post WHERE id = %s', (id,))
    return redirect(url_for('home'))
