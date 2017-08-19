
# Dependancies

The scripts use the following (install in this order):

* python-smbus
* python-uinput
* I2C must be enabled - using `raspi-config` or add 'i2c_bcm2708', 'i2c_dev' to
  '/etc/modules'.

# Install/Run


sudo python digitalJoy.py &


# Mapping

If you want to change the button mapping, open the script (`nano digitalJoy.py`)
navigate to the 'buttons' **dictionary**. The **key** (LH) is the BCM GPIO pin
and the **value** (RH) is the key to emulate upon press event. For example, to
map 17 to spacebar:

```python
17: uinput.KEY_SPACE
```

