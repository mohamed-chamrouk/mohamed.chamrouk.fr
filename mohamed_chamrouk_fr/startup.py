from mohamed_chamrouk_fr.flask_spotify_auth import getAuth, refreshAuth, getToken
from mohamed_chamrouk_fr import app
import time

#Add your client ID
CLIENT_ID = app.config['CLIENT_ID']

#aDD YOUR CLIENT SECRET FROM SPOTIFY
CLIENT_SECRET = app.config['CLIENT_SECRET']

#Port and callback url can be changed or ledt to localhost:5000
PORT = "5000"
CALLBACK_URL = "http://127.0.0.1"
CALLBACK = "projects/spotify"

#Add needed scope from spotify user
SCOPE = "streaming user-read-email user-read-private"
#token_data will hold authentication header with access code, the allowed scopes, and the refresh countdown
TOKEN_DATA = []


def getUser():
    return getAuth(CLIENT_ID, f"{CALLBACK_URL}:{PORT}/{CALLBACK}/", SCOPE)


def getUserToken(code):
    global TOKEN_DATA
    TOKEN_DATA = getToken(code, CLIENT_ID, CLIENT_SECRET,
                          f"{CALLBACK_URL}:{PORT}/{CALLBACK}/")


def refreshToken(tim):
    time.sleep(tim)
    global TOKEN_DATA
    TOKEN_DATA = refreshAuth(CLIENT_ID, CLIENT_SECRET)


def getAccessToken():
    return TOKEN_DATA
