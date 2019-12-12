# -*- coding: utf-8 -*-
"""
Created on Mon Dec  9 02:16:52 2019

@author: wpqld_000
"""

# 아무래도 이건 그냥 가져다 써야할거같다
# 너무 세부적인 코드도 많고 보기 힘들고..

import threading
import RPi.GPIO as GPIO
import time

adc_value = -1
SPICLK = 11
SPIMISO = 9
SPIMOSI = 10
SPICS = 8 # 가변저항 사용용 변수
#LED = 18 # LED 핀

photo_ch = 0

def init():
    GPIO.setwarnings(False)
    GPIO.cleanup()
    GPIO.setmode(GPIO.BCM) # 세팅
    GPIO.setup(SPIMOSI, GPIO.OUT)
    GPIO.setup(SPIMISO, GPIO.IN)
    GPIO.setup(SPICLK, GPIO.OUT)
    GPIO.setup(SPICS, GPIO.OUT)
#    GPIO.setup(LED, GPIO.OUT) # 가변저항용 출력 4개와 LED 하나

def readadc(adcnum, clockpin, mosipin, misopin, cspin): # 가변저항 세팅 코드
    if ((adcnum > 7) or (adcnum < 0)):
        return -1
    GPIO.output(cspin, True)	
    GPIO.output(clockpin, False)  
    GPIO.output(cspin, False) # 출력값을 세팅했는데..

    commandout = adcnum
    commandout |= 0x18  
    commandout <<= 3    
    for i in range(5):
        if (commandout & 0x80):
            GPIO.output(mosipin, True)
        else:
            GPIO.output(mosipin, False)
        commandout <<= 1
        GPIO.output(clockpin, True)
        GPIO.output(clockpin, False)
    
    adcout = 0
    for i in range(12):
        GPIO.output(clockpin, True)
        GPIO.output(clockpin, False)
        adcout <<= 1
        
        if (GPIO.input(misopin)):
            adcout |= 0x1
            
    GPIO.output(cspin, True)
    adcout >>= 1
    return adcout

def timerValue():
    init()
    return readadc(photo_ch, SPICLK, SPIMOSI, SPIMISO, SPICS)/145 + 1 # 가변저항 값    

def main():
    global adc_value
    adc_value=readadc(photo_ch, SPICLK, SPIMOSI, SPIMISO, SPICS)/145 + 1 # 가변저항 값
    return adc_value


#if __name__ == '__main__':
#    try:
#        main() # 시작
#    except KeyboardInterrupt:
#        GPIO.cleanup() # 종료

init()
