# PSPi Version 4 Software

https://discord.gg/aR5jzUY Version 4 discussion on Discord

**Project Features:**

ADS1015 for joystick and battery detection

MCP23017 for buttons

4.3" LCD, driven by GPIO using custom RGB 565 overlay

Made for Pi Zero and Zero W, compatible with Pi 3 if modification is done

**Current Status**

Code is stable, tweaks and improvements will be added

**Installation Instructions for Offline Installation - This is gradually becoming more automated**

Download repository, extract and copy all subfolders to the BOOT partition of a fresh RetroPie image. You must overwrite the original config.txt

Boot the PSPi with the SD card inserted, with a USB keyboard attached.

After Emulation Station loads, press F4 on the keyboard to exit to the command line.

*Type the following command to install everything:*

sudo bash /boot/pspi/setup.sh

**Only do this next step if the buttons aren't working. It's integrated into the button installation script, so it shouldn't be needed.**

type sudo raspi-config

Select Interfacing Options

Select I2C

Select Yes and press enter

**To-Do List**

To see a list of areas where help is needed, check out https://github.com/othermod/PSPi-1000-Version-4/tree/master/experimental
