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

warning = 0
status = 0

def changeicon(percent):
    i = 0
    killid = 0
    os.system(PNGVIEWPATH + "/pngview -b 0 -l 3000" + percent + " -x 400 -y 5 " + ICONPATH + "/battery" + percent + ".png &")
    if DEBUGMSG == 1:
        print("Changed battery icon to " + percent + "%")
    out = check_output("ps aux | grep pngview | awk '{ print $2 }'", shell=True)
    nums = out.split('\n')
    for num in nums:
        i += 1
        if i == 1:
            killid = num
            os.system("sudo kill " + killid)		


def endProcess(signalnum = None, handler = None):
    GPIO.cleanup()
    os.system("sudo killall pngview");
    exit(0)



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



os.system(PNGVIEWPATH + "/pngview -b 0 -l 299999 -x 400 -y 5 " + ICONPATH + "/blank.png &")

ret = 3800

while True:
    if ret < 3500:
        changeicon("0")
	os.system("/usr/bin/omxplayer --no-osd --layer 999999  " + ICONPATH + "/lowbattshutdown.mp4 --alpha 160;sudo shutdown -h now")
        status = 0
		
    elif ret < 3600:
        changeicon("25")
	if CLIPS == 1:
            os.system("/usr/bin/omxplayer --no-osd --layer 999999  " + ICONPATH + "/lowbattalert.mp4 --alpha 160")
    elif ret < 3900:
        if status != 50:
            changeicon("50")
        status = 50
    elif ret < 4000:
        changeicon("75")
        status = 75
    else:
        changeicon("100")      
        status = 100

    time.sleep(REFRESH_RATE)
