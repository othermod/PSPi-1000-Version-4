#!/usr/bin/python
import RPi.GPIO as GPIO
import time
from time import localtime, strftime
import array
import os
import math

from config import *
from mcp3008 import *



print("Batteries 100% voltage:      " + str(VOLT100))
print("Batteries 75% voltage:       " + str(VOLT75))
print("Batteries 50% voltage:       " + str(VOLT50))
print("Batteries 25% voltage:       " + str(VOLT25))
print("Batteries dangerous voltage: " + str(VOLT0))
print("ADC 100% value:              " + str(ADC100))
print("ADC 75% value:               " + str(ADC75))
print("ADC 50% value:               " + str(ADC50))
print("ADC 25% value:               " + str(ADC25))
print("ADC dangerous voltage value: " + str(ADC0))
print(" ")
print("Time           ADC          Volt")
while True:
    ret1 = readadc(ADCCHANNEL, SPICLK, SPIMOSI, SPIMISO, SPICS)
    time.sleep(3)
    ret2 = readadc(ADCCHANNEL, SPICLK, SPIMOSI, SPIMISO, SPICS)
    time.sleep(3)
    ret3 = readadc(ADCCHANNEL, SPICLK, SPIMOSI, SPIMISO, SPICS)
    ret = ret1 + ret2 + ret3
    ret = ret/3
    print(strftime("%H:%M", localtime()) + "          " + str(ret) + "          " + str(((HIGHRESVAL+LOWRESVAL)*ret*(ADCVREF/1024))/HIGHRESVAL))

    time.sleep(170)

