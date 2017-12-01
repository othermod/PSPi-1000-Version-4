#!/bin/bash
# https://www.othermod.com

if [ $(id -u) -ne 0 ]; then
	echo "Installer must be run as root."
	echo "Try 'sudo bash $0'"
	exit 1
fi

#bash apt-get/install.sh
bash /boot/buttons/install.sh
#bash pigpio/install.sh
bash /boot/joystick/install.sh
bash /boot/backlight/install.sh
bash /boot/shutdown/install.sh
bash /boot/uinput/python setup.py install

echo "Complete. Reboot is required."
	echo
echo "Reboot now? [y/n]"
read
if [[ "$REPLY" =~ ^(yes|y|Y)$ ]]; then
	echo "Rebooting..."
	reboot
#else
	echo
	echo "Done"
fi