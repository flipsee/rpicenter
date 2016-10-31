import RPi.GPIO as GPIO
import time

try:
    from .rpicenterModel import *
except SystemError:
    from rpicenterModel import *

import devices
from devices.dht import DHT
from devices.led import Led
from devices.display import Display

#1. import all Devices.
#2. load all devices from db.
#3. load recipies.
#.wait input.


def main():
    try:
        devices.gpio_setmode(GPIO.BCM)
        
        print("--- Loading Devices ---")
        dhtSensor = devices.register_device(device_object_id="DHT1", slot="0", location="Living Room", gpio_pin=5, type="DHT")
        redLed = Led(device_object_id="Red-Led", slot="1", location="Living Room", gpio_pin=26)
        devices.register_device(device=redLed)
       
        greenLed = devices.register_device(device_object_id="Green-Led", slot="2", location="Living Room", gpio_pin=19, type ="Led")
        blueLed =  devices.register_device(device_object_id="Blue-Led", slot="3", location="Living Room", gpio_pin=13, type="Led")
        disp =  devices.register_device(device_object_id="Display", slot="4", location="Living Room", gpio_pin=24, type="Display")

        print(str(devices._devices))
        print("Command in RedLed are: " + str(redLed.commands))
        redLed.on()
        time.sleep(2)
        redLed.off()        
        time.sleep(2)
        print("Command in dht are: " + str(dhtSensor.commands))
        print("Temperature@" + str(dhtSensor.location) + " is: " + str(dhtSensor.temperature()))

        disp.show_message("happycat_oled_64.ppm")
        time.sleep(5)

    except KeyboardInterrupt:
        print("Shutdown requested...exiting")
    finally:
        exit_handler()

def exit_handler():    
    print("App terminated, cleanup!")
    devices.cleanup()

if __name__ == '__main__':
    main()
