import uinput, time, math
import RPi.GPIO as GPIO
#!/usr/bin/python
import array
import os
import signal
import subprocess
import sys
from subprocess import check_output

# A button is needed to initiate configuration in RetroPie. Can be removed after RetroPie configuration.
buttons = {
       27 : uinput.BTN_JOYSTICK
        }

# Hardware settings
DZONE = 500 # dead zone applied to joystick (mV)
VREF = 3300 # joystick Vcc (mV)

state = {x : 0 for x in buttons} # button internal state

# Initialise the joystick events, mapped between the voltage readings of the ADC:
# 0 - Down/Right : VREF/2 - Center : VREF - Up/Left
events = [uinput.ABS_X + (0, VREF, 0, 0), uinput.ABS_Y + (0, VREF, 0, 0)]

# Initialise GPIO and button events. Can be removed after RetroPie configuration.
GPIO.setmode(GPIO.BCM)
for x in buttons:
    GPIO.setup(x, GPIO.IN, pull_up_down=GPIO.PUD_UP) # pull-up so button connects to ground
    # append buttons used to uinput events
    events.append(buttons[x])

# Setup HID emulator, wait a second
device = uinput.Device(events)
time.sleep(1)

#Center the sticks
device.emit(uinput.ABS_X, VREF/2, syn=False);
device.emit(uinput.ABS_Y, VREF/2);

# Read and sets state of GPIO buttons
def setState(state, button, key):
    if (not state) and (not GPIO.input(button)):
        state = True
        device.emit(key, 1)
        # print key
        # print button
    if state and GPIO.input(button):
        state = False
        device.emit(key, 0)
    return state

# The loop polls GPIO and joystick state every 50ms
while True:
	#Gets the ADC values for channels 0 and 1 from the OS,
	an0 = int(open('/sys/class/hwmon/hwmon0/device/in4_input').read())
	an1 = int(open('/sys/class/hwmon/hwmon0/device/in5_input').read())
    #Check button states. Can be removed after Retropie Configuration.
	for button in buttons:
        	key = buttons[button]
        	state[button] = setState(state[button],button,key)
    #Check and apply joystick states
	if (an0 > (VREF/2 + DZONE)) or (an0 < (VREF/2 - DZONE)):
		device.emit(uinput.ABS_X, an0 - 100 - 200 * (an0 < VREF/2 - DZONE) + 200 * (an0 > VREF/2 + DZONE))
	else:
		#Center the sticks if within deadzone
		device.emit(uinput.ABS_X, VREF/2)
	if (an1 > (VREF/2 + DZONE)) or (an1 < (VREF/2 - DZONE)):
		device.emit(uinput.ABS_Y, an1 + 100 - 200 * (an1 < VREF/2 - DZONE) + 200 * (an1 > VREF/2 + DZONE))
	else:
		#Center the sticks if within deadzone
		device.emit(uinput.ABS_Y, VREF/2)
	time.sleep(.05)
            
			
import uinput, time, math
import RPi.GPIO as GPIO
from Adafruit_ADS1x15 import ADS1x15
#!/usr/bin/python
import array
import os
import signal
import subprocess
from subprocess import check_output

from config import *

warning = 0
status = 0
value = 4200
# ---- OPTIONS ----
#===================

# BCM GPIO PIN : ASCII KEYBOARD MAPPING (25 used by PiTFT)
# You can change the BCM GPIO map and corresponding key press event here
# Console: #13 BTN1, #16 BTN2, #19 BTN3, #20 BTN4, #21 BTN5
# A single button is needed to initiate configuration in RetroPie
buttons = {
        11 : uinput.BTN_JOYSTICK
        }

# Joystick AXIS mapping to ADC channels
X_AXIS = 0
Y_AXIS = 1
BATTERY = 2

# Hardware settings
ADS1015 = 0x00  # 12-bit ADC
DZONE = 500 # dead zone applied to joystick (mV)
VREF = 5200 # joystick Vcc (mV), will be 5200 in final build

# ---- OPTIONS END ----
#=======================

state = {x : 0 for x in buttons} # button internal state

# Initialise the ADC using the default mode (use default I2C address)
adc = ADS1x15(ic=ADS1015)
gain = 6144
sps = 250

