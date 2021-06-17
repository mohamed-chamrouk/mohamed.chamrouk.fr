from mohamed_chamrouk_fr.flask_spotify_auth import getAuth, refreshAuth, getToken
from mohamed_chamrouk_fr import app, conn
import time
import requests

SPOTIFY_API_BASE_URL = 'https://api.spotify.com'
API_VERSION = "v1"
SPOTIFY_API_URL = "{}/{}".format(SPOTIFY_API_BASE_URL, API_VERSION)

USER_PROFILE_ENDPOINT = "{}/{}".format(SPOTIFY_API_URL, 'me')
USER_RECENTLY_PLAYED_ENDPOINT = "{}/{}/{}".format(USER_PROFILE_ENDPOINT,
                                                  'player', 'recently-played')

#Add your client ID
CLIENT_ID = app.config['CLIENT_ID']

#aDD YOUR CLIENT SECRET FROM SPOTIFY
CLIENT_SECRET = app.config['CLIENT_SECRET']

#Port and callback url can be changed or ledt to localhost:5000
PORT = "5000"
CALLBACK_URL = "http://127.0.0.1"
#CALLBACK_URL = "https://mohamed.chamrouk.fr"
CALLBACK = "projects/spotify_callback"

#Add needed scope from spotify user
SCOPE = "streaming user-read-email user-read-private user-read-recently-played user-top-read"
#token_data will hold authentication header with access code, the allowed scopes, and the refresh countdown
TOKEN_DATA = []


def getUser():
    return getAuth(CLIENT_ID, f"{CALLBACK_URL}:{PORT}/{CALLBACK}/", SCOPE)


def getUserToken(code):
    global TOKEN_DATA
    TOKEN_DATA = getToken(code, CLIENT_ID, CLIENT_SECRET,
                          f"{CALLBACK_URL}:{PORT}/{CALLBACK}/")


def refreshToken(tim):
    global TOKEN_DATA
    TOKEN_DATA = refreshAuth(CLIENT_ID, CLIENT_SECRET)
    refreshStat()
    time.sleep(tim)


def getAccessToken():
    return TOKEN_DATA


def refreshStat():
    counter = 0
    url = USER_RECENTLY_PLAYED_ENDPOINT
    params = {'limit': 50}
    headers = {"Authorization": f"Bearer {TOKEN_DATA[1]}"}
    resp = requests.get(url, params=params, headers=headers).json()['items']
    for track in resp:
        played_at = track['played_at']
        title = track['track']['name']
        artist = ", ".join([artist['name'] for artist in track['track']['artists']])
        url_track = track['track']['album']['images'][1]['url']
        with conn.connect() as connection:
            counter += 1
            connection.execute(
                'INSERT INTO spotify_stat (played_at, track, artist, url_track)'
                ' VALUES (%s, %s, %s, %s)'
                '  ON CONFLICT DO NOTHING',
                played_at, title, artist, url_track
            )
    app.logger.info(f"Updated {counter} records.")
