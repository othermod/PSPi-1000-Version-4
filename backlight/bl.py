import RPi.GPIO as GPIO
import time
pwmPin = 19
dc = 49
a = 1
GPIO.setmode(GPIO.BCM)
GPIO.setup(pwmPin, GPIO.OUT)
pwm = GPIO.PWM(pwmPin, 50)
pwm.start(dc)

try:
	while 1:
		pwm.ChangeDutyCycle(dc)
		#print dc
		if dc == 20 or dc == 50:
			a = -a
		
		dc = dc - a
		

		time.sleep(.1)


except KeyboardInterrupt:
	pwm.stop()
	GPIO.cleanup()
