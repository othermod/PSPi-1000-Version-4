#!/bin/bash
# Much of this is borrowed from Adafruit's Retrogame installer
# It has been modiified for offline installation

if [ $(id -u) -ne 0 ]; then
	echo "Installer must be run as root."
	echo "Try 'sudo bash $0'"
	exit 1
fi

# Given a list of strings representing options, display each option
# preceded by a number (1 to N), display a prompt, check input until
# a valid number within the selection range is entered.

echo "Copying config file /boot/retrogame.cfg."
if [ -e /boot/retrogame.cfg ]; then
	echo "File already exists."
	echo "Overwriting will reset buttons to default.."	
	echo "Overwrite file? [y/n] "
	read
	if [[ ! "$REPLY" =~ ^(yes|y|Y)$ ]]; then
		echo "Not overwritten."
	else
		if [ -e /boot/buttons/retrogame.cfg ]; then
			echo "File exists. Continuing."
			cp /boot/buttons/retrogame.cfg /boot/retrogame.cfg
			echo "Overwritten."
		else
			echo "File doesn't exist."
			echo "Copy retrogame.cfg to /boot/buttons/ and try again."
			echo "Failed."
			exit 1	
		fi	
	fi
else
	if [ -e /boot/buttons/retrogame.cfg ]; then
		echo "File exists. Continuing."
		cp /boot/buttons/retrogame.cfg /boot/retrogame.cfg
		echo "Copied."
	else
		echo "File doesn't exist."
		echo "Copy retrogame.cfg to /boot/buttons/ and try again."
		echo "Failed."
		exit 1	
	fi
	
	
fi
echo "Copying retrogame to /usr/local/bin/retrogame"
if [ -e /usr/local/bin/retrogame ]; then
	echo "/usr/local/bin/retrogame already exists."
	echo "Overwrite file? [y/n] "
	read
	if [[ ! "$REPLY" =~ ^(yes|y|Y)$ ]]; then
		echo "Not verwritten."
	else
		if [ -e /boot/buttons/retrogame ]; then
			echo "File exists. Continuing."
			cp /boot/buttons/retrogame /usr/local/bin/retrogame
			echo "Overwritten."
		else
			echo "File doesn't exist."
			echo "Copy retrogame to /boot/buttons and try again."
			echo "Failed."
			exit 1	
		fi
	fi
else
	if [ -e /boot/buttons/retrogame ]; then
		echo "File exists. Continuing."
		cp /boot/buttons/retrogame /usr/local/bin/retrogame
		echo "Copied."
	else
		echo "File doesn't exist."
		echo "Copy retrogame to /boot/buttons/ and try again."
		echo "Failed."
		exit 1	
	fi
fi


	echo "Configuring retrogame to start at boot..."
	# Add udev rule (will overwrite if present)
echo "SUBSYSTEM==\"input\", ATTRS{name}==\"retrogame\", ENV{ID_INPUT_KEYBOARD}=\"1\"" > /etc/udev/rules.d/10-retrogame.rules
	# Start on boot
grep retrogame /etc/rc.local >/dev/null
if [ $? -eq 0 ]; then
	echo "retrogame already exists in rc.local. Re-creating."
	# retrogame already in rc.local, but make sure correct:
	sed -i "s/^.*retrogame.*$/\/usr\/local\/bin\/retrogame \&/g" /etc/rc.local >/dev/null
else
	echo "retrogame doesn't exist in rc.local. Creating."
	# Insert retrogame into rc.local before final 'exit 0'
	sed -i "s/^exit 0/\/usr\/local\/bin\/retrogame \&\\nexit 0/g" /etc/rc.local >/dev/null
fi
