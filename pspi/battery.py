#!/usr/bin/python
#https://www.othermod.com

#need to remove imports that are no longer used
import uinput, time, math
import array
import os
import signal
import subprocess
from subprocess import check_output

status = 10.5
charging = 0
#Set debug to 1 to display status
debug = 0


#number of battery readings to average together
average = 10

#refresh rate in seconds
refresh = 1

PNGVIEWPATH = "/boot/pspi/battery"
ICONPATH = "/boot/pspi/battery"
	
def changeicon(number):
    i = 0
    killid = 0
    os.system(PNGVIEWPATH + "/pngview -b 0 -l 3000" + number + " -x 450 -y 5 " + ICONPATH + "/battery" + number + ".png &")
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
	
def checkvoltage():
	global a
	a = [int(open('/sys/class/hwmon/hwmon0/device/in7_input').read())] + a[:-1]
#	return a
def checkstatus():
	global b
	b = int(open('/sys/class/hwmon/hwmon0/device/in6_input').read())
#	return b
# The loop polls GPIO and joystick state every 5s
os.system(PNGVIEWPATH + "/pngview -b 0 -l 299999 -x 450 -y 5 " + ICONPATH + "/blank.png &")
a = [int(open('/sys/class/hwmon/hwmon0/device/in7_input').read())] * average
#b = int(open('/sys/class/hwmon/hwmon0/device/in6_input').read())
while True:
    	# check battery states
	checkvoltage()
	checkstatus()
	bat = sum(a) / average
	if debug == 1:
		print bat
		print a
	if b > 500:
		if charging == 1:
			a = [a[0]] * average
		charging = 0
	if b < 1000 and a[0] > 3800:
		if charging == 0:
			a = [a[0]] * average
		charging = 1
	#not charging math
	#needs to know how to detect charger attached
	#emergency poweroff occurs at 3.5v
	if charging == 0:
		if bat < 3600: #change to 0 during troubleshooting
			if status != 0:
				changeicon("0")
			status = 0
			#needs to issue a shutdown
		
    		elif bat < 3638: #change to 0 during troubleshooting
        		if status > 1:
				changeicon("1")
			#might change this icon to the exclamation point
				status = 1
		
    		elif bat < 3678:
			if status > 2:
				changeicon("2")
				status = 2

		elif bat < 3716:
			if status > 3:
				changeicon("3")
				status = 3

    		elif bat < 3748:
			if status > 4:
				changeicon("4")
				status = 4

    		elif bat < 3786:
			if status > 5:
				changeicon("5")
				status = 5

    		elif bat < 3827:
			if status > 6:
				changeicon("6")
				status = 6
		
    		elif bat < 3873:
			if status > 7:
				changeicon("7")
				status = 7
	
    		elif bat < 3899:
			if status > 8:
				changeicon("8")
				status = 8
	
    		elif bat < 3939:
			if status > 9:
				changeicon("9")
				status = 9

    		else:
			if status > 10:
				changeicon("10")      
				status = 10
	if charging == 1:
		if bat < 4023:
			if status < 11:
				changeicon("11")
				status = 11
		elif bat < 4072:
			if status < 12:
				changeicon("12")
				status = 12
		elif bat < 4150:
			if status < 13:
				changeicon("13")
				status = 13
		else:
			if status < 14:
				changeicon("14")
				status = 14
    	time.sleep(refresh)

