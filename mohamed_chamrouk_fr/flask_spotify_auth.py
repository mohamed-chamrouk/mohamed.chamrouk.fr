import base64
import json
import requests
from mohamed_chamrouk_fr import app

SPOTIFY_URL_AUTH = 'https://accounts.spotify.com/authorize/?'
SPOTIFY_URL_TOKEN = 'https://accounts.spotify.com/api/token/'
RESPONSE_TYPE = 'code'
HEADER = 'application/x-www-form-urlencoded'
REFRESH_TOKEN = ''


def getAuth(client_id, redirect_uri, scope):
    data = "{}client_id={}&response_type=code&redirect_uri={}&scope={}"\
            .format(SPOTIFY_URL_AUTH, client_id, redirect_uri, scope)
    return data


def getToken(code, client_id, client_secret, redirect_uri):
    body = {
        "grant_type": 'authorization_code',
        "code": code,
        "redirect_uri": redirect_uri
    }
    encoded = base64_encode(client_id, client_secret)
    headers = {"Content-Type": HEADER, "Authorization": f"Basic {encoded}"}
    post = requests.post(SPOTIFY_URL_TOKEN, headers=headers, data=body)
    return handleToken(json.loads(post.text))


def handleToken(response):
    auth_head = {"Authorization": f"Bearer {response.get('access_token')}"}
    global REFRESH_TOKEN
    current_refresh = response.get("refresh_token")
    REFRESH_TOKEN = REFRESH_TOKEN if current_refresh is None else current_refresh
    app.logger.info(f"expires in : {response.get('expires_in')} with refresh token : {REFRESH_TOKEN}")
    return [response.get("access_token"), auth_head, response.get('scope'),
            response.get('expires_in')]


def refreshAuth(client_id, client_secret):
    global REFRESH_TOKEN
    body = {
        "grant_type": "refresh_token",
        "refresh_token": REFRESH_TOKEN
    }
    global HEADER
    encoded = base64_encode(client_id, client_secret)
    headers = {"Content-Type": HEADER, "Authorization": f"Basic {encoded}"}
    post_refresh = requests.post(SPOTIFY_URL_TOKEN, data=body, headers=headers)
    # p_back = json.dumps(post_refresh.text)
    return handleToken(json.loads(post_refresh.text))


def base64_encode(client_id, client_secret):
    encodedData = base64.b64encode(bytes(f"{client_id}:{client_secret}", "ISO-8859-1")).decode("ascii")
    authorization_header_string = f"{encodedData}"
    return(authorization_header_string)
