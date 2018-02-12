# PSPi Version 4 Software To-Do List

https://discord.gg/aR5jzUY Version 4 discussion on Discord

**Joystick**

*Current Code*

The joystick is attached to an ADC chip called the ADS1015. A driver is running in the background at all times, writing the joystick values to /sys/class/hwmon/hwmon0/device/in4_input and in5_input. 
These values are then read using Python. The script polls both in4_input and in5_input every 50ms. It takes those values and modifies them slightly to improve joystick minimum and maximum positions, and then uses the uinput Python module to write those values to /dev/input/js0. 
The Python script is not very efficient, and constantly uses about 3-4% of the CPU on a Pi Zero when it reports every 50ms.

*Goal*

Create a joystick driver, possibly using code similar to https://github.com/marqs85/gamecon_gpio_rpi/blob/master/gamecon_gpio_rpi-1.3/gamecon_gpio_rpi.c (or https://github.com/recalbox/mk_arcade_joystick_rpi, which is based off gamecon)
This should make it easier to create a virtual controller, and make interaction with emulationstation and retroarch better.

**PWM Backlight**

*Current Code*

At the moment pi-baster (which is a slightly modified version of servoblaster) is used to generate DMA/PCM timed PWM on GPIO 19

*Goal*

Simplify the code to suite this project.