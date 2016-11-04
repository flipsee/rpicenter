import configparser
import paho.mqtt.client as mqtt
import RPi.GPIO as GPIO
import time

try:
    from .rpicenterModel import *
except SystemError:
    from rpicenterModel import *

import devices
from devices import *

#1. load all devices from db.
#2. load recipies.
#3. wait input.

mqtt_client = None
mqtt_client_topic = None
curr_class = None

def insert_sample():
    db = rpicenterBL()
    try:
        with db.atomic() as txn:
            db.add_Device(DeviceObjectID="TempSensor", Slot="0", Location="Living Room", GPIOPin=5, Type="DHT", IsLocal=True)
            db.add_Device(DeviceObjectID="RedLed", Slot="1", Location="Living Room", GPIOPin=26, Type="Led", IsLocal=True)
            db.add_Device(DeviceObjectID="GreenLed", Slot="2", Location="Living Room", GPIOPin=19, Type="Led", IsLocal=True)
            db.add_Device(DeviceObjectID="BlueLed", Slot="3", Location="Living Room", GPIOPin=13, Type="Led", IsLocal=True)
            db.add_Device(DeviceObjectID="Display", Slot="4", Location="Living Room", GPIOPin=24, Type="Display", IsLocal=True)

            #db.add_Device(DeviceObjectID="Button1", Slot="5", Location="Living Room", GPIOPin=24, Type="Display", IsLocal=True)
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

def send_message(topic, message):
    global mqtt_client
    mqtt_client.publish(topic, message)

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    global mqtt_client_topic
    client.subscribe(mqtt_client_topic)

def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))
    _msg = msg.payload.decode(encoding="utf-8", errors="ignore")
    run_command(_msg)

def run_command(msg):
    print(msg)
    result = ""
    try:
        _device = str(msg).split('.')
        _method = _device[1].split('(')

        device = devices.get_device(str(_device[0]))
        if device is not None:        
            try:     
                if _method.count() == 1:
                    result = eval('getattr(device, str(_method[0]))()')
                else:
                    temp = 'getattr(device, str(_method[0]))(' + _method[1]
                    print(str(temp))
                    result = eval('getattr(device, str(_method[0]))(' + _method[1])
            except:
                result = "Error calling: " + str(msg)
        else: result = "Unable to find Device: " + _device[0]
    except:
        result = "Invalid Message"
    finally:
        print(result)
    return result

def main():
    global mqtt_client
    try:
        load_devices()
        if mqtt_client is not None:
            mqtt_client.loop_forever()
        else:
            while True:
                usercmd = input("Enter command\n")
                run_command(usercmd)
    except KeyboardInterrupt:
        print("Shutdown requested...exiting") 
    finally:
        exit_handler(mqtt_client)

def exit_handler(mqtt_client):    
    print("App terminated, cleanup!")
    devices.cleanup()
    if mqtt_client is not None: mqtt_client.disconnect()

def list_devices():
    return devices.list_devices()

def test():
    try:        
        load_devices()    
        #dhtSensor = dev.register_device(device_object_id="DHT1", slot="0", location="Living Room", gpio_pin=5, type="DHT")
        #redLed = Led(device_object_id="Red-Led", slot="1", location="Living Room", gpio_pin=26)
        #dev.register_device(device=redLed)
        #greenLed = dev.register_device(device_object_id="Green-Led", slot="2", location="Living Room", gpio_pin=19, type ="Led")
        #blueLed =  dev.register_device(device_object_id="Blue-Led", slot="3", location="Living Room", gpio_pin=13, type="Led")
        #disp =  dev.register_device(device_object_id="Display", slot="4", location="Living Room", gpio_pin=24, type="Display")

        print("List Devices: ")
        for key, value in devices.list_devices().items():
            print(key + ": " + str(value))

        redLed = devices.get_device("RedLed")
        redLed.on()
        time.sleep(2)
        redLed.off()        
        time.sleep(2)

        dhtSensor = devices.get_device("TempSensor")
        print("Temperature@" + str(dhtSensor.location) + " is: " + str(dhtSensor.temperature()))

        disp = devices.get_device("Display")
        disp.show_message("happycat_oled_64.ppm")
        time.sleep(5)
    except KeyboardInterrupt:
        print("Shutdown requested...exiting")
    finally:
        exit_handler()

def innit():
    cfg = configparser.ConfigParser()
    configname = 'rpicenter.conf'
    if os.path.exists(configname): #check the config file in the caller path
        cfg.read(configname)
    else: #if not found check the config in the source path
        cfg.read(os.path.join(os.path.abspath(os.path.dirname(__file__)),configname))

    config = cfg["DEFAULT"]

    devices.gpio_setmode(eval("GPIO." + str(config["gpio_type"])))

    global mqtt_client
    global mqtt_client_topic

    if config["mqtt_server"] is not None:
        mqtt_client = None #mqtt.Client()
        #mqtt_client.on_connect = on_connect
        #mqtt_client.on_message = on_message
        #mqtt_client_topic = config["mqtt_topic"]
        #mqtt_client.connect(str(config["mqtt_server"]), int(config["mqtt_port"]), 60)

if __name__ == '__main__':    
    innit()
    main()
    #test()

