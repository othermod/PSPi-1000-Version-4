A total rewrite of this board's software is in progress, to make it work with the newest version of RetroPie and the Raspberry Pi Zero 2 W. Keep an eye on this page for updates.

### Progress for the original Raspberry Pi Zero:
- [x] Get the shutdown and automatic poweroff feature working on RetroPie v4.7.1
- [x] Write driver to read ADS1015
- [x] Write driver to read MCP23017
- [x] Create controller/joystick driver using the two ICs
- [x] Add battery charge/discharge detection to the controller driver
- [ ] Enable joystick on the controller driver
- [x] Add adjustment of display brightness using the Display button (currently just using a Python script)
- [x] Get PWM audio working
- [x] Configure controller buttons in EmulationStation
- [ ] Configure controller buttons in Retroarch and games

### Progress for the Raspberry Pi Zero 2 W (will bring everything over once the original Zero is working):
[ ] Install necessary updates and hacks to get PWM audio working on the new version of the OS
