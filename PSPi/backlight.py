import RPi.GPIO as GPIO 
import time 
import os  
duty = [.2, .25, .325, .45]
bl = 2
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(26, GPIO.IN, pull_up_down = GPIO.PUD_UP)
os.system("sudo /boot/PSPi/pi-blaster --pcm")
time.sleep(1)
os.system("echo '19=.325' > /dev/pi-blaster")
def BL(channel):
	global duty
	global bl
	bl = bl - 1
	if bl < 0:
		bl = 3
	os.system("echo '19=%s' > /dev/pi-blaster" % duty[bl])

GPIO.add_event_detect(26, GPIO.FALLING, callback = BL, bouncetime = 300)


try:
	while 1:
		time.sleep(1)

except KeyboardInterrupt:
	GPIO.cleanup()
