# PiJuice Input Board Python HID Emulator

The Python scripts within this repository can be used with the ADS1015 and PiJuice input
board to emulate a keyboard, mouse or joystick input device. The devices work
with AdvMame, PiPlay and X Window (`startx`). I haven't had success with
Mame4All (my USB keyboard doesn't work either though...).

# Dependancies

The scripts use the following (install in this order):

* python-smbus - `sudo apt-get install python-smbus`.
* libudev - `sudo apt-get install libudev-dev`.
* python-uinput - `sudo pip install python-uinput` (`apt-get install
  python-pip` if you don't have 'pip').
* I2C must be enabled - using `raspi-config` or add 'i2c_bcm2708', 'i2c_dev' to
  '/etc/modules'.
* *rpi\_ws281x - if you want neopixels `sudo pip install rpi_ws2812x`.*

# Install/Run

```
# Install dependancies - see above
# Clone folder
git clone https://github.com/tuna-f1sh/pijuice-console
# Change to directory
cd pijuice-console
# Load uinput module
sudo modprobe uinput
# Run the script as a background task (& at end)
sudo python digitalJoy.py &
# For a Neopixel demo, which flashes the pixels on each button press
sudo python neopixelJoy.py &
```

If all the above dependancies exist the script should now be running in the
background. Start whatever software you want to control. For example, to run X
Window desktop with the joystick as a mouse (stop any existing instances using
`fg` to bring the task into the foreground then pressing 'Ctrl-C'):

```
sudo python mouseJoy.py &
startx
```

Remember to stop any instances of the task using `fg` followed by 'Ctrl-C',
before starting another.

## Run at Boot

Once you've got the script running and mapping correct, you can set it to run
at boot by editing `/etc/rc.local`:

```
sudo nano /etc/rc.local
# Add this before 'exit 0'
python /home/pi/pijuice-console/digitalJoy.py & # or whereever/whatever script
```

You also need to load the uinput module at boot by adding 'uinput' to
'/etc/modules' (`sudo nano /etc/modules/`).

# Mapping

If you want to change the button mapping, open the script (`nano digitalJoy.py`)
navigate to the 'buttons' **dictionary**. The **key** (LH) is the BCM GPIO pin
and the **value** (RH) is the key to emulate upon press event. For example, to
map 17 to spacebar:

```python
17: uinput.KEY_SPACE
```

# Troubleshooting

* If 'Cannot find I2C device...', the I2C module has not loaded correctly. Try
  `sudo rmmod i2c-bcm2708;sudo modprobe i2c-bcm2708`.
* GPIO 16 is the SD LED. I can be used but you might get a warning.
* 'Error accessing 0x48...' - ensure that the console PCB is connected to the correct pins SDA/SDC.

# Credits

Developed by John Whittington -
[@j_whittington](http://www.twitter.com/j_whittington) - [JBR
Engineering](http://www.jbrengineering.co.uk)

Uses [Adafruit ADS1X15 Library](https://github.com/adafruit/Adafruit-Raspberry-Pi-Python-Code) and [python-uinput](https://github.com/tuomasjjrasanen/python-uinput)
