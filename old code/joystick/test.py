import time
import RPi.GPIO as GPIO
from Adafruit_ADS1x15 import ADS1x15

# ---- OPTIONS ----
#===================

# BCM GPIO PIN : ASCII KEYBOARD MAPPING (25 used by PiTFT)
# You can change the BCM GPIO map and corresponding key press event here
# Console: #13 BTN1, #16 BTN2, #19 BTN3, #20 BTN4, #21 BTN5
buttons = {
        19 : 1,
        16 : 1,
        20 : 1,
        21 : 1,
        13 : 1,
        17 : 1,
        22 : 1,
        23 : 1,
        27 : 1
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
joystate = [0] * 4 # joystick internal state
extstate = [0] * 4 # joystick external state

# Initialise the ADC using the default mode (use default I2C address)
adc = ADS1x15(ic=ADS1015)
gain = 4096
sps = 250

# Initialise GPIO and button events
GPIO.setwarnings(False) # #16 is SD LED but we can still use it
GPIO.setmode(GPIO.BCM)
GPIO.setup(4, GPIO.OUT, pull_up_down=GPIO.PUD_DOWN) # pull-up so button connects to ground
GPIO.output(4,False)
for x in buttons:
    GPIO.setup(x, GPIO.IN, pull_up_down=GPIO.PUD_UP) # pull-up so button connects to ground

# Function to read data from I2C chip using Adafruit lib
# Channel must be an integer 0-3
def ReadChannel(channel):
    data = adc.readADCSingleEnded(channel, gain, sps)
    #print data
    return data

# Converts ADC reading to digital button states
def digitalJoy(axis, direction):
    value = ReadChannel(axis)
    if direction:
        if (value > (VREF/2 + DZONE)):
            return 1
        else:
            return 0

    else:
        if (value < (VREF/2 - DZONE)):
            return 1
        else:
            return 0

# Read and sets state of GPIO buttons
def setState(state, button, key):
    if (not state) and (not GPIO.input(button)):
        state = True
        GPIO.output(4,True)
        # print key
        # print button
    if state and GPIO.input(button):
        state = False
        GPIO.output(4,False)
    return state

# Read and sets joystick events
def setStateJoy(state, extstate, key):
    if (not state) and extstate:
        state = True
        GPIO.output(4,True)
    if state and (not extstate):
        GPIO.output(4,False)
        state = False
    return state

# The loop polls GPIO and joystick state every 20ms
while True:
    # check button states
    for button in buttons:
        state[button] = setState(state[button],button,1)
    # check joystick states
    extstate[0] = digitalJoy(Y_AXIS, 0)
    extstate[1] = digitalJoy(Y_AXIS, 1)
    extstate[2] = digitalJoy(X_AXIS, 0)
    extstate[3] = digitalJoy(X_AXIS, 1)
    # send joystick uinputs
    for x in range(4):
        joystate[x] = setStateJoy(joystate[x], extstate[x], 1)

    time.sleep(.02)
