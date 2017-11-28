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
            
