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

echo "Copying config file /boot/retrogame.cfg"
cp -f /boot/pspi/buttons/retrogame.cfg /boot/retrogame.cfg

echo "Copying retrogame to /usr/local/bin/retrogame"
cp -f /boot/pspi/buttons/retrogame /usr/local/bin/retrogame


echo "Configuring retrogame..."
# Add udev rule (will overwrite if present)
echo "SUBSYSTEM==\"input\", ATTRS{name}==\"retrogame\", ENV{ID_INPUT_KEYBOARD}=\"1\"" > /etc/udev/rules.d/10-retrogame.rules

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

cp -f /boot/pspi/configs/es_input.cfg /opt/retropie/configs/all/emulationstation/es_input.cfg
cp -f /boot/pspi/configs/retroarch.cfg /opt/retropie/configs/all/retroarch.cfg
cp -f /boot/pspi/configs/pspi.cfg /opt/retropie/configs/all/retroarch-joypads/pspi.cfg

cd /boot/uinput/
python setup.py install

cp -f /boot/pspi/configs/cmdline.txt /boot/cmdline.txt

#remove DHCP wait
rm -f /etc/systemd/system/dhcpcd.service.d/wait.conf

#add custom startup image
cp -f /boot/pspi/configs/pspi.png /home/pi/RetroPie/splashscreens/pspi.png
cp -f /boot/pspi/configs/splashscreen.list /etc/splashscreen.list

#modify theme
cp -f /boot/pspi/configs/carbon.xml /etc/emulationstation/themes/carbon/carbon.xml
cp -f /boot/pspi/configs/background.png /etc/emulationstation/themes/carbon/art/background.png

#add WiFi options to retropie menu
cp -f '/boot/pspi/configs/othermod - WiFi Disable.sh' '/home/pi/RetroPie/retropiemenu/othermod - WiFi Disable.sh'
cp -f '/boot/pspi/configs/othermod - WiFi Enable.sh' '/home/pi/RetroPie/retropiemenu/othermod - WiFi Enable.sh'
cp -f '/boot/pspi/configs/othermod - WiFi Normal Speed.sh' '/home/pi/RetroPie/retropiemenu/othermod - WiFi Normal Speed.sh'
cp -f '/boot/pspi/configs/othermod - WiFi Super Speed.sh' '/home/pi/RetroPie/retropiemenu/othermod - WiFi Super Speed.sh'

read -rsp $'Press any key to reboot...\n' -n1 key
reboot

