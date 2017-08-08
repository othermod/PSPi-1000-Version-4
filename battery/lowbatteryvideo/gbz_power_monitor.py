#!/usr/bin/env python2.7
# date: 30/05/16
# author: Popcorn <abandonedemails@gmail.com> - Add "Sudomod" in the subject or your message will not be received
# version: 1.0a
# name: GBZ-Power-Monitor - a Power Management utility for the Gameboy Zero project
# description: a GPIO monitor that detects low battery and power switch status which provides a graceful shutdown facility
# source: https://github.com/Camble/GBZ-Power-Monitor_PB

import RPi.GPIO as GPIO
import os
import sys
import time

batteryGPIO    = 17  # GPIO 17/pin 0
powerGPIO      = 27  # GPIO 27/pin 2
sampleRate     = 0.1 # tenth of a second
batteryTimeout = 10  # 10 seconds
powerTimeout   = 1   # 1 second
shutdownVideo  = "~/GBZ-Power-Monitor_PB/lowbattshutdown.mp4" # use no space or non-alphanum characters
lowalertVideo  = "~/GBZ-Power-Monitor_PB/lowbattalert.mp4"    # use no space or non-alphanum characters
playerFlag     = 0

GPIO.setmode(GPIO.BCM)
GPIO.setup(batteryGPIO, GPIO.IN) # No pull_up_down for LBO with voltage clamped with diode
GPIO.setup(powerGPIO, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

def lowBattery(channel):
  #Checking for LED bounce for the duration of the battery Timeout
  for bounceSample in range(1, int(round(batteryTimeout / sampleRate))):
    time.sleep(sampleRate)

    if GPIO.input(batteryGPIO) is 1:
       break

  global playerFlag
  while playerFlag is 1:
    time.sleep(1)

  #If the LED is a solid condition, there will be no bounce.  Launch shutdown video and then gracefully shutdown
  if bounceSample is int(round(batteryTimeout / sampleRate)) - 1:
    playerFlag = 1
    os.system("/usr/bin/omxplayer --no-osd --layer 999999 " + shutdownVideo + " --alpha 180;")
    if GPIO.input(batteryGPIO) is 0:
      os.system("sudo shutdown -h now")
      playerFlag = 0
      sys.exit(0)

  #If the LED is a solid for more than 10% of the timeout, we know that the battery is getting low.  Launch the Low Battery alert.
  if bounceSample > int(round(batteryTimeout / sampleRate * 0.1)):
    playerFlag = 1
    os.system("/usr/bin/omxplayer --no-osd --layer 999999 " + lowalertVideo + " --alpha 160;")
    playerFlag = 0

    #Discovered a bug with the Python GPIO library and threaded events.  Need to unbind and rebind after a System Call or the program will crash
    GPIO.remove_event_detect(batteryGPIO)
    GPIO.add_event_detect(batteryGPIO, GPIO.BOTH, callback=lowBattery, bouncetime=300)

    #If we know the battery is low, we aggresively monitor the level to ensure we shutdown once the Power Timeout is exceeded.
    lowBattery(batteryGPIO)

def powerSwitch(channel):
  #Checking for LED bounce for the duration of the Power Timeout
  for bounceSample in range(1, int(round(powerTimeout / sampleRate))):
    time.sleep(sampleRate)

    if GPIO.input(powerGPIO) is 1:
       break

  if bounceSample is int(round(powerTimeout / sampleRate)) - 1:
      #When the Power Switch is placed in the off position with no bounce for the duration of the Power Timeout, we immediately shutdown
      os.system("sudo shutdown -h now")
      try:
         sys.stdout.close()
      except:
         pass
      try:
         sys.stderr.close()
      except:
         pass

      sys.exit(0)

def main():
  #if the Low Battery LED is active when the program launches, handle it
  if GPIO.input(batteryGPIO) is 0:
    lowBattery(batteryGPIO)

  #if the Power Switch is active when the program launches, handle it
  if GPIO.input(powerGPIO) is 0:
    powerSwitch(powerGPIO)

  #Add threaded event listeners for the Low Battery and Power Switch
  try:
    GPIO.remove_event_detect(batteryGPIO)
    GPIO.add_event_detect(batteryGPIO, GPIO.FALLING, callback=lowBattery, bouncetime=300)

    GPIO.remove_event_detect(powerGPIO)
    GPIO.add_event_detect(powerGPIO, GPIO.FALLING, callback=powerSwitch, bouncetime=300)
  except KeyboardInterrupt:
    GPIO.cleanup()

main()

#We make an endless loop so the threads running the GPIO events will always be listening, in the future we can add Battery Level monitoring here
while True:
  time.sleep(1)

GPIO.cleanup()
