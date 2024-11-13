import cv2
import numpy as np
from pyzbar.pyzbar import decode
from pymongo import MongoClient
import json
import asyncio
import datetime
import ssl
from flask import session

from noProxy.attendance import *
from noProxy.config import DB_STRING


client = MongoClient('mongodb+srv://doadmin:73ITEo985v61j2cg@bablucopter-b5efd098.mongo.ondigitalocean.com/admin?tls=true&authSource=admin')
db = client.noproxy
users = db['users']

time_difference = lambda a: datetime.timedelta.total_seconds(a)/60

def decoder(image):
    gray_img = cv2.cvtColor(image,0)
    barcode = decode(gray_img)
    for obj in barcode:
        points = obj.polygon
        (x,y,w,h) = obj.rect
        pts = np.array(points, np.int32)
        pts = pts.reshape((-1, 1, 2))

        barcodeData = obj.data.decode("utf-8")
        barcodeType = obj.type

        # if barcodeData:
        #     cv2.polylines(image, [pts], True, (0, 0, 255), 5)
        #     cv2.putText(frame, barcodeData, (x,y), cv2.FONT_HERSHEY_SIMPLEX,0.8,(0,0,255), 2)
        #     return True
        # else:   
        #     cv2.polylines(image, [pts], True, (0, 255, 0), 3)
        #     cv2.putText(frame, 'invalid', (x,y), cv2.FONT_HERSHEY_SIMPLEX,0.8,(0,255,0), 2)
        #     return False
        if barcodeData:
            return barcodeData
        else:
            return None

def scan_attendance():
    cap = cv2.VideoCapture(0)
    while True:
        ret, frame = cap.read()
        data = decoder(frame)
        if data:
            cv2.destroyAllWindows()
            return mark_attendance(data)
            break
        cv2.imshow('Image', frame)
        code = cv2.waitKey(10)
        if code == ord('q'):
            cv2.destroyAllWindows()
            break