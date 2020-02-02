#!/usr/bin/env python

import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BOARD)
GPIO.setup(37, GPIO.OUT) #ROT
GPIO.setup(36, GPIO.OUT) #GRUEN
GPIO.setup(40, GPIO.OUT) #BLAU


#GPIO.output(37, 1)
#time.sleep(5)
#GPIO.output(37, 0)

p = GPIO.PWM(37, 120)
pp = GPIO.PWM(36, 120)
ppp = GPIO.PWM(40, 120)
# frequency=100Hz
p.start(0)
pp.start(0)
ppp.start(0)

zaehler_blau = 0
zaehler_gruen = 0

while 1:
    p.ChangeDutyCycle(0)
    pp.ChangeDutyCycle(0)  
    ppp.ChangeDutyCycle(0)

    for dc in range(1, 80, 1):
        p.ChangeDutyCycle(dc)
        if dc % 4 == 0:
            zaehler_gruen += 1
            pp.ChangeDutyCycle(zaehler_gruen)
        if dc % 8 == 0:
            zaehler_blau += 1
            ppp.ChangeDutyCycle(zaehler_blau)
            if zaehler_blau == 2:
                print(zaehler_blau)
                break

        time.sleep(0.05)
    print("Rot fertig")

    for dc in range(zaehler_gruen, 80, 1):
        pp.ChangeDutyCycle(dc)
        if dc % 2 == 0:
            zaehler_blau += 1
            ppp.ChangeDutyCycle(zaehler_blau)
        time.sleep(0.05)
    print("Grün fertig")

    for dc in range(zaehler_blau, 80, 1):
        ppp.ChangeDutyCycle(dc)
        time.sleep(0.05)
    print("Blau fertig")
    
    zaehler_blau = 0
    zaehler_gruen = 0
    dc = 0
    
    null_ja_oder_nein = input("Input als Pause: ")
