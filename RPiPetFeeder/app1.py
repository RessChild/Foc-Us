#!/usr/bin/env python
from flask import Flask, render_template, Response
from camera import Camera
from time import sleep
import cv2
app = Flask(__name__)

cam = Camera()
frame = None
flag = False

@app.after_request
def set_response_headers(r):
    r.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    r.headers['Pragma'] = 'no-cache'
    r.headers['Expires'] = '0'
    return r

@app.route('/')
def index():
    global flag
    flag = True
    return render_template('index.html')

def gen(camera):
    global flag
    while True:
       if flag:
           sleep(1)
           flag = False
       global frame
       frame = camera.get_frame()
       f = open('./static/img.jpg', 'wb')
       f.write(frame)
       f.close()

       yield (b'--frame\r\n'
              b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video_feed')
def video_feed():
   return Response(gen(cam),
                   mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/get')
def get_image():
    sleep(1)
    f = open('./static/img.jpg', 'wb')
    f.write(frame)
    f.close()
    return render_template("pic.html")

if __name__ == '__main__':
   app.run(host='0.0.0.0', debug=True, threaded=True, port=80)
