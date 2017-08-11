# gbzbatterymonitor

# Installation

## Hardware part
1. Buy a MCP3008 and some resistors suitable for this project, you can calculate resistor value here: [voltage divider calculator](http://www.raltron.com/cust/tools/voltage_divider.asp), Vin = 4.2V and Vout needs to be maximum 3.3V. I used a 2kOhm and a 5,6kOhm resistor.
2. Wire up the MCP3008 like this mockup: ![Image of wiring](https://github.com/joachimvenaas/gbzbatterymonitor/raw/master/help/mockup.jpg)
3. Measure the voltage of the connecting point of the two resistors and to ground, it should not be over 3.3V
4. If you want you can wire up LEDs aswell.

## Software part
1. Install [Raspidmx (pngview)](https://github.com/AndrewFromMelbourne/raspidmx/) and compile it by using `make`
2. Install this script by running the following command from terminal or ssh: `git clone https://github.com/joachimvenaas/gbzbatterymonitor`
3. Navigate into the gbzbatterymonitor folder: `cd gbzbatterymonitor`
4. Edit the config by typing `nano config.py` Here you must edit the battery voltages to suit your needs, add the path to pngview and icons and add the resistor values.
5. Test the script by running command: `python main.py`
6. If the script runs as desired you can close it by pressing Ctrl+C
7. Add the script to startup by typing `sudo nano /etc/rc.local` and add `python /home/pi/gbzbattery/main.py &` before `exit 0`
8. Reboot to test
9. You can close the script by killing its process id. Find the id by typing `ps aux | grep gbzbattery`. Then `kill <id>`

### Optional
1. Charge your battery to 100%
2. Run `python monitor.py` to get the exact values from the battery
3. Let the battery run down to 3.2V
4. Copy the data to Excel or something simular and calculate the 75%, 50% and 25% values
5. Edit the config.py file with the newly gattered data to get more accurate batterymeter

##### Sources and inspiration:
- www.sudomod.com
- https://github.com/aboudou/picheckvoltage
- https://github.com/Camble/GBZ-Power-Monitor_PB
- https://github.com/AndrewFromMelbourne/raspidmx/
