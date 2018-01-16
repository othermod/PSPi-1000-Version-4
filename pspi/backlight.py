import RPi.GPIO as GPIO 
import time 
import os  
duty = 90

GPIO.setmode(GPIO.BCM)
#GPIO.setup(19, GPIO.IN, pull_up_down = GPIO.PUD_UP)

GPIO.setup(26, GPIO.IN, pull_up_down = GPIO.PUD_UP)

#GPIO.setup(19, GPIO.OUT)

#pwm = GPIO.PWM(19, 100)
#pwm.start(100)

#os.system("gpio -g mode 19 pwm")
#os.system("gpio -g pwm 19 350")
os.system("sudo pigpiod")
time.sleep(1)
os.system("sudo pigs p 19 90")
#os.system("sudo killall pigpiod")
#os.system("sudo killall pigpiod")
def BL(channel):
	global duty
	duty = duty - 10
	if duty < 60:
		duty = 120
#	os.system("sudo pigpiod")
	os.system("sudo pigs p 19 %s" % duty)
#	os.system("sudo killall pigpiod")
#	global duty
#	duty = duty - 10
#	if duty == 10:
#		duty = 50
#	pwm.ChangeDutyCycle(duty)
#	print duty

GPIO.add_event_detect(26, GPIO.FALLING, callback = BL, bouncetime = 100)

try:
	while 1:
		time.sleep(1)

except KeyboardInterrupt:
	GPIO.cleanup()
