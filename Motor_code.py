# -*- coding: utf-8 -*-
"""
Created on Sun Dec  1 16:46:10 2019

@author: wpqld_000
"""

from __future__ import print_function

from datetime import datetime
import time
import cv2 # opencv
import RPi.GPIO as GPIO
import picamera as cam

from imutils.object_detection import non_max_suppression
from imutils import paths
from imutils.video import VideoStream
import numpy as np
import argparse
import imutils
# 라즈베리 파이 카메라 import 

import variable_resistor as vr

ledPIN = 20 # led 용 핀 추후 수정 가능
            # 모터 핀 바로 위에꺼
servoPIN = 21 # 21번 핀 사용 GND 옆
GPIO.setmode(GPIO.BCM) # BCM 으로 사용
GPIO.setup(servoPIN, GPIO.OUT) # 모터 조작용 정보핀
GPIO.setup(ledPIN, GPIO.OUT) # 타이머 대용으로 쓸거므로 out

p = GPIO.PWM(servoPIN, 100) # GPIO 17 als PWM mit 50Hz
GPIO.PWM(ledPIN, 100) # GPIO 17 als PWM mit 50Hz
# 이게 왜 50부터 시작인지는 좀 봐야할거같음
# LED 에선 PWM이 밝기값을 조절하는 용도
# servo 에서는 값 표현의 범위가 비례하며 값이 클수록 세세한 조절이 가능
# 참고로 50 기준 3.5~13 / 100 기준 7~26
# 최소치는 3 정도로 보면될듯함 (3~17)

# 정확히는 현재 각도의 값을 몇으로 잡을 것인가를 정의
p.start(0) # Initialisierung 초기화
angle = 10 # 모터가 사용할 기본 (3~17 중간값)
p.ChangeDutyCycle(angle) # 중심으로 모터를 옮김
time.sleep(2)
# 이걸 기반으로 모터 각을 계산하고 이동여부를 판단

# 원래는 현재 기기가 가리키는 각도의 값을 반환받아 쓰고자 했는데
# 아두이노랑 다르게 라즈베리의 경우 이런 역할을 하는 함수가 존재하지 않는 듯
# 그저 외부에서 강제로 모터를 제어하는 함수만 지원하는걸로 보임

#camera = cam.PiCamera() # 카메라 객체 만들고
#camera.resolution = (800,600) # 사진 크기 결정

cap = cv2.VideoCapture(0) # cv 의 카메라캡쳐 객체
hog = cv2.HOGDescriptor()
hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())
# hog 는 대상탐색 지원 라이브러리
# 다수의 인원을 탐색 할 수 있도록 세팅
#vs = None # finish 에서 써야하니까 전역으로 빼내어 선언함
vs = VideoStream(usePiCamera=True).start()


