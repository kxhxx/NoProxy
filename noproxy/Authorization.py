from flask import session, redirect
from pymongo import MongoClient
from noProxy.config import DB_STRING
import requests
from pip._vendor import cachecontrol
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
import google.auth.transport.requests

client = MongoClient(DB_STRING)
db = client.noProxy
users = db['users']

GOOGLE_CLIENT_ID = "595278317536-m9i9vije8plq9ge5k6729qvk93p3kmei.apps.googleusercontent.com"
client_secrets_file = "client_secret.json"


def get_token():
    request_session = requests.session()
    cached_session = cachecontrol.CacheControl(request_session)
    token_request = google.auth.transport.requests.Request(session=cached_session)
    return token_request


def login_user(token_request, credentials):
    id_info = id_token.verify_oauth2_token(
        id_token=credentials._id_token,
        request=token_request,
        audience=GOOGLE_CLIENT_ID,
        clock_skew_in_seconds=100
    )
    id_info = dict(id_info)

    id_info['_id'] = id_info.get('email')
    id_info['role'] = 'student'

    if not users.find_one({'_id':id_info.get('email')}):
        users.insert_one(id_info)
    session['user'] = id_info.get('email')
    session["google_id"] = id_info.get("sub")
    session["name"] = id_info.get("name")
    return redirect('/')