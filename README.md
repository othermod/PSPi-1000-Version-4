# PSPi Version 4 Software

https://discord.gg/aR5jzUY Version 4 discussion on Discord

**Project Features:**

ATmega (aka Arduino) is NOT used for buttons and joystick, meaning the USB is left available

ADS1015 for joystick and battery detection

MCP23017 for buttons

4.3" LCD, driven by GPIO using custom overlay

Compatibility with Pi Zero 

**In Progress:**

Add code to joystick's python script to detect battery voltage.

Integrate shutdown, joystick, LCD dimming, battery detection, into a single file. Buttons may be a separate file for simplicity.

**Goals and Help Needed:**

Have a battery meter in EmulationStation and games

Maintain Pi 3 software compatibility and work around Pi 3 defect (need to figure out how to use the I2C-0 bus from the camera connector)

