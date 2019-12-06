# -*- coding: utf-8 -*-
"""
Created on Sun Dec  1 16:46:10 2019

@author: wpqld_000
"""

from datetime import datetime
import time
import cv2 # opencv
import RPi.GPIO as GPIO
import picamera as cam
# 라즈베리 파이 카메라 import 

ledPIN = 20 # led 용 핀 추후 수정 가능
            # 모터 핀 바로 위에꺼
servoPIN = 21 # 21번 핀 사용 GND 옆
GPIO.setmode(GPIO.BCM) # BCM 으로 사용
GPIO.setup(servoPIN, GPIO.OUT) # 모터 조작용 정보핀
GPIO.setup(ledPIN, GPIO.OUT) # 타이머 대용으로 쓸거므로 out

p = GPIO.PWM(servoPIN, 50) # GPIO 17 als PWM mit 50Hz
GPIO.PWM(ledPIN, 100) # GPIO 17 als PWM mit 50Hz
# 이게 왜 50부터 시작인지는 좀 봐야할거같음
# LED 에선 PWM이 밝기값을 조절하는 용도
# servo 에서는 값 표현의 범위가 비례하며 값이 클수록 세세한 조절이 가능
# 참고로 50 기준 3.5~13 / 100 기준 7~26

# 정확히는 현재 각도의 값을 몇으로 잡을 것인가를 정의
p.start(0) # Initialisierung 초기화
angle = 12.5 # 모터가 사용할 기본
p.ChangeDutyCycle(angle) # 중심으로 모터를 옮김
# 이걸 기반으로 모터 각을 계산하고 이동여부를 판단

#우선 생각중인건 무한루프 돌리고,
# sleep(0.1)씩이라도 돌려서 조금씩 맞춰가는거

# 원래는 현재 기기가 가리키는 각도의 값을 반환받아 쓰고자 했는데
# 아두이노랑 다르게 라즈베리의 경우 이런 역할을 하는 함수가 존재하지 않는 듯
# 그저 외부에서 강제로 모터를 제어하는 함수만 지원하는걸로 보임

camera = cam.PiCamera() # 카메라 객체 만들고
camera.resolution = (800,600) # 사진 크기 결정

def ledTimer(loop): # 타이머 정의 함수, 1초를 주기로 깜빡거림
    for i in range(loop):
        GPIO.output(ledPIN,GPIO.HIGH)
        time.sleep(0.5)
        GPIO.output(ledPIN,GPIO.LOW)
        time.sleep(0.5)
# led 함수 확인완료

def servoControl(move): # 모터 컨트롤용 함수
    global angle
    # 들어온 정보를 기반으로 모터를 회전
    # 카메라 이동 구간
    angle = angle+move if angle+move < 25 else angle
    # 합이 25를 넘지않으면 더한값, 아니라면 원본 값 대입
    p.ChangeDutyCycle(angle)
    time.sleep(1)
    # 실제로 카메라를 움직이는 구간
    # 입출력 시간을 고려해서 몇번 테스트 해봐야할듯
# servo 함수 확인 완료
# 이제 수정해야됨
    
def finish():  #종료함수
    p.ChangeDutyCycle(0) # 각도를 초기화하고 종료
    p.stop()
    GPIO.cleanup()
#    cap.release()
#    cv2.destroyAllWindows()

def Foc_Us(): # 본체가 될 함수
    
    try:
        # OpenCV 호출 구간 
        # 오픈할 카메라정보를 넘겨줘야할거같은데    
        camera.capture("경로명 및 사진이름") # 라즈베리 카메라 캡쳐
    
        cap = cv2.VideoCapture(0) # 카메라 객체를 열어둠
        while cap.isOpend(): # 무한루프
            # 기본 카메라로 화면 데이터를 읽어옴   
            success, frame = cap.read() # 성공 여부 및 프레임
            if success:
            # 프레임 출력
            # cv2.imshow('Camera Window', frame)
    
            # 포지션을 잡고, 물체의 위치값을 반환받음
            # obj = ~~~
    
            # 조건문 구간
            # 모터의 회전 각을 수정하는 방식
            # 대략적인 수식은 아래처럼 될듯
           
            # 굳이 저렇게 작은값을 쓰는 이유는
            # 물리적인 데이터 입출력 적용속도가 있을거니까
            # 그래서 그냥 무한루프 돌리면서 계속 중심잡아가는게 편할거같음
            # 다만 문제점은 이거 인터럽트 걸어줘야하는데 그거 방식좀 찾아보고
            # 하여튼 현재 위치 값을 조건에 따라 다른 각 이동을 시키는 방식
            
                angle = 0 # 여기 추후에 수정 필요
            # 모션캡쳐로 위치값을 받아오고 그에 따라서 각조절이 좀 필요할듯
            
                while True: # 우선은 무한 반복
                    servoControl(angle)
            # 현재 각위치를 알아야 카메라를 돌리는 정도를 알 수 있기 때문에
            # 우선 객체로 구현을 할 것을 고민 중
        
        # 탐지 성공했다면 루프 빠져나올거고
        ledTimer(3) # 정해진 시간만큼 깜빡이고
        camera.capture("/foc_us/"+datetime.now()+".jpg") # 라즈베리 카메라 캡쳐
        
    except KeyboardInterrupt: # ctrl + c 
        finish()

# 이후 하게된다면 이쪽 구간에서 카메라 촬영 함수 호출할듯..?
# 사용자 UI 정보도 이쪽이고
# 고려사항
# 우선,라즈베리 카메라로 실시간 영상전송이 가능한가 여부
# 좀 힘들거같긴한데 이게 안되면 촬영을 매초 해서 전송하는방식응로 바꿔얒 뭐..
    
if __name__=="__main__": # 함수호출
#    ledTimer(5)
    servoControl(12.5)
    servoControl(12.5)
    servoControl(-12.5)
    servoControl(12.5)
    finish()
#    Foc_Us()
