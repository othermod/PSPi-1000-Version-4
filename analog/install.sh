#!/bin/bash
# Much of this is borrowed from Adafruit's Retrogame installer
# It has been modiified for offline installation
#change everything here so that it re-creates the line instead of adding a new one. That way it won't make duplicates.
if [ $(id -u) -ne 0 ]; then
	echo "Installer must be run as root."
	echo "Try 'sudo bash $0'"
	exit 1
fi

if [ "$(id -u)" != 0 ]; then
  echo 'Sorry, you need to run this script with sudo'
  exit 1
fi

# enable I2C on Raspberry Pi
echo '>>> Enable I2C'
if grep -q 'i2c-bcm2708' /etc/modules; then
  echo 'Seems i2c-bcm2708 module already exists, skip this step.'
else
  echo 'i2c-bcm2708' >> /etc/modules
fi
if grep -q 'i2c-dev' /etc/modules; then
  echo 'Seems i2c-dev module already exists, skip this step.'
else
  echo 'i2c-dev' >> /etc/modules
fi

if grep -q '#dtoverlay=i2c0-bcm2708,pins_28_29' /boot/config.txt; then
	echo 'Uncommenting CSI'
	echo 'dtoverlay=i2c0-bcm2708,pins_28_29' >> /boot/config.txt
fi

if grep -q 'dtparam=i2c_vc=on' /boot/config.txt; then
  echo 'Seems i2c_vc parameter already set, skip this step.'
else
  echo 'dtparam=i2c_vc=on' >> /boot/config.txt
fi
if grep -q 'dtparam=i2c_arm=on' /boot/config.txt; then
  echo 'Seems i2c_arm parameter already set, skip this step.'
else
  echo 'dtparam=i2c_arm=on' >> /boot/config.txt
fi
if grep -q 'dtoverlay=i2c0-bcm2708,pins_28_29' /boot/config.txt; then
  echo 'CSI is already configured, skipping this step.'
else
  echo 'dtoverlay=i2c0-bcm2708,pins_28_29' >> /boot/config.txt
fi
if [ -f /etc/modprobe.d/raspi-blacklist.conf ]; then
  sed -i 's/^blacklist spi-bcm2708/#blacklist spi-bcm2708/' /etc/modprobe.d/raspi-blacklist.conf
  sed -i 's/^blacklist i2c-bcm2708/#blacklist i2c-bcm2708/' /etc/modprobe.d/raspi-blacklist.conf
else
  echo 'File raspi-blacklist.conf does not exist, skip this step.'
fi
 
# install i2c-tools
echo '>>> Install i2c-tools'
if hash i2cget 2>/dev/null; then
  echo 'Seems i2c-tools is installed already, skip this step.'
else
	sudo dpkg -i /boot/analog/i2c-tools_3.1.1+svn-2_armhf.deb
	sudo dpkg -i /boot/analog/python-smbus_3.1.1+svn-2_armhf.deb
fi
