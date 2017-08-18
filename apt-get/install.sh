#!/bin/bash
# Much of this is borrowed from Adafruit's Retrogame installer
# It has been modiified for offline installation

if [ $(id -u) -ne 0 ]; then
	echo "Installer must be run as root."
	echo "Try 'sudo bash $0'"
	exit 1
fi

sudo dpkg -i /boot/apt-get/i2c-tools_3.1.1+svn-2_armhf.deb
sudo dpkg -i /boot/apt-get/python-smbus_3.1.1+svn-2_armhf.deb