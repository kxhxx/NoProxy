from flask import session, redirect, render_template
from functools import wraps
from pymongo import MongoClient
from noProxy.config import DB_STRING

client = MongoClient(DB_STRING)
db = client.noProxy
users = db['users']


def login_required(function):
    @wraps(function)
    def constraint(**kwargs):
        try:
            if session['user']:
                return function(**kwargs)
            else:
                return redirect('/login')
        except KeyError:
            return redirect('/login')
    return constraint


def admin_required(function):
    @wraps(function)
    def constraint(**kwargs):
        if users.find_one({'_id':session['user']})['role'] == 'admin':
            return function(**kwargs)
        else:
            return render_template('notification.html', message='Unauthorized')
    return constraint