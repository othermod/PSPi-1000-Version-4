#!/bin/bash
# https://www.othermod.com
if [ $(id -u) -ne 0 ]; then
	echo "Installer must be run as root."
	echo "Try 'sudo bash $0'"
	exit 1
fi


echo "Configuring backlight to start at boot..."

grep backlight /etc/rc.local >/dev/null
if [ $? -eq 0 ]; then
	echo "backlight already exists in rc.local. Re-creating."
	# backlight already in rc.local, but make sure correct:
	sed -i "s/^.*backlight.*$/python \/boot\/backlight\/backlight.py \&/g" /etc/rc.local >/dev/null
else
	echo "backlight doesn't exist in rc.local. Creating."
	# Insert backlight into rc.local before final 'exit 0'
	sed -i "s/^exit 0/python \/boot\/backlight\/backlight.py \&\\nexit 0/g" /etc/rc.local >/dev/null
fi

