# -*- coding: utf-8 -*-
"""
Created on Sun Dec  1 16:46:10 2019

@author: wpqld_000
"""

import time
import cv2 as cv # opencv
import RPi.GPIO as GPIO

ledPIN = 20 # led 용 핀 추후 수정 가능
            # 모터 핀 바로 위에꺼
servoPIN = 21 # 21번 핀 사용 GND 옆
GPIO.setmode(GPIO.BCM)
GPIO.setup(servoPIN, GPIO.OUT)
GPIO.setup(ledPIN, GPIO.OUT) # 타이머 대용으로 쓸거므로 out
GPIO.Input()

p = GPIO.PWM(servoPIN, 50) # GPIO 17 als PWM mit 50Hz
l = GPIO.PWM(ledPIN, 50)
# 이게 왜 50부터 시작인지는 좀 봐야할거같

"""
GPIO.output(ledPIN,GPIO.HIGH)
GPIO.output(ledPIN,GPIO.LOW)
time.sleep(0.1)
"""

p.start(2.5) # Initialisierung 초기화
# 정확히는 현재 각도의 값을 몇으로 잡을 것인가를 정의

#우선 생각중인건 무한루프 돌리고,
# sleep(0.1)씩이라도 돌려서 조금씩 맞춰가는거

val = 1; # 우선 현재 각도를 좀 파악할 필요가 있음..
# 받을 수 있으면 받아쓰는 함수를 쓰고
# 아니라면 그냥 제일 처음각도로 강제이동시키고 써야할듯


# ESC를 누르면 종료
#        key = cv2.waitKey(1) & 0xFF
#        if (key == 27): 
#            break

try:
    # OpenCV 호출 구간 
    cap = cv2.VideoCapture(0) # 카메라 객체를 열어둠
    while cap.isOpend(): # 무한루프
        # 기본 카메라로 화면 데이터를 읽어옴   
        success, frame = cap.read() # 성공 여부 및 프레임
        if success:
        # 프레임 출력
#            cv2.imshow('Camera Window', frame)

        # 포지션을 잡고, 물체의 위치값을 반환받음
        # obj = ~~~

        # 조건문 구간
        # 모터의 회전 각을 수정하는 방식
        # 대략적인 수식은 아래처럼 될듯
        """
        if obj < 중심값:
            val = val + 1
        elif obj > 중심값:
            val = val - 1
        else obj == 중심값:
            ~~ (아마 break 구문이 들어갈듯)
        """
        # 굳이 저렇게 작은값을 쓰는 이유는
        # 물리적인 데이터 입출력 적용속도가 있을거니까
        # 그래서 그냥 무한루프 돌리면서 계속 중심잡아가는게 편할거같음
        # 다만 문제점은 이거 인터럽트 걸어줘야하는데 그거 방식좀 찾아보고
        # 하여튼 현재 위치 값을 조건에 따라 다른 각 이동을 시키는 방식

        # 카메라 이동 구간       
        p.ChangeDutyCycle(val) 
        time.sleep(0.2)
        # 실제로 카메라를 움직이는 구간
        # 입출력 시간을 고려해서 몇번 테스트 해봐야할듯

except KeyboardInterrupt: # ctrl + c 
    p.stop()
    GPIO.cleanup()
    cap.release()
    cv2.destroyAllWindows()


# 이후 하게된다면 이쪽 구간에서 카메라 촬영 함수 호출할듯..?
# 사용자 UI 정보도 이쪽이고
# 고려사항
# 우선,라즈베리 카메라로 실시간 영상전송이 가능한가 여부
# 좀 힘들거같긴한데 이게 안되면 촬영을 매초 해서 전송하는방식응로 바꿔얒 뭐..