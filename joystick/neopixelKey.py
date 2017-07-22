import uinput, time
import RPi.GPIO as GPIO
from Adafruit_ADS1x15 import ADS1x15
from neopixel import *

# ---- OPTIONS ----
#===================

# BCM GPIO PIN : ASCII KEYBOARD MAPPING (25 used by PiTFT)
# You can change the BCM GPIO map and corresponding key press event here
# Console: #13 BTN1, #16 BTN2, #19 BTN3, #20 BTN4, #21 BTN5, #26 TAC4, #6 TAC3, #5 TAC2, #0 TAC1, #27 EDGE1, #17 EDGE2
buttons = {
        19 : uinput.KEY_R,
        16 : uinput.KEY_Q,
        20 : uinput.KEY_X,
        21 : uinput.KEY_LEFTCTRL,
        13 : uinput.KEY_Z,
        17 : uinput.KEY_R,
        22 : uinput.KEY_ESC,
        23 : uinput.KEY_5,
        27 : uinput.KEY_1,
	26 : uinput.KEY_2,
	6  : uinput.KEY_3,
	5  : uinput.KEY_4,
	0  : uinput.KEY_6,
}

# LED strip configuration:
LED_COUNT      = 2      # Number of LED pixels.
LED_PIN        = 18      # GPIO pin connected to the pixels (must support PWM!).
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 5       # DMA channel to use for generating signal (try 5)
LED_BRIGHTNESS = 128     # Set to 0 for darkest and 255 for brightest
LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)

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

# Initialise the key press events for joystick
events = [uinput.KEY_UP, uinput.KEY_DOWN, uinput.KEY_LEFT, uinput.KEY_RIGHT]

# Initialise GPIO and button events
GPIO.setwarnings(False) # #16 is SD LED but we can still use it
GPIO.setmode(GPIO.BCM)

# Initialise Neopixels
strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS)
strip.begin()

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
        device.emit(key, 1)
        #print key
        #print button
	# Flash pixels
	strip.setPixelColor(0,Color(255,255,255))
	strip.setPixelColor(1,Color(255,255,255))
	strip.show()
    if state and GPIO.input(button):
        state = False
        device.emit(key, 0)
    return state

# Read and sets joystick events
def setStateJoy(state, extstate, key):
    if (not state) and extstate:
        state = True
        device.emit(key, 1)
        # device.emit_click(key)
    if state and (not extstate):
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
    extstate[0] = digitalJoy(Y_AXIS, 0)
    extstate[1] = digitalJoy(Y_AXIS, 1)
    extstate[2] = digitalJoy(X_AXIS, 0)
    extstate[3] = digitalJoy(X_AXIS, 1)
    # send joystick uinputs
    for x in range(4):
        key = events[x]
        joystate[x] = setStateJoy(joystate[x], extstate[x], key)

    time.sleep(.02)
    strip.setPixelColor(0,0)
    strip.setPixelColor(1,0)
    strip.show()