def objDetect():
    #vs = VideoStream(usePiCamera=True).start()
    #파이 카메라를 통해 화면을 받아오도록 하고, 촬영 시작
    time.sleep(2.0) #실행 대기시간
    print("Stream Started!")
    
    while True: # 무한 루프
    # grab the raw NumPy array representing the image, then initialize the timestamp
    # and occupied/unoccupied text
        frame = vs.read() # 파이카메라에서 이미지를 한장 가져옴
        frame = imutils.resize(frame, width=400) # 사진 크기 변환
    
     	# detect people in the image
        print(type(frame))
        (rects, weights) = hog.detectMultiScale(frame, winStride=(4, 4), padding=(8, 8), scale=1.05)
        # 탐색해서 대상이 있다고 예상되는 사각형을 갖고 옴
    
        if len(rects) > 0: # 탐색한 놈이 1개 이상 있다면
            for (x, y , w, h) in rects: # 각 경우에 대해서
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 0, 255), 2) # 사각형을 그림
                 
            # 각 사각형 정보를 사용하기 위해 배열로 변환
            rects = np.array([[x, y, x + w, y + h] for (x, y, w, h) in rects])
            #non_max_suppression(frame, probs=None, overlapThresh=0.65)
            (x1, y1, w1, h1) = rects.astype("int")[0]
            # 반환되는 값은 2차원 배열값이므로, 인덱스 접근을 통해 1차원 값을 접근
            

            # draw the final bounding boxes
            cv2.rectangle(frame, (x1, y1), (x1 + w1, y1 + h1), (0, 255, 0),2)
            # 최종탐색
            
            if x1 + (w1//2) > 205: # 피사체 중심이 오른쪽으로 쏠린 경우
                print("왼쪽이동")
                succ = True if servoControl(1) else False # 그 반대방향으로 이동
                if not succ:
                    break # 초점을 맞추기 위해 더이상 움직일 수 없다면, 종료
            elif x1 + (w1//2) < 195: #
                print("오른쪽이동")
                succ = True if servoControl(-1) else False
                if not succ:
                    break # 마찬가지
            else: # 그 외의 경우는 초점 잡기 완료
                print("초점 잡혔음")
                return True # 성공적으로 끝
            
        cv2.imshow("Frame", frame)

                    # 이부분 수정 필요 
            # 지금은 단일탐색 기준으로 코드를 짰는데 이건 다중탐색으로 진행되므로
            # 평균값을 구해서 그 중심으로 이동시키는 코드로 변환이 필요
            # 중심값에서의 약간의 오차를 허용

    
        key = cv2.waitKey(1) & 0xFF # 입력된 키가 있고, q라면 종료
        if key == ord("q"):
            break
    return False # 실패. 더이상 진행 불가


def ledTimer(loop): # 타이머 정의 함수, 1초를 주기로 깜빡거림
    for i in range(loop):
        GPIO.output(ledPIN,GPIO.HIGH)
        time.sleep(0.5)
        GPIO.output(ledPIN,GPIO.LOW)
        time.sleep(0.5)
# led 함수 확인완료

def servoControl(move): # 모터 컨트롤용 함수
    global angle
    global p
    # 들어온 정보를 기반으로 모터를 회전
    # 카메라 이동 구간
    canMove = True if angle+move < 17 and angle+move > 3 else False
    angle = angle+move if canMove else angle
    # 3~17 사이값이면 움직일수있으니 True, 그 외엔 이동불가
    # 움직일수있다면 움직이고 아니면 고정

    p.ChangeDutyCycle(angle)
    print(angle)
    time.sleep(0.7)
    # 실제로 카메라를 움직이는 구간
    # 입출력 시간을 고려해서 몇번 테스트 해봐야할듯
    
    return canMove # 움직이기 성공 여부 판단
# servo 함수 확인 완료
# 이제 수정해야됨
    
def finish():  #종료함수
    global p
    p.ChangeDutyCycle(3) # 각도를 초기화하고 종료
    time.sleep(1)
    p.stop()
    GPIO.cleanup()
    
    cv2.destroyAllWindow() #cv 사용 종료
    vs.stop() # 정지

#    cap.release()
#    cv2.destroyAllWindows()

def Foc_Us(): # 본체가 될 함수
    
    try:
        succ = objDetect() #물체 탐지 시작
        # 성공여부를 반환받음
        if succ: # 성공이라면 타이머 입력 대기로 넘어감
            loop = vs.timerValue()
            ledTimer(loop)
        else:
            print("초점 실패, 진행 불가합니다")

#        ledTimer(3) # 정해진 시간만큼 깜빡이고
#        camera.capture("/foc_us/"+datetime.now()+".jpg") # 라즈베리 카메라 캡쳐
        
    except KeyboardInterrupt: # ctrl + c 
        print("Keyboard Interrupt")
    finally:
        finish()

# 이후 하게된다면 이쪽 구간에서 카메라 촬영 함수 호출할듯..?
# 사용자 UI 정보도 이쪽이고
# 고려사항
# 우선,라즈베리 카메라로 실시간 영상전송이 가능한가 여부
# 좀 힘들거같긴한데 이게 안되면 촬영을 매초 해서 전송하는방식응로 바꿔얒 뭐..
    
if __name__=="__main__": # 함수호출
#    ledTimer(5)
#    for i in range(20):
#        servoControl(1)
#    finish()
    Foc_Us()
