import threading
import mohamed_chamrouk_fr.startup as startup
import mohamed_chamrouk_fr.spotify_threading as spotify_thread
from flask import redirect, Blueprint, request, render_template
from flask_login import login_required

spot = Blueprint('project_spotify', __name__)


@spot.route("/projects/spotify_auth/")
@login_required
def project_spotify():
    response = startup.getUser()
    return redirect(response)


@spot.route("/projects/spotify/")
@login_required
def auth():
    startup.getUserToken(request.args.get('code'))
    if "Thread-spotify" not in [thread.name for thread in threading.enumerate()]:
        sp_t = spotify_thread(3500)
        sp_t.start()
    return render_template('projects/spotify/spotify.html')
