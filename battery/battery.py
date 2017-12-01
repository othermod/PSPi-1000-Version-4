#https://www.othermod.com
#need to remove old portions of code

import uinput, time, math
#import RPi.GPIO as GPIO
#!/usr/bin/python
import array
import os
import signal
import subprocess
from subprocess import check_output


warning = 0
status = 0
value = 4200

PNGVIEWPATH = "/boot/battery/pngview"
ICONPATH = "/boot/battery/icons"
DEBUGMSG = 0
	
def changeicon(percent):
    i = 0
    killid = 0
    os.system(PNGVIEWPATH + "/pngview -b 0 -l 3000" + percent + " -x 460 -y 5 " + ICONPATH + "/battery" + percent + ".png &")
    if DEBUGMSG == 1:
        print("Changed battery icon to " + percent + "%")
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
status = 0
bat1 = int(open('/sys/class/hwmon/hwmon0/device/in6_input').read())
bat2 = bat1
bat3 = bat1
bat4 = bat1
bat5 = bat1
while True:
    # check battery states
	bat5 = bat4
	bat4 = bat3
	bat3 = bat2
	bat2 = bat1
	bat1 = int(open('/sys/class/hwmon/hwmon0/device/in6_input').read())
	a = [bat1, bat2, bat3, bat4, bat5]
	bat = (sum(a) / len(a))
#	print bat
	if bat < 3600: #change to 0 during troubleshooting
		changeicon("0")
		os.system("/usr/bin/omxplayer --no-osd --layer 999999  " + ICONPATH + "/lowbattshutdown.mp4 --alpha 160;sudo shutdown -h now")
		status = 0
		
    	elif bat < 3657: #change to 0 during troubleshooting
        	changeicon("1")
		if CLIPS == 1:
			os.system("/usr/bin/omxplayer --no-osd --layer 999999  " + ICONPATH + "/lowbattalert.mp4 --alpha 160")
		
    	elif bat < 3723:
		if status != 2:
			changeicon("2")
		status = 2

    	elif bat < 3756:
		if status != 3:
			changeicon("3")
		status = 3

    	elif bat < 3798:
		if status != 4:
			changeicon("4")
		status = 4
		
    	elif bat < 3876:
		if status != 5:
			changeicon("5")
		status = 5
	
    	elif bat < 3963:
		if status != 6:
			changeicon("6")
		status = 6
	
    	elif bat < 4059:
		if status != 7:
			changeicon("7")
		status = 7
	
    	else:
		if status != 8:
			changeicon("8")      
		status = 8
    	time.sleep(5)

