#!/bin/bash
# https://www.othermod.com
if [ $(id -u) -ne 0 ]; then
	echo "Installer must be run as root."
	echo "Try 'sudo bash $0'"
	exit 1
fi


echo "Configuring shutdown to start at boot..."

grep shutdown /etc/rc.local >/dev/null
if [ $? -eq 0 ]; then
	echo "shutdown already exists in rc.local. Re-creating."
	# shutdown already in rc.local, but make sure correct:
	sed -i "s/^.*shutdown.*$/python \/boot\/shutdown\/shutdown.py \&/g" /etc/rc.local >/dev/null
else
	echo "shutdown doesn't exist in rc.local. Creating."
	# Insert shutdown into rc.local before final 'exit 0'
	sed -i "s/^exit 0/python \/boot\/shutdown\/shutdown.py \&\\nexit 0/g" /etc/rc.local >/dev/null
fi

