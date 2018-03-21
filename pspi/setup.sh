#!/bin/bash
# https://www.othermod.com
if [ $(id -u) -ne 0 ]; then
	echo "Installer must be run as root."
	echo "Try 'sudo bash $0'"
	exit 1
fi

echo "Configuring pspi to start at boot..."

#boot script should have the necessary lines(battery, poweroff, backlight, buttons), then new ones should be added after a y/n question(joystick)
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

#overwrite cmdline, for cleaner startup
cp -f /boot/pspi/configs/cmdline.txt /boot/cmdline.txt

#remove DHCP wait, for faster bootup
rm -f /etc/systemd/system/dhcpcd.service.d/wait.conf

#add custom startup image
cp -f /boot/pspi/theme/pspi.png /home/pi/RetroPie/splashscreens/pspi.png
cp -f /boot/pspi/theme/splashscreen.list /etc/splashscreen.list

#modify theme
#also, figure out how to change theme so the scrolling is instant instead of fade
#also, figure out how to set "power save mode" to Enhanced
rm -r /home/pi/.emulationstation/themes/carbon
cp -p -r -f  /boot/pspi/theme/themes/carbon /home/pi/.emulationstation/themes/carbon

#add pspi-simple theme (testing)
rm -r /home/pi/.emulationstation/themes/pspi-simple
cp -p -r -f  /boot/pspi/theme/themes/pspi-simple /home/pi/.emulationstation/themes/pspi-simple

#add WiFi options tand othermod menu
#change this so it asks whether you have a Zero W (or better yet, detects whether it's a Zero W), and doesn't WiFi files if the answer is no
cp -p -r -f  /boot/pspi/theme/scripts /home/pi/RetroPie/othermod
cp -f /boot/pspi/theme/es_systems.cfg /home/pi/.emulationstation/es_systems.cfg

read -rsp $'Press any key to reboot...\n' -n1 key
reboot

