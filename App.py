from flask import Flask, session, abort, redirect, request, render_template, flash, jsonify
from flask_socketio import SocketIO, emit
from pymongo import MongoClient
from noProxy.config import DB_STRING
import os
from random import random
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
import google.auth.transport.requests

import gunicorn
import eventlet

from noProxy.authorization import *
from noProxy.scanner import *
from noProxy.attendance import *
from noProxy.restrictions import *

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

app = Flask(__name__)
app.secret_key = "bablucopter"
socketio = SocketIO(app)

flow = Flow.from_client_secrets_file(
    client_secrets_file=client_secrets_file,
    scopes=["https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email", "openid"],
    redirect_uri="http://127.0.0.1:5000/callback"
    # redirect_uri = 'https://e338-223-185-7-171.ngrok.io/callback'
)


@app.route("/")
def index():
    return render_template('index.html', session=session, login=True if session.get('user') else False)


@app.route("/login")
def login():
    authorization_url, state = flow.authorization_url()
    session["state"] = state
    return redirect(authorization_url)


@app.route("/callback")
def callback():
    flow.fetch_token(authorization_response=request.url)
    try:
        if not session["state"] == request.args["state"]:
            pass
            # return render_template('notification.html', message='Error') # State does not match!
        credentials = flow.credentials
    except KeyError:
        credentials = flow.credentials
    return login_user(get_token(), credentials)


@app.route("/logout")
@login_required
def logout():
    session.clear()
    return redirect("/")


@app.route('/mark')
@login_required
def mark():
    message = scan_attendance()
    return render_template('notification.html', message=message)

@app.route("/admin")
@login_required
@admin_required
def admin():
    return render_template('admin.html', session=session, login=True if session.get('user') else False)

@app.route("/admin/attendance/start", methods=['GET','POST'])
@login_required
@admin_required
def start_attendance_session():
    dataGet = request.get_json(force=True)
    attendance_id = start_session(dataGet['course_name'], dataGet['course_code'], dataGet['class_strength'])
    return jsonify({'status':True, 'uid':attendance_id}) 

@app.route('/admin/attendance/<uid>')
def show_qr_attendance(uid):
    image_links = get_qr_images(uid)
    if image_links != []:
        image = random.choice(image_links)
    else:
        image = None
    return render_template('qr_display.html', image_link=image if image is not None else None, session=session, login=True if session.get('user') else False)


@socketio.on('listener', namespace='/listener')
def listener():
    pass



if __name__ == "__main__":
    # app.run(debug=True)
    eventlet.wsgi.server(eventlet.listen(('', 5000)), app, log_output=True, debug=True)
