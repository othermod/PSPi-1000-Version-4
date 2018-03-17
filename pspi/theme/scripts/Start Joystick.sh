#!/bin/bash

#first kill joystick if already running
sudo pkill -f joystick.py
sudo python /boot/pspi/joystick.py &