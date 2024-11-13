import qrcode
import pyzbar
import png
from pymongo import MongoClient
from datetime import date
import pyimgur
import os
from flask import session
from noProxy.config import DB_STRING

client = MongoClient(DB_STRING)
db = client.noProxy
users = db['users']
attendance_collection = db['attendance']
ongoing_attendance_collection = db['ongoing_attendance']


def generate_qr_codes(uid, valid_ids):
    os.mkdir(f'{uid}')
    image_links = []
    for _id in valid_ids: 
        data = {"_id":uid, 'valid_id':_id}
        qr = qrcode.make(data)
        qr.save(f"{uid}/{_id}.png")
        imgur = pyimgur.Imgur('e3177ad6b500c76')
        image = imgur.upload_image(f'{uid}/{_id}.png', title=_id)
        os.remove(f'{uid}/{_id}.png')
        image_links.append(image.link)
    ongoing_attendance_collection.update_one({'_id':uid},{'$set':{'image_links':image_links}})
    return image_links

