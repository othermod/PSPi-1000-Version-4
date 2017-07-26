# PSPi Version 4 Software

https://discord.gg/aR5jzUY Version 4 discussion on Discord

**Project Features:**

ATmega (aka Arduino) is NOT used for buttons and joystick, meaning the USB is left available

ADS1015 for joystick and battery detection

MCP23017 for buttons

4.3" LCD, driven by GPIO using custom overlay

**In Progress*

Add code to joystick's python script to detect battery voltage.

**Goals:**

Integrate everything for buttons, joystick, and dimming into a single file

Have a battery meter in EmulationStation (maybe even within games?)

Improve audio quality in hardware and software. It currently uses an audio circuit similar to the Pi 2 (buffer-filter-amplifier).
