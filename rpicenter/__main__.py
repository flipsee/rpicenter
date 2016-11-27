import RPi.GPIO as GPIO
import threading, time, inspect
import config, devices 
from functools import wraps
from rpicenterModel import *
from input import mqtt, console, ir, webapi
import devices

#1. load all devices from db.
#2. load recipies.
#3. wait input.
remote_communication = None
public_commands = {}

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
            db.add_Device(DeviceObjectID="Remote1", Slot="1", Location="Main Bed Room", GPIOPin=0, Type="Remote", IsLocal=False)
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
    except Exception as ex:
        print("Error loading Devices: " + str(ex))
    finally:
        db.close()

def run_command(msg, input=None, requestID=None):
    #print("run_command: " + msg)
    result = ""
    try:
        _device_name, _method_name, _param = __parse_input__(str(msg))
        print(str(_device_name) + " : " + _method_name + " : " + _param)

        ### call the public method ###
        if _device_name == None:
            try:
                if public_commands.get(_method_name, None) != None:
                    print("Running Public Command")
                    result = eval(_method_name + _param)
                    if input != None: input.reply(requestID=requestID, msg=result)
                else: result = "Unknown Command! "
            except KeyError:
                result = "Unknown Command! "
            return result

        ### call the devices method ###
        device = devices.get_device(str(_device_name))
        #print(str(device) + ":"+ device.is_local)

        #is local device
        if device is not None and device.is_local == True:        
            try:     
                __run_hooks__(device.hooks, "PRE_" + _method_name)
                
                result = eval('getattr(device, _method_name)' + _param)

                __run_hooks__(device.hooks, "POST_" + _method_name)

                #print("result: " + str(result))
                if input != None: input.reply(requestID=requestID, msg=result)            
            except Exception as ex:
                print(str(ex))
                result = "Error calling: " + str(msg)

        #is a remote device
        elif device is not None and device.is_local == False:
            print("Remote Device")
            _topic = "esp8266/request/rpicenter/12345"
            _message = _method_name + _param
            remote_communication.publish_msg(topic=_topic, msg=_message)

        #not a device, error!!!
        else: result = "Unable to find Device: " + _device_name
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

def __parse_input__(msg=None):
    _device_name = None
    _method_Name = None
    _param = None
    if msg is not None:
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
        #print(_device_name + " : " + _method_name + " : " + _param)
        if _classidx < 0 or (_paramidx >= 0 and _paramidx < _classidx): _device_name = None
    return _device_name, _method_name, _param

def main():
    remote_communication = mqtt(callback=run_command) # we will use this to communicate with remote device also.

    input_channel = []
    #input_channel.append(ir(callback=run_command))
    input_channel.append(remote_communication)
    #input_channel.append(webapi(callback=run_command))
    input_channel.append(console(callback=run_command))
    
    try:
        cfg = config.get_config()
        GPIO.setmode(eval("GPIO." + str(cfg["gpio_type"])))
        GPIO.setwarnings(False)
        #devices.gpio_setmode(eval("GPIO." + str(cfg["gpio_type"])))

        load_devices()
        load_hooks()
        #load_recipies()
        print(str(list_devices))

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


### decorator ###
def public_command(func, *args, **kwargs):
    """this is a Decorator to register methods that can be called in run_command\call$
    """
    #print("Registering Public Command: " + func.__name__ + " Doc: " + str(func.__doc$
    public_commands[func.__name__] = str(func.__doc__)
    @wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper

### public command that can be called by the user. ###
@public_command
@devices.command
def list_devices(msg=None):
    """ list devices in RPICenter"""
    if msg is not None: print("Msg: " + str(msg))
    for key, value in devices.list_devices().items():
        print("Key: " + key + " Value: " + str(value))
    return devices.list_devices()

@public_command
@devices.command
def list_commands():
    print("i'm here")
    return public_commands

@public_command
@devices.command
def show_temp_to_screen():
    """ get the temperature and display on screen """
    temp = run_command("TempSensor.temperature")
    run_command("Display.show_message('" + str(temp) + "')")    
        

if __name__ == '__main__':    
    main()

