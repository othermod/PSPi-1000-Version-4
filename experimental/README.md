# PSPi Version 4 Software To-Do List

https://discord.gg/aR5jzUY Version 4 discussion on Discord

**Joystick**

*Current Code*

The joystick is attached to an ADC chip called the ADS1015. A driver is running in the background at all times, writing the joystick values to /sys/class/hwmon/hwmon0/device/in4_input and in5_input. 
These values are then read using Python. The script polls both in4_input and in5_input every 50ms. It takes those values and modifies them slightly to improve joystick minimum and maximum positions, and then uses the uinput Python module to write those values to /dev/input/js0. 
The Python script is not very efficient, and constantly uses about 3-4% of the CPU on a Pi Zero when it reports every 50ms.

*Goal*

Integrate the joystick into retrogame, possibly using code similar to https://github.com/marqs85/gamecon_gpio_rpi/blob/master/gamecon_gpio_rpi-1.3/gamecon_gpio_rpi.c (or https://github.com/recalbox/mk_arcade_joystick_rpi, which is based off gamecon)
This should make it easier to create a virtual controller, and will make interaction with emulationstation and retroarch better.

**PWM Backlight**

*Current Code*

PiGPIO is being used for DMA timed PWM. This works perfectly but it requires that the daemon run constantly, and it constantly uses 5-7% of the CPU on the Pi Zero.

*Goal*

There are 3 different types of PWM available on the Raspberry Pi:
Software PWM
Hardware PWM on PWM0 or PWM1
DMA timed PWM

Software PWM (normally using RPi.GPIO) is very unstable and uses precious CPU cycles on the Pi Zero.
Hardware PWM is ideal and was originally intended to be used for the backlight. The problem is that the PWM audio driver interferes with it. Even when using single-channel audio on PWM0 (GPIO18) with the mono overlay, PWM1 (GPIO19) is initialized when audio is played.

That leaves DMA timed PWM. This is available in every GPIO pin and is accurate and efficient. PiGPIO (https://github.com/joan2937/pigpio), RPIO.GPIO (https://github.com/metachris/RPIO/blob/master/source/c_pwm/pwm.c), and servoblaster (https://github.com/richardghirst/PiBits/tree/master/ServoBlaster) all use it.
I hope to avoid the PiGPIO daemon entirely and use a combination of available code to adjust the PWM signal more efficiently, and possibly also add this to retrogame.