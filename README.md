# PSPi Version 4 Software

https://discord.gg/aR5jzUY Version 4 discussion on Discord

**Project Features:**

ATmega (aka Arduino) is NOT used for buttons and joystick, meaning the USB is left available

ADS1015 for joystick and battery detection

MCP23017 for buttons

4.3" LCD, driven by GPIO using custom RGB 565 overlay

Made for Pi Zero and Zero W, compatible with Pi 3

**Current Status**

Code is stable, tweaks and improvements will be added

**Installation Instructions for Offline Installation - Will be automated later**

Download repository, extract and copy all subfolders to the BOOT partition of a fresh RetroPie image. You must overwrite the original config.txt. Do not copy cmdline.txt yet.

Boot the PSPi with the SD card inserted, with a USB keyboard attached.

After Emulation Station loads, press F4 on the keyboard to exit to the command line.

*Type the following commands:*

sudo bash /boot/buttons/install.sh

sudo bash /boot/shutdown/install.sh

sudo bash /boot/battery/install.sh

sudo bash /boot/backlight/install.sh

sudo bash /boot/joystick/install.sh

cd /boot/uinput

sudo python setup.py install

sudo reboot