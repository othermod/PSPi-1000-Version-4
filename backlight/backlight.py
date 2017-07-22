import os
from time import sleep
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(27, GPIO.IN, pull_up_down=GPIO.PUD_UP)

os.system("gpio -g mode 19 pwm")
os.system("gpio -g pwm 19 1023")

nums = [1023, 500, 200, 50]
i = 0

def my_callback(channel):
  global i
  global nums
  if i >= len(nums) - 1:
    i = 0
  else:
    i = i + 1
  os.system("gpio -g pwm 19 %s" % nums[i])
  GPIO.remove_event_detect(27)
  sleep(0.1)
  GPIO.add_event_detect(27, GPIO.FALLING, callback=my_callback, bouncetime=300)

GPIO.add_event_detect(27, GPIO.FALLING, callback=my_callback, bouncetime=300)

try:
  while True:
    sleep(0.01)
    pass
except KeyboardInterrupt:
  GPIO.cleanup()
  os.system("gpio -g mode 19 in")       # clean up GPIO on CTRL+C exit  
GPIO.cleanup()           # clean up GPIO on normal exit  