import RPi.GPIO as GPIO 
import time 
import os  
duty = 90

GPIO.setmode(GPIO.BCM)
#GPIO.setup(19, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setwarnings(False)
GPIO.setup(26, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(4, GPIO.IN, pull_up_down = GPIO.PUD_UP)
os.system("sudo pigpiod")
time.sleep(1)
os.system("sudo pigs p 19 90")
def BL(channel):
	global duty
	duty = duty - 10
	if duty < 60:
		duty = 120
	os.system("sudo pigs p 19 %s" % duty)

def Shutdown(channel):
	# Dim backlight before shutdown
	# Pulls BL pin low, allowing backlight to kill as soon as shutdown completes
	os.system("sudo killall pigpiod")
	GPIO.setup(19, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)
	# Issue shutddown command
	os.system("sudo shutdown -h now")

GPIO.add_event_detect(26, GPIO.FALLING, callback = BL, bouncetime = 200)
GPIO.add_event_detect(4, GPIO.FALLING, callback = Shutdown, bouncetime = 200)


try:
	while 1:
		time.sleep(1)

except KeyboardInterrupt:
	GPIO.cleanup()