# Initialise the joystick events, mapped between the voltage readings of the ADC:
# 0 - Down/Right : VREF/2 - Center : VREF - Up/Left
events = [uinput.ABS_X + (0, VREF, 0, 0), uinput.ABS_Y + (0, VREF, 0, 0)]

# Initialise GPIO and button events
GPIO.setmode(GPIO.BCM)
for x in buttons:
    GPIO.setup(x, GPIO.IN, pull_up_down=GPIO.PUD_UP) # pull-up so button connects to ground
    # append buttons used to uinput events
    events.append(buttons[x])

# Setup HID emulator
device = uinput.Device(events)
time.sleep(1)

# center sticks
device.emit(uinput.ABS_X, VREF/2, syn=False);
device.emit(uinput.ABS_Y, VREF/2);

# Function to read data from I2C chip using Adafruit lib
# Channel must be an integer 0-3
def ReadChannel(channel):
    data = adc.readADCSingleEnded(channel, gain, sps)
    return data
	
	
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
	
# Prepare handlers for process exit
signal.signal(signal.SIGTERM, endProcess)
signal.signal(signal.SIGINT, endProcess)

# Maps ADC reading to Joystick position
def digitalJoy(axis):
    value = int(ReadChannel(axis))
#    print value
	# If the stick moved in a direction outside the deadzone 
	# Added some math to increase the joystick range
    if (value > (VREF/2 + DZONE)) or (value < (VREF/2 - DZONE)):
        if axis == X_AXIS:
            device.emit(uinput.ABS_X, value - 100 - 200 * (value < VREF/2 - DZONE) + 200 * (value > VREF/2 + DZONE))
        if axis == Y_AXIS:
            device.emit(uinput.ABS_Y, value + 100 - 200 * (value < VREF/2 - DZONE) + 200 * (value > VREF/2 + DZONE))
    # center the sticks
    else: 
        if axis == X_AXIS:
            device.emit(uinput.ABS_X, VREF/2)
        if axis == Y_AXIS:
            device.emit(uinput.ABS_Y, VREF/2)
    global value

		
	
    
# Read and sets state of GPIO buttons
def setState(state, button, key):
    if (not state) and (not GPIO.input(button)):
        state = True
        device.emit(key, 1)
        # print key
        # print button
    if state and GPIO.input(button):
        state = False
        device.emit(key, 0)
    return state

# The loop polls GPIO and joystick state every 20ms
os.system(PNGVIEWPATH + "/pngview -b 0 -l 299999 -x 460 -y 5 " + ICONPATH + "/blank.png &")
while True:
    # check button states
    for button in buttons:
        key = buttons[button]
        state[button] = setState(state[button],button,key)
    # check joystick states
    digitalJoy(Y_AXIS)
#    print value
    digitalJoy(X_AXIS)
#    print value
    digitalJoy(BATTERY)
#    print value
#    print (time.strftime("%H:%M:%S"))
#    print status
    global status
    if value < 3500: #change to 0 during troubleshooting
	changeicon("0")
	os.system("/usr/bin/omxplayer --no-osd --layer 999999  " + ICONPATH + "/lowbattshutdown.mp4 --alpha 160;sudo shutdown -h now")
	status = 0
		
    elif value < 3657: #change to 0 during troubleshooting
        changeicon("12")
	if CLIPS == 1:
		os.system("/usr/bin/omxplayer --no-osd --layer 999999  " + ICONPATH + "/lowbattalert.mp4 --alpha 160")
		
    elif value < 3723:
	if status != 25:
		changeicon("25")
	status = 25

    elif value < 3756:
	if status != 38:
		changeicon("38")
	status = 38

    elif value < 3798:
	if status != 50:
		changeicon("50")
	status = 50	
		
    elif value < 3876:
	if status != 62:
		changeicon("62")
	status = 62
	
    elif value < 3963:
	if status != 75:
		changeicon("75")
	status = 75
	
    elif value < 4059:
	if status != 88:
		changeicon("88")
	status = 88
	
    else:
	if status != 100:
		changeicon("100")      
	status = 100
    time.sleep(.05)

