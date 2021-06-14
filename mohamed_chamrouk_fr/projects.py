from flask_login import login_required, current_user
from mohamed_chamrouk_fr import spotify_threading
from flask import (Blueprint, render_template, request,
                   flash, redirect, url_for, abort)
from mohamed_chamrouk_fr import conn
from mohamed_chamrouk_fr import app
import threading


proj = Blueprint('projects', __name__)


@proj.route("/projects/")
def projects():
    projects = get_all_projects()
    return render_template('projects/projects.html', projects=projects,
    thread= True if not spotify_threading.stop_threads and "Thread-spotify" in [thread.name for thread in threading.enumerate()] else False)


@proj.route("/projects/create", methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        source = request.form['source']
        idproject = request.form['idproject']

        error = None

        if not title:
            error = 'Titre requis.'

        if error is not None:
            flash(error)
        else:
            with conn.connect() as connection:
                connection.execute(
                    'INSERT INTO projects (title, body, idproject, source)'
                    ' VALUES (%s, %s, %s, %s)',
                    title, body, idproject, source
                )
            return redirect(url_for('projects.projects'))

    return render_template('projects/create.html')


@proj.route('/projects/update/<int:id>/', methods=('GET', 'POST'))
@login_required
def update(id):
    project = get_project(id)

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        source = request.form['source']
        idproject = request.form['idproject']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            with conn.connect() as connection:
                connection.execute(
                    'UPDATE projects SET title = %s, body = %s, source = %s, idproject = %s'
                    ' WHERE id = %s',
                    (title, body, source, idproject, id)
                )
            return redirect(url_for('home'))

    return render_template('projects/update.html', project=project)


@proj.route('/projects/delete/<int:id>/', methods=('POST',))
@login_required
def delete(id):
    get_project(id)
    with conn.connect() as connection:
        connection.execute('DELETE FROM projects WHERE id = %s', (id,))
    return redirect(url_for('projects.projects'))


def get_project(id):
    with conn.connect() as connection:
        project = connection.execute(
            'SELECT id, title, body, idproject, source'
            ' FROM projects '
            ' WHERE id = %s',
            (id,)
        ).fetchone()

    if project is None:
        abort(404, f"Le Post d'id {id} n'existe pas.")
    return project


def get_all_projects():
    with conn.connect() as connection:
        projects = connection.execute(
            'SELECT id, title, body, idproject, source'
            ' FROM projects').fetchall()
    return projects
