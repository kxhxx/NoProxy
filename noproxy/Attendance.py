from flask import session, redirect
from flask_socketio import SocketIO, emit
from pymongo import MongoClient
import uuid
from datetime import datetime
import pytz
import random
import string
from noProxy.config import DB_STRING
from noProxy.qr import *
from noProxy.scanner import *

from app import socketio

client = MongoClient(DB_STRING)
db = client.noProxy
users = db['users']
ongoing_attendance_collection = db['ongoing_attendance']
attendance_collection = db['attendance']

UTC = pytz.utc
IST = pytz.timezone('Asia/Kolkata')

def start_session(course_name, course_code, class_strength):
    while True:
        # uid = uuid.uuid1()
        uid = ''.join(random.choices(string.ascii_uppercase + string.digits, k = 10))    
        if not ongoing_attendance_collection.find_one({'_id':uid}):
            break
    valid_ids = []
    while len(valid_ids) != int(class_strength):
        random_id = random.randint(100000,999999)
        if random_id not in valid_ids:
            valid_ids.append(random_id)
    datetime_ist = datetime.datetime.now(IST)
    ongoing_attendance_collection.insert_one({
        '_id':uid,
        'course_name':course_name,
        'course_code':course_code,
        'started_by':session['user'],
        'start_time':  datetime_ist.strftime('%d/%m/%Y %H:%M:%S %Z'),
        'valid_ids':valid_ids,
        'used_ids':[],
        'marked_students':[],
        'used_images':[]
    })
    session['ongoing_attendance'] = uid
    generate_qr_codes(uid, valid_ids)
    return uid


def mark_attendance(data):
    data = eval(data)
    uid = data['_id']
    attendance_id = data['valid_id']
    ongoing_session_data = ongoing_attendance_collection.find_one({'_id':uid})
    if attendance_id in ongoing_session_data['valid_ids'] and attendance_id not in ongoing_session_data['used_ids'] and session['user'] not in ongoing_session_data['marked_students']:
        used_ids = ongoing_session_data['used_ids']
        used_ids.append(attendance_id)
        marked_students = ongoing_session_data['marked_students']
        marked_students.append(session['user'])
        used_images = ongoing_session_data['used_images']
        index = ongoing_session_data['valid_ids'].index(attendance_id)
        print(ongoing_session_data['image_links'][index])
        used_images.append(ongoing_session_data['image_links'][index])
        ongoing_attendance_collection.update_one({'_id':uid}, {'$set':{'used_ids':used_ids, 'marked_students':marked_students, 'used_images':used_images}})
    else:
        return 'Invalid or already marked'
    socketio.emit('listener', {'_id':uid,'used_id':attendance_id}, namespace='/listener')
    return 'Attendance marked'

def get_qr_images(uid):
    image_links = []
    used_images = ongoing_attendance_collection.find_one({'_id':uid})['used_images']
    all_links = ongoing_attendance_collection.find_one({'_id':uid})['image_links']
    for link in all_links:
        if link not in used_images:
            image_links.append(link)
    return image_links

    


