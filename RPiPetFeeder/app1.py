#!/usr/bin/env python
from flask import Flask, render_template, Response
import picamera
from camera import Camera
from time import sleep
app = Flask(__name__)

cam = Camera()

@app.route('/')
def index():
   return render_template('index.html')

def gen(camera):
   while True:
       frame = camera.get_frame()
       print(frame)
       yield (b'--frame\r\n'
              b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video_feed')
def video_feed():
   return Response(gen(cam),
                   mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/get')
def get_image():
    return render_template("index.html")

if __name__ == '__main__':
   app.run(host='0.0.0.0', debug=True, threaded=True)
