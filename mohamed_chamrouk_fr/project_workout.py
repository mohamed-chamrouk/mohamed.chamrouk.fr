import requests
import mohamed_chamrouk_fr.startup as startup
from flask import (redirect, Blueprint, request, render_template, url_for,
                   make_response)
from flask_login import login_required

wkt = Blueprint('project_workout', __name__)


@wkt.route("/projects/workout/")
@login_required
def auth():
    return render_template('projects/workout/workout.html')
