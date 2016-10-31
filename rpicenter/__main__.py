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

def insert_sample():
    db = rpicenterBL()
    try:
        with db.atomic() as txn:
            db.add_Device(DeviceObjectID="TempSensor", Slot="0", Location="Living Room", GPIOPin=5, Type="DHT", IsLocal=True)
            db.add_Device(DeviceObjectID="RedLed", Slot="1", Location="Living Room", GPIOPin=26, Type="Led", IsLocal=True)
            db.add_Device(DeviceObjectID="GreenLed", Slot="2", Location="Living Room", GPIOPin=19, Type="Led", IsLocal=True)
            db.add_Device(DeviceObjectID="BlueLed", Slot="3", Location="Living Room", GPIOPin=13, Type="Led", IsLocal=True)
            db.add_Device(DeviceObjectID="Display", Slot="4", Location="Living Room", GPIOPin=24, Type="Display", IsLocal=True)
    finally:
        db.close()
   

def load_devices():
    db = rpicenterBL()
    try:
        data = db.get_devices()

        if data.count() == 0:
            insert_sample()
            data = db.get_devices()

        print("=== Loading Devices-Start: " + str(data.count()) + " ===")
        for entry in data:
            print("Device:" + entry.DeviceObjectID)
            devices.register_device(device_object_id=entry.DeviceObjectID, slot=entry.Slot, gpio_pin=entry.GPIOPin, location=entry.Location, is_local=entry.IsLocal, type=entry.Type)
        print("=== Loading Devices-End ===")
    finally:
        db.close()

def main():
    try:        
        devices.gpio_setmode(GPIO.BCM) #change this to board.

        load_devices()    
        #dhtSensor = dev.register_device(device_object_id="DHT1", slot="0", location="Living Room", gpio_pin=5, type="DHT")
        #redLed = Led(device_object_id="Red-Led", slot="1", location="Living Room", gpio_pin=26)
        #dev.register_device(device=redLed)
        #greenLed = dev.register_device(device_object_id="Green-Led", slot="2", location="Living Room", gpio_pin=19, type ="Led")
        #blueLed =  dev.register_device(device_object_id="Blue-Led", slot="3", location="Living Room", gpio_pin=13, type="Led")
        #disp =  dev.register_device(device_object_id="Display", slot="4", location="Living Room", gpio_pin=24, type="Display")

        print("Registered Devices: " + str(devices._devices))

        redLed = devices.get_device("RedLed")
        print("Command in RedLed are: " + str(redLed.commands))
        redLed.on()
        time.sleep(2)
        redLed.off()        
        time.sleep(2)

        dhtSensor = devices.get_device("TempSensor")
        print("Command in dht are: " + str(dhtSensor.commands))
        print("Temperature@" + str(dhtSensor.location) + " is: " + str(dhtSensor.temperature()))

        disp = devices.get_device("Display")
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
