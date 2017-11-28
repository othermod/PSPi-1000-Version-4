import uinput, time
import RPi.GPIO as GPIO
from Adafruit_ADS1x15 import ADS1x15

# ---- OPTIONS ----
#===================

# BCM GPIO PIN : ASCII KEYBOARD MAPPING (25 used by PiTFT)
# You can change the BCM GPIO map and corresponding key press event here
# Console: #13 BTN1, #16 BTN2, #19 BTN3, #20 BTN4, #21 BTN5
buttons = {
        17 : uinput.KEY_Z,
        19 : uinput.KEY_SPACE,
        20 : uinput.KEY_ENTER,
        21 : uinput.BTN_RIGHT,
        13 : uinput.BTN_LEFT
        }

# Joystick AXIS mapping to ADC channels
Y_AXIS = 0
X_AXIS = 1

# Hardware settings
ADS1015 = 0x00  # 12-bit ADC
DZONE = 500 # dead zone applied to joystick (mV)
VREF = 3300 # joystick Vcc (mV)

# ---- OPTIONS END ----
#=======================

state = {x : 0 for x in buttons} # button internal state

# Initialise the ADC using the default mode (use default I2C address)
adc = ADS1x15(ic=ADS1015)
gain = 4096
sps = 250

# Initialise the events for mouse
events = [uinput.REL_X, uinput.REL_Y]

# Initialise GPIO and button events
GPIO.setmode(GPIO.BCM)
for x in buttons:
    GPIO.setup(x, GPIO.IN, pull_up_down=GPIO.PUD_UP) # pull-up so button connects to ground
    # append buttons used to uinput events
    events.append(buttons[x])

# Setup HID emulator
device = uinput.Device(events)
time.sleep(1) # wait helps driver loading

# Function to read data from I2C chip using Adafruit lib
# Channel must be an integer 0-3
def ReadChannel(channel):
    data = adc.readADCSingleEnded(channel, gain, sps)
    #print data
    return data

# Reads joystick state and moves the mouse in the corresponding direction
def digitalJoy(axis):
    value = ReadChannel(axis)
    # move mouse if joystick moved
    if (value > (VREF/2 + DZONE)):
        if axis == X_AXIS:
            device.emit(uinput.REL_X, 5)
        else:
            device.emit(uinput.REL_Y, 5)
    # center the sticks
    elif (value < (VREF/2 - DZONE)):
        if axis == X_AXIS:
            device.emit(uinput.REL_X, -5)
        else:
            device.emit(uinput.REL_Y, -5)

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
while True:
    # check button states
    for button in buttons:
        key = buttons[button]
        state[button] = setState(state[button],button,key)
    # check joystick states
    digitalJoy(Y_AXIS)
    digitalJoy(X_AXIS)

    time.sleep(.02)
