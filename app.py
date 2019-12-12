#!/usr/bin/env python
from flask import Flask, render_template, Response
from camera import Camera
from time import sleep
import cv2
import variable_resistor as vr

app = Flask(__name__)

frame = None # jpeg 형식의 byte단위 파일 저장
flag = False # 촬영한 이미지 불러오는 타이밍과 이미지 저장 타이밍을 겹치지 않게 하기 위해 설정

cam = Camera() # 카메라 객체 초기화

manual = ['왼쪽은 스트리밍 화면, 오른쪽은 촬영 결과 화면입니다', '촬영 버튼을 누르면 가변저항값에 맞추어 0~7초 사이의 타이머가 설정됩니다', 'LED를 통해 촬영 타이밍을 볼 수 있으며, 촬영 버튼 클릭 시 불이 들어오고, 촬영 시작 1초간 불이 꺼집니다'] # 템플릿에 들어갈 메뉴얼

@app.after_request
def set_response_headers(r): 
    # 웹상에서 캐시 데이터 유지로 인해 촬영 완료된 이미지 갱신이 안되는 문제 수정
    r.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    r.headers['Pragma'] = 'no-cache'
    r.headers['Expires'] = '0'
    return r

@app.route('/')
def index():
    global flag
    t = int(vr.main()) # 가변 저항값 0~7사이의 값으로 받아옴
    if vr.adc_value != -1: # 가변 저항값이 제대로 들어왔는지 확인
        cam.ledon() # 값 잘 들어왔으면 led 키고
        sleep(t-1) # 가변 저항 시간 -1 만큼 led 키고있다가
        cam.ledoff() # led 종료
        sleep(1) # 나머지 1초
    flag = True # 하단 코드에서 이미지 입력 수행
    sleep(0.5) # 이미지 저장될 때까지 대기(높을수록 안전)
    return render_template('index.html',
            timer='촬영 타이머 : '+str(t)+'초',
            manual=manual
            ) # 템플릿에 보낼 값들과 부를 템플릿 지정

def gen(camera): # 스레드 형태로 구동
    global flag
    global frame
    while True:
        frame = camera.get_frame() # jpeg byte 단위로 한 프레임 사진 불러옴
        f = open('./static/img.jpg', 'wb') # 파일 저장할 위치 열고
        f.write(frame) # 파일 입력
        f.close() # file stream  종료
        if flag: # 파일을 불러와야될 상황이라면
            sleep(1) # 타이머 걸고
            flag = False # 다시 flag값 원상복귀시킴

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n') # 서버로부터 클라이언트에 스트리밍 전송 

@app.route('/video_feed') # 스트리밍 페이지
def video_feed():
   return Response(gen(cam),
           mimetype='multipart/x-mixed-replace; boundary=frame') # 응답 객체(컨텐츠 : frame)

@app.route('/get') # 이미지 한장 찍어서 볼 수 있는 링크
def get_image():
    sleep(1)
    f = open('./static/img.jpg', 'wb')
    f.write(frame)
    f.close()
    return render_template("pic.html")

if __name__ == '__main__':
   app.run(host='0.0.0.0', debug=True, threaded=True, port=80) # 쓰레드, 포트 설정
