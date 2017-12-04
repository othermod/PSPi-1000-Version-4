#!/usr/bin/python
#https://www.othermod.com

#need to remove imports that are no longer used
import uinput, time, math
import array
import os
import signal
import subprocess
from subprocess import check_output

status = 0

#Set debug to 1 to display status
debug= 0

#number of battery readings to average together
average = 10

#refresh rate in seconds
refresh = 6

PNGVIEWPATH = "/boot/battery/pngview"
ICONPATH = "/boot/battery/icons"
	
def changeicon(number):
    i = 0
    killid = 0
    os.system(PNGVIEWPATH + "/pngview -b 0 -l 3000" + number + " -x 460 -y 5 " + ICONPATH + "/battery" + number + ".png &")
    if debug == 1:
        print("Changed battery icon to " + number)
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
	

# The loop polls GPIO and joystick state every 5s
os.system(PNGVIEWPATH + "/pngview -b 0 -l 299999 -x 460 -y 5 " + ICONPATH + "/blank.png &")
a = [int(open('/sys/class/hwmon/hwmon0/device/in6_input').read())] * average
while True:
    	# check battery states
	a = [int(open('/sys/class/hwmon/hwmon0/device/in6_input').read())] + a[:-1]
	bat = sum(a) / average
	if debug == 1:
		print bat
	if bat < 3630: #change to 0 during troubleshooting
		changeicon("0")
		status = 0
		
    	elif bat < 3670: #change to 0 during troubleshooting
        	changeicon("1")
		
    	elif bat < 3720:
		if status != 2:
			changeicon("2")
		status = 2

		elif bat < 3740:
		if status != 3:
			changeicon("3")
		status = 3

    	elif bat < 3770:
		if status != 4:
			changeicon("4")
		status = 4

    	elif bat < 3800:
		if status != 5:
			changeicon("5")
		status = 5

    	elif bat < 3870:
		if status != 6:
			changeicon("6")
		status = 6
		
    	elif bat < 4000:
		if status != 7:
			changeicon("7")
		status = 7
	
    	elif bat < 4040:
		if status != 8:
			changeicon("8")
		status = 8
	
    	elif bat < 4080:
		if status != 9:
			changeicon("9")
		status = 9
	
    	else:
		if status != 10:
			changeicon("10")      
		status = 10
    	time.sleep(refresh)

