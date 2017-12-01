import RPi.GPIO as GPIO
import time
import os
pwmPin = 19
dc = 1
GPIO.setmode(GPIO.BCM)
GPIO.setup(19, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(26, GPIO.IN, pull_up_down = GPIO.PUD_UP)

def BL(channel):
	global dc
	if dc == 1:
		dc = 0
		GPIO.setup(19, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)
	else:
		dc = 1
		GPIO.setup(19, GPIO.IN, pull_up_down = GPIO.PUD_UP)
#	print dc

GPIO.add_event_detect(26, GPIO.FALLING, callback = BL, bouncetime = 1000)

try:
	while 1:
		time.sleep(1)

except KeyboardInterrupt:
	GPIO.cleanup()
