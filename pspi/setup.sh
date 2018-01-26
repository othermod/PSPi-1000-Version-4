#!/bin/bash
# https://www.othermod.com
if [ $(id -u) -ne 0 ]; then
	echo "Installer must be run as root."
	echo "Try 'sudo bash $0'"
	exit 1
fi

echo "Configuring pspi to start at boot..."

grep pspi /etc/rc.local >/dev/null
if [ $? -eq 0 ]; then
	echo "pspi already exists in rc.local. Re-creating."
	# pspi already in rc.local, but make sure correct:
	sed -i "s/^.*pspi.*$/bash \/boot\/pspi\/boot.sh/g" /etc/rc.local >/dev/null
else
	echo "pspi doesn't exist in rc.local. Creating."
	# Insert pspi into rc.local before final 'exit 0'
	sed -i "s/^exit 0/bash \/boot\/pspi\/boot.sh\\nexit 0/g" /etc/rc.local >/dev/null
fi

echo "Copying config file /boot/retrogame.cfg."
if [ -e /boot/retrogame.cfg ]; then
	echo "File already exists."
	echo "Overwriting will reset buttons to default.."
	echo "Overwrite file? [y/n] "
	read
	if [[ ! "$REPLY" =~ ^(yes|y|Y)$ ]]; then
		echo "Not overwritten."
	else
		if [ -e /boot/pspi/buttons/retrogame.cfg ]; then
			echo "File exists. Continuing."
			cp /boot/pspi/buttons/retrogame.cfg /boot/retrogame.cfg
			echo "Overwritten."
		else
			echo "File doesn't exist."
			echo "Copy retrogame.cfg to /boot/buttons/ and try again."
			echo "Failed."
			exit 1
		fi
	fi
else
	if [ -e /boot/pspi/buttons/retrogame.cfg ]; then
		echo "File exists. Continuing."
		cp /boot/pspi/buttons/retrogame.cfg /boot/retrogame.cfg
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
		echo "Not overwritten."
	else
		if [ -e /boot/pspi/buttons/retrogame ]; then
			echo "File exists. Continuing."
			cp -f /boot/pspi/buttons/retrogame /usr/local/bin/retrogame
			echo "Overwritten."
		else
			echo "File doesn't exist."
			echo "Copy retrogame to /boot/buttons and try again."
			echo "Failed."
			exit 1
		fi
	fi
else
	if [ -e /boot/pspi/buttons/retrogame ]; then
		echo "File exists. Continuing."
		cp /boot/pspi/buttons/retrogame /usr/local/bin/retrogame
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
#if grep -q 'dtparam=i2c1=on' /boot/config.txt; then
#  echo 'Seems i2c1 parameter already set, skip this step.'
#else
#  echo 'dtparam=i2c1=on' >> /boot/config.txt
#fi
#if grep -q 'dtparam=i2c_arm=on' /boot/config.txt; then
#  echo 'Seems i2c_arm parameter already set, skip this step.'
#else
#  echo 'dtparam=i2c_arm=on' >> /boot/config.txt
#fi
if [ -f /etc/modprobe.d/raspi-blacklist.conf ]; then
#  sed -i 's/^blacklist spi-bcm2708/#blacklist spi-bcm2708/' /etc/modprobe.d/raspi-blacklist.conf
  sed -i 's/^blacklist i2c-bcm2708/#blacklist i2c-bcm2708/' /etc/modprobe.d/raspi-blacklist.conf
else
  echo 'File raspi-blacklist.conf does not exist, skip this step.'
fi

cp /boot/pspi/es_input.cfg /opt/retropie/configs/all/emulationstation/es_input.cfg
cp /boot/pspi/retroarch.cfg /opt/retropie/configs/all/retroarch.cfg
cp /boot/pspi/pspi.cfg /opt/retropie/configs/all/retroarch-joypads/pspi.cfg

cd /boot/uinput/
python setup.py install

cp /boot/pspi/cmdline.txt /boot/cmdline.txt


#wiringPi install - currently disabled
#cd /boot/wiringPi
#./build

cd /boot/pigpio
make
make install

#remove DHCP wait
rm -f /etc/systemd/system/dhcpcd.service.d/wait.conf

read -rsp $'Press any key to reboot...\n' -n1 key
reboot
