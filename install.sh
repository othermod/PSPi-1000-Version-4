#!/bin/bash
# Much of this is borrowed from Adafruit's Retrogame installer
# It has been modiified for offline installation

if [ $(id -u) -ne 0 ]; then
	echo "Installer must be run as root."
	echo "Try 'sudo bash $0'"
	exit 1
fi

bash apt-get/install.sh
bash buttons/install.sh
bash pigpio/install.sh
bash joystick/install.sh
python python-uinput-master/setup.py install
sudo make install


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