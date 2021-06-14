import threading
import requests
import mohamed_chamrouk_fr.startup as startup
from mohamed_chamrouk_fr import app, conn
from mohamed_chamrouk_fr.spotify_threading import spotify_thread
from flask import (redirect, Blueprint, request, render_template, url_for,
                   make_response)
from flask_login import login_required


SPOTIFY_API_BASE_URL = 'https://api.spotify.com'
API_VERSION = "v1"
SPOTIFY_API_URL = "{}/{}".format(SPOTIFY_API_BASE_URL, API_VERSION)

USER_PROFILE_ENDPOINT = "{}/{}".format(SPOTIFY_API_URL, 'me')
USER_PLAYLISTS_ENDPOINT = "{}/{}".format(USER_PROFILE_ENDPOINT, 'playlists')
USER_TOP_ARTISTS_AND_TRACKS_ENDPOINT = "{}/{}".format(
    USER_PROFILE_ENDPOINT, 'top')  # /<type>
USER_RECENTLY_PLAYED_ENDPOINT = "{}/{}/{}".format(USER_PROFILE_ENDPOINT,
                                                  'player', 'recently-played')
BROWSE_FEATURED_PLAYLISTS = "{}/{}/{}".format(SPOTIFY_API_URL, 'browse',
                                              'featured-playlists')

RECENTLY_PLAYED = ""
TOP_ARTISTS_SHORT = ""
TOP_ARTISTS_MEDIUM = ""
TOP_ARTISTS_LONG = ""
TOP_TRACKS_SHORT = ""
TOP_TRACKS_MEDIUM = ""
TOP_TRACKS_LONG = ""


spot = Blueprint('project_spotify', __name__)


@spot.route("/projects/spotify_auth/")
@login_required
def auth():
    response = startup.getUser()
    return redirect(response)


@spot.route("/projects/spotify_callback/")
@login_required
def callback():
    startup.getUserToken(request.args.get('code'))
    if "Thread-spotify" not in [thread.name for thread in threading.enumerate()]:
        app.logger.info("Creating new thread for refreshing spotify token and user stats.")
        sp_t = spotify_thread(3500, "Thread-spotify")
        sp_t.start()

        #sp_stat_t = spotify_thread(5000, "Thread-stat-spotify")
        #sp_stat_t.start()
    global TOP_ARTISTS, TOP_TRACKS, RECENTLY_PLAYED, TOP_TRACKS_SHORT, TOP_TRACKS_MEDIUM, TOP_TRACKS_LONG, TOP_ARTISTS_SHORT, TOP_ARTISTS_MEDIUM, TOP_ARTISTS_LONG
    TOP_ARTISTS_SHORT = get_users_top(startup.getAccessToken()[1], 'artists', 'short_term')
    TOP_ARTISTS_MEDIUM = get_users_top(startup.getAccessToken()[1], 'artists', 'medium_term')
    TOP_ARTISTS_LONG = get_users_top(startup.getAccessToken()[1], 'artists', 'long_term')
    TOP_TRACKS_SHORT = get_users_top(startup.getAccessToken()[1], 'tracks', 'short_term')
    TOP_TRACKS_MEDIUM = get_users_top(startup.getAccessToken()[1], 'tracks', 'medium_term')
    TOP_TRACKS_LONG = get_users_top(startup.getAccessToken()[1], 'tracks', 'long_term')
    TOP_ARTISTS = {'long_term': TOP_ARTISTS_LONG, 'medium_term': TOP_ARTISTS_MEDIUM,
                   'short_term': TOP_ARTISTS_SHORT}
    TOP_TRACKS = {'long_term': TOP_TRACKS_LONG, 'medium_term': TOP_TRACKS_MEDIUM,
                  'short_term': TOP_TRACKS_SHORT}
    return redirect(url_for('project_spotify.spotify'))


@spot.route("/projects/spotify/", methods=["POST", "GET"])
@login_required
def spotify():
    if request.method == 'POST':
        dict = {'Court': 'short_term', 'Moyen': 'medium_term', 'Long': 'long_term'}
        res = make_response(render_template('projects/spotify/spotify.html',
                            tartists=TOP_ARTISTS[getcookie() if request.form.get('term') is None else dict[request.form.get('term')]]['items'],
                            ttracks=TOP_TRACKS[getcookie() if request.form.get('term') is None else dict[request.form.get('term')]]['items'],
                            talltime=get_top_artists() if request.form.get('cat') == "Artistes" else get_top_tracks(),
                            category=getcatcookie() if request.form.get('cat') is None else request.form.get('cat')))
        try:
            res.set_cookie("time_range", dict[request.form.get('term')])
        except:
            app.logger.error("No cookie term found.")

        try:
            res.set_cookie("category", request.form.get('cat'))
        except:
            app.logger.error("No cookie cat found.")
        return res, 302
        
    if TOP_ARTISTS_LONG == "":
        return redirect(url_for('project_spotify.auth'))
    if getcatcookie() == "Artistes":
        talltime = get_top_artists()
    else:
        talltime = get_top_tracks()
    return render_template('projects/spotify/spotify.html',
                           tartists=TOP_ARTISTS[getcookie()]['items'],
                           ttracks=TOP_TRACKS[getcookie()]['items'],
                           talltime=talltime,
                           category=getcatcookie())


def getcookie():
    return 'long_term' if request.cookies.get('time_range') is None else request.cookies.get('time_range')


def getcatcookie():
    return 'Musiques' if request.cookies.get('category') is None else request.cookies.get('category')


def get_users_top(auth_header, t, time_range):
    if t not in ['artists', 'tracks']:
        print('invalid type')
        return None
    params = {'limit': 50, 'time_range': time_range}
    url = f"{USER_TOP_ARTISTS_AND_TRACKS_ENDPOINT}/{t}"
    resp = requests.get(url, headers=auth_header, params=params)
    return resp.json()


def get_top_tracks():
    with conn.connect() as connection:
        stats = connection.execute(
            'SELECT s.track, s.artist, s.url_track, count(s.track)'
            ' FROM public.spotify_stat s'
            '  GROUP BY track, artist, url_track'
            '   ORDER BY count DESC'
        ).fetchall()
    data = []
    for row in stats:
        data.append({
        'title': row['track'],
        'artist': row['artist'],
        'url_track': row['url_track'],
        'count': row['count']
        })
    return data

def get_top_artists():
    with conn.connect() as connection:
        stats = connection.execute(
            'SELECT s.artist, count(s.artist)'
            ' FROM public.spotify_stat s'
            '  GROUP BY artist'
            '   ORDER BY count DESC'
        ).fetchall()
    data = []
    for row in stats:
        data.append({
        'artist': row['artist'],
        'count': row['count']
        })
    return data
