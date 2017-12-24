#!/bin/bash
# https://www.othermod.com
if [ $(id -u) -ne 0 ]; then
	echo "Installer must be run as root."
	echo "Try 'sudo bash $0'"
	exit 1
fi


echo "Configuring joystick to start at boot..."

grep joystick.py /etc/rc.local >/dev/null
if [ $? -eq 0 ]; then
	echo "Joystick already exists in rc.local. Re-creating."
	# joystick already in rc.local, but make sure correct:
	sed -i "s/^.*joystick.py.*$/python \/boot\/joystick\/joystick.py \&/g" /etc/rc.local >/dev/null
else
	echo "joystick doesn't exist in rc.local. Creating."
	# Insert joystick into rc.local before final 'exit 0'
	sed -i "s/^exit 0/python \/boot\/joystick\/joystick.py \&\\nexit 0/g" /etc/rc.local >/dev/null
fi
echo "starting joystick"
python /boot/joystick/joystick.py &
sleep 2
echo "calibrating joystick"
jscal -c /dev/input/js0
echo "sleep 1" > /home/pi/joystick.sh
jscal -p /dev/input/js0 >> /home/pi/joystick.sh
grep joystick.sh /etc/rc.local >/dev/null
if [ $? -eq 0 ]; then
	echo "Calibration already set to load at bootup. Re-creating"
	# joystick already in rc.local, but make sure correct:
	sed -i "s/^.*joystick.sh.*$/bash \/home\/pi\/joystick.sh/g" /etc/rc.local >/dev/null
else
	echo "Calibration not set to load at bootup. Creating."
	# Insert joystick into rc.local before final 'exit 0'
	sed -i "s/^exit 0/bash \/home\/pi\/joystick.sh\\nexit 0/g" /etc/rc.local >/dev/null
fi
