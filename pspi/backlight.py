import RPi.GPIO as GPIO 
import time 
import os  
duty = 350

GPIO.setmode(GPIO.BCM)
#GPIO.setup(19, GPIO.IN, pull_up_down = GPIO.PUD_UP)

GPIO.setup(26, GPIO.IN, pull_up_down = GPIO.PUD_UP)

#GPIO.setup(19, GPIO.OUT)

#pwm = GPIO.PWM(19, 100)
#pwm.start(100)

time.sleep(5)
os.system("gpio -g mode 19 pwm")
os.system("gpio -g pwm 19 350")

def BL(channel):
	global duty
	duty = duty - 75
	if duty < 200:
		duty = 500
	os.system("gpio -g pwm 19 %s" % (duty-1))
#	global duty
#	duty = duty - 10
#	if duty == 10:
#		duty = 50
#	pwm.ChangeDutyCycle(duty)
#	print duty

GPIO.add_event_detect(26, GPIO.FALLING, callback = BL, bouncetime = 1000)

try:
	while 1:
		time.sleep(1)

except KeyboardInterrupt:
	GPIO.cleanup()
