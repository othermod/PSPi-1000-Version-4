#!/bin/bash
# Much of this is borrowed from Adafruit's Retrogame installer
# It has been modiified for offline installation

if [ $(id -u) -ne 0 ]; then
	echo "Installer must be run as root."
	echo "Try 'sudo bash $0'"
	exit 1
fi


echo "Configuring joystick to start at boot..."

grep joystick /etc/rc.local >/dev/null
if [ $? -eq 0 ]; then
	echo "joystick already exists in rc.local. Re-creating."
	# joystick already in rc.local, but make sure correct:
	sed -i "s/^.*joystick.*$/python \/boot\/examples\/joystick.py \&/g" /etc/rc.local >/dev/null
else
	echo "joystick doesn't exist in rc.local. Creating."
	# Insert joystick into rc.local before final 'exit 0'
	sed -i "s/^exit 0/python \/boot\/examples\/joystick.py \&\\nexit 0/g" /etc/rc.local >/dev/null
fi

