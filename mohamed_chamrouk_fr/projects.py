from flask import Blueprint, render_template


proj = Blueprint('projects', __name__)


@proj.route("/projects/")
def projects():
    return render_template('projects/projects.html')
