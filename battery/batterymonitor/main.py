#!/usr/bin/python
import RPi.GPIO as GPIO
import time
import array
import os
import signal
import subprocess
import math
from subprocess import check_output

from config import *
from mcp3008 import *

warning = 0
status = 0

def changeicon(percent):
    i = 0
    killid = 0
    os.system(PNGVIEWPATH + "/pngview -b 0 -l 3000" + percent + " -x 650 -y 5 " + ICONPATH + "/battery" + percent + ".png &")
    if DEBUGMSG == 1:
        print("Changed battery icon to " + percent + "%")
    out = check_output("ps aux | grep pngview | awk '{ print $2 }'", shell=True)
    nums = out.split('\n')
    for num in nums:
        i += 1
        if i == 1:
            killid = num
            os.system("sudo kill " + killid)		

def changeled(x):
    if LEDS == 1:
        if x == "green":
            GPIO.output(GOODVOLTPIN, GPIO.HIGH)
            GPIO.output(LOWVOLTPIN, GPIO.LOW)
        elif x == "red":
            GPIO.output(GOODVOLTPIN, GPIO.LOW)
            GPIO.output(LOWVOLTPIN, GPIO.HIGH)

def endProcess(signalnum = None, handler = None):
    GPIO.cleanup()
    os.system("sudo killall pngview");
    exit(0)

def initPins():
    GPIO.setup(GOODVOLTPIN, GPIO.OUT)
    GPIO.setup(LOWVOLTPIN, GPIO.OUT)
    GPIO.output(GOODVOLTPIN, GPIO.LOW)
    GPIO.output(LOWVOLTPIN, GPIO.LOW)

if DEBUGMSG == 1:
    print("Batteries 100% voltage:		" + str(VOLT100))
    print("Batteries 75% voltage:		" + str(VOLT75))
    print("Batteries 50% voltage:       	" + str(VOLT50))
    print("Batteries 25% voltage:       	" + str(VOLT25))
    print("Batteries dangerous voltage: 	" + str(VOLT0))
    print("ADC 100% value:      	 	" + str(ADC100))
    print("ADC 75% value:			" + str(ADC75))
    print("ADC 50% value:			" + str(ADC50))
    print("ADC 25% value:       		" + str(ADC25))
    print("ADC dangerous voltage value: 	" + str(ADC0))

# Prepare handlers for process exit
signal.signal(signal.SIGTERM, endProcess)
signal.signal(signal.SIGINT, endProcess)

if LEDS == 1:
    GPIO.setmode(GPIO.BOARD)
    initPins()

os.system(PNGVIEWPATH + "/pngview -b 0 -l 299999 -x 650 -y 5 " + ICONPATH + "/blank.png &")

while True:
    ret1 = readadc(ADCCHANNEL, SPICLK, SPIMOSI, SPIMISO, SPICS)
    time.sleep(3)
    ret2 = readadc(ADCCHANNEL, SPICLK, SPIMOSI, SPIMISO, SPICS)
    time.sleep(3)
    ret3 = readadc(ADCCHANNEL, SPICLK, SPIMOSI, SPIMISO, SPICS)
    ret = ret1 + ret2 + ret3
    ret = ret/3

    if DEBUGMSG == 1:
        print("ADC value: " + str(ret) + " (" + str(((HIGHRESVAL+LOWRESVAL)*ret*(ADCVREF/1024))/HIGHRESVAL) + " V)")
 
    if ret < ADC0:
        if status != 0:
            changeicon("0")
            changeled("red")
            if CLIPS == 1:
	        os.system("/usr/bin/omxplayer --no-osd --layer 999999  " + ICONPATH + "/lowbattshutdown.mp4 --alpha 160;sudo shutdown -h now")
        status = 0
    elif ret < ADC25:
        if status != 25:
            changeled("red")
            changeicon("25")
            if warning != 1:
		if CLIPS == 1:
                    os.system("/usr/bin/omxplayer --no-osd --layer 999999  " + ICONPATH + "/lowbattalert.mp4 --alpha 160")
                warning = 1
        status = 25
    elif ret < ADC50:
        if status != 50:
            changeled("green")
            changeicon("50")
        status = 50
    elif ret < ADC75:
        if status != 75:
            changeled("green")
            changeicon("75")
        status = 75
    else:
        if status != 100:
            changeled("green")
            changeicon("100")      
        status = 100

    time.sleep(REFRESH_RATE)
