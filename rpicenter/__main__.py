import RPi.GPIO as GPIO
import threading, time
from input import mqtt, console, ir, webapi
import config, devices 
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
            db.add_Device(DeviceObjectID="Buzzer", Slot="6", Location="Living Room", GPIOPin=21, Type="Buzzer", IsLocal=True)
    finally:
        db.close()

def load_hooks():
    print("=== Adding Hooks ===")        
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
    except:
        print("Error loading Devices")
    finally:
        db.close()

def run_command(msg, input=None, requestID=None):
    #print("run_command: " + msg)
    result = ""
    try:
        cmd = str(msg)
        _classidx = cmd.find(".")
        _paramidx = cmd.find("(")

        _device_name = str(cmd[:_classidx])
        if _paramidx < 0: # means that it doesn't have any param 
            _method_name = str(cmd[(_classidx + 1):])
            _param = "()"
        else:
            _method_name = str(cmd[(_classidx + 1):_paramidx])
            _param = str(cmd[_paramidx:len(cmd)])
        
        device = devices.get_device(str(_device_name))
        if device is not None:        
            try:     
                __run_hooks__(device.hooks, "PRE_" + _method_name)
                
                result = eval('getattr(device, _method_name)' + _param)

                __run_hooks__(device.hooks, "POST_" + _method_name)

                #print("result: " + str(result))
                if input != None: input.reply(requestID=requestID, msg=result)
            
            except Exception as ex:
                print(str(ex))
                result = "Error calling: " + str(msg)
                
        else: result = "Unable to find Device: " + _device[0]
    except Exception as ex:
        print(str(ex))
        result = "Invalid Message"
    finally:
        return result
        #print(str(result))

def __run_hooks__(hooks, key, *args, **kwargs):
    if (hooks != None):
        for h_key, h_value in hooks.items():
            if h_key == key: eval(h_value)

def main():
    input_channel = []
    input_channel.append(mqtt(callback=run_command))
    input_channel.append(console(callback=run_command))
    input_channel.append(ir(callback=run_command))
    input_channel.append(webapi(callback=run_command))
    
    try:
        cfg = config.get_config()
        GPIO.setmode(eval("GPIO." + str(cfg["gpio_type"])))
        #devices.gpio_setmode(eval("GPIO." + str(cfg["gpio_type"])))

        load_devices()
        load_hooks()
        #load_recipies()

        ### Input Channels ###
        for input in input_channel:
            i = threading.Thread(target=input.run)
            i.daemon = True
            i.start()

        # the below is to suspend the thread so it will not quit
        while True:
            pass
    except KeyboardInterrupt:
        print("=== Shutdown requested! exiting ===") 
    finally:
        print("App terminated, cleanup...")
        for input in input_channel:
            input.cleanup()
        
        devices.cleanup()
        GPIO.cleanup()
        time.sleep(0.5)

def list_devices():
    return devices.list_devices()


if __name__ == '__main__':    
    main()

