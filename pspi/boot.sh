#!/bin/bash
# https://www.othermod.com
if [ $(id -u) -ne 0 ]; then
	echo "Installer must be run as root."
	echo "Try 'sudo bash $0'"
	exit 1
fi

python /boot/pspi/battery.py &
python /boot/pspi/joystick.py &
python /boot/pspi/shutdown.py &
/usr/local/bin/retrogame &
/usr/bin/tvservice -o
python /boot/pspi/backlight.py &
