import threading
import requests
import json
import uwsgi
import mohamed_chamrouk_fr.startup as startup
from mohamed_chamrouk_fr import app, conn
from mohamed_chamrouk_fr.spotify_threading import spotify_thread
import mohamed_chamrouk_fr.spotify_threading as spotify_threading
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

uwsgi.cache_clear()

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
    if not uwsgi.cache_exists('isRunning'):
        app.logger.info("Creating new thread for refreshing spotify token and user stats.")
        uwsgi.cache_set('isRunning', 'True')
        uwsgi.cache_set('stop_threads', 'False')
        sp_t = spotify_thread(2500, "Thread-spotify")
        sp_t.start()
    try:
        if uwsgi.cache_get('isRunning').decode('utf-8') == 'True' and uwsgi.cache_get('stop_threads').decode('utf-8') == 'True':
            app.logger.info("Relancement de l'application spotify")
            uwsgi.cache_update('stop_threads', 'False')
    except AttributeError: 
        app.logger.error(f"La variable isRunning ou stop_threads n'est pas initialisée, valeurs : ir:{uwsgi.cache_get('isRunning')} et st:{uwsgi.cache_get('stop_threads')}")
    list_time_range = ['short_term', 'medium_term', 'long_term']
    list_type = ['artists', 'tracks']
    dict_index = {'short_term_artists' : 1, 'medium_term_artists' : 2,'long_term_artists' : 3,
                  'short_term_tracks' : 4, 'medium_term_tracks' : 5, 'long_term_tracks' : 6}

    for type in list_type:
        for time_range in list_time_range:
            set_analytics_data(dict_index[f"{time_range}_{type}"],
                               json.dumps(json.loads(get_users_top(
                                startup.getAccessToken()[1],
                                type,
                                time_range,))),
                               time_range,
                               type)

    app.logger.info(f"All the threads are listed below : {[thread.name for thread in threading.enumerate()]}")

    return redirect(url_for('project_spotify.spotify'))


@spot.route("/projects/spotify/", methods=["POST", "GET"])
@login_required
def spotify():
    if request.method == 'POST':
        dict = {'Court': 'short_term', 'Moyen': 'medium_term', 'Long': 'long_term'}
        term = getcookie() if request.form.get('term') is None else dict[request.form.get('term')]
        res = make_response(render_template('projects/spotify/spotify.html',
                            tartists=get_analytics_data(term, "artists")['items'],
                            ttracks=get_analytics_data(term, "tracks")['items'],
                            talltime=getcatfunction() if request.form.get('cat') is None else (get_top_artists() if request.form.get('cat') == "Artistes" else get_top_tracks()),
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

    return render_template('projects/spotify/spotify.html',
                           tartists=get_analytics_data(getcookie(), "artists")['items'],
                           ttracks=get_analytics_data(getcookie(), "tracks")['items'],
                           talltime=getcatfunction(),
                           category=getcatcookie())


@spot.route("/projects/spotify_kill/")
@login_required
def kill():
    try:
        uwsgi.cache_update('stop_threads', 'True')
        app.logger.info(f"Application spotify mise en pause avec : {uwsgi.cache_get('stop_threads')}")
    except:
        app.logger.info("Couldn't kill process")
    return redirect(url_for('projects.projects'))


def getcookie():
    return ('long_term' if request.cookies.get('time_range') is None else request.cookies.get('time_range'))


def getcatcookie():
    return ('Musiques' if request.cookies.get('category') is None else request.cookies.get('category'))


def getcatfunction():
    return (get_top_artists() if getcatcookie() == 'Artistes' else get_top_tracks())


def get_users_top(auth_header, t, time_range):
    if t not in ['artists', 'tracks']:
        print('invalid type')
        return None
    params = {'limit': 50, 'time_range': time_range}
    url = f"{USER_TOP_ARTISTS_AND_TRACKS_ENDPOINT}/{t}"
    resp = requests.get(url, headers=auth_header, params=params)
    return resp.text


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
    return data[:50 if len(data) > 50 else len(data)]


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
    return data[:50 if len(data) > 50 else len(data)]


def get_analytics_data(time_range, type):
    with conn.connect() as connection:
        analy = connection.execute(
        'SELECT json'
        ' FROM public.spotify_analytics'
        '  WHERE time_range = %s AND type = %s',
        (time_range,type)
        ).fetchone()
        r_list = [row for row in analy]
    return json.loads(r_list[0])

def set_analytics_data(id, json, time_range, type):
    with conn.connect() as connection:
        connection.execute(
        'INSERT INTO spotify_analytics (id, json, time_range, type)'
        ' VALUES (%s, %s, %s, %s)'
        '  ON CONFLICT (id) DO UPDATE'
        '   SET json = EXCLUDED.json, time_range = EXCLUDED.time_range, type = EXCLUDED.type',
        id, json, time_range, type
        )
