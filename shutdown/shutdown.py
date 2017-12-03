#!/bin/python
# Shuts system down when button is pressed.
# https://www.othermod.com 
import RPi.GPIO as GPIO
import time
import os

# Set up GPIO pin
GPIO.setmode(GPIO.BCM)
GPIO.setup(4, GPIO.IN, pull_up_down = GPIO.PUD_UP)

def Shutdown(channel):
	#Dim backlight before shutdown
	#Pulls BL pin low, allowing backlight to kill as soon as shutdown completes
	GPIO.setup(19, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)
	#Issue shutddown command
	os.system("sudo shutdown -h now")

# Interrupt looking for pin voltage to drop
GPIO.add_event_detect(4, GPIO.FALLING, callback = Shutdown, bouncetime = 2000)

while 1:
	time.sleep(1)












