#!/bin/python
# Shuts system down when button is pressed. 
import RPi.GPIO as GPIO
import time
import os

# Use the Broadcom SOC Pin numbers
# Setup the Pin with Internal pullups enabled and PIN in reading mode.
GPIO.setmode(GPIO.BCM)
GPIO.setup(4, GPIO.IN, pull_up_down = GPIO.PUD_UP)

# Our function on what to do when the button is pressed
def Shutdown(channel):
	#Dim backlight before shutdown. Pulls BL pin low, allowing backlight to kill as soon as shutdown completes.
	GPIO.setup(19, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)
	#shutddown
    os.system("sudo shutdown -h now")

# Add our function to execute when the button pressed event happens
GPIO.add_event_detect(4, GPIO.FALLING, callback = Shutdown, bouncetime = 2000)

# Now wait!
while 1:
    time.sleep(1)












