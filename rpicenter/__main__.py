import RPi.GPIO as GPIO
import threading, time
import config, ir, mqtt, devices
from devices import *

try:
    from .rpicenterModel import *
except SystemError:
    from rpicenterModel import *

#1. load all devices from db.
#2. load recipies.
#3. wait input.

def insert_sample():
    db = rpicenterBL()
    try:
        with db.atomic() as txn:
            db.add_Device(DeviceObjectID="TempSensor", Slot="0", Location="Living Room", GPIOPin=5, Type="DHT", IsLocal=True)
            db.add_Device(DeviceObjectID="RedLed", Slot="1", Location="Living Room", GPIOPin=26, Type="Led", IsLocal=True)
            db.add_Device(DeviceObjectID="GreenLed", Slot="2", Location="Living Room", GPIOPin=19, Type="Led", IsLocal=True)
            db.add_Device(DeviceObjectID="BlueLed", Slot="3", Location="Living Room", GPIOPin=13, Type="Led", IsLocal=True)
            db.add_Device(DeviceObjectID="Display", Slot="4", Location="Living Room", GPIOPin=24, Type="Display", IsLocal=True)
            db.add_Device(DeviceObjectID="Btn", Slot="5", Location="Living Room", GPIOPin=12, Type="Switch", IsLocal=True)
    finally:
        db.close()

def load_hooks():
    print("Adding Hooks")        
    RedLed = devices.get_device("RedLed")
    RedLed.add_hook("POST_on", "run_command('GreenLed.off')")
    RedLed.add_hook("POST_off", "run_command('GreenLed.on')")

    Btn = devices.get_device("Btn")
    Btn.add_callback(lambda: run_command('RedLed.toggle'))

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

def run_command(msg):
    #print("run_command: " + msg)
    result = ""
    try:
        _device = str(msg).split('.')
        _method = _device[1].split('(')

        device = devices.get_device(str(_device[0]))
        if device is not None:        
            _method_name = str(_method[0])
            try:     
                __run_hooks__(device.hooks, "PRE_" + _method_name)

                if len(_method) == 1:
                    result = eval('getattr(device, _method_name)()')
                else:
                    #print(str('getattr(device, _method_name)(' + _method[1]))
                    result = eval('getattr(device, _method_name)(' + _method[1])
                
                __run_hooks__(device.hooks, "POST_" + _method_name)
            except Exception as ex:
                print(str(ex))
                result = "Error calling: " + str(msg)
                
        else: result = "Unable to find Device: " + _device[0]
    except:
        result = "Invalid Message"
    finally:
        print(str(result))
    return result

def __run_hooks__(hooks, key, *args, **kwargs):
    if (hooks != None):
        for h_key, h_value in hooks.items():
            if h_key == key: eval(h_value)

def init():
    cfg = config.get_config()
    devices.gpio_setmode(eval("GPIO." + str(cfg["gpio_type"])))

def main():
    try:
        init()

        load_devices()
        load_hooks()

        ### Input Channels ###
        mqtt.add_callback(run_command)
        if mqtt.client is not None:
            #mqtt.client.loop_forever()
            console = threading.Thread(target=mqtt.client.loop_forever)
            console.daemon = True
            console.start()

        ir.add_callback(run_command)
        console = threading.Thread(target=ir.input_ir)
        console.daemon = True
        console.start()

        #console = threading.Thread(target=console_input)
        #console.daemon = True
        #console.start()
        
        console_input()
        ### Input Channels-End ###

    except KeyboardInterrupt:
        print("Shutdown requested...exiting") 
    finally:
        exit_handler(mqtt.client)

def console_input():
    print("Starting Console Input...")
    while True:
        usercmd = input("Enter command:\n")
        run_command(usercmd)

def exit_handler(mqtt_client):    
    print("App terminated, cleanup!")
    devices.cleanup()
    if mqtt_client is not None: mqtt_client.disconnect()

def list_devices():
    return devices.list_devices()


if __name__ == '__main__':    
    main()

