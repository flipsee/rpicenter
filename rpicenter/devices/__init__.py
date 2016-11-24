import RPi.GPIO as GPIO
from functools import wraps
import sys, os, glob, inspect
import importlib

_devices = {}
_devices_list = {}

### Class method wrapper ###
def command(func,*args, **kwargs):
    @wraps(func)
    def wrapper(*args, **kwargs):
        _result = None
        _device_object_id = ""

        if len(args) > 0 and isinstance(args[0], Device):
            self = args[0]
            _device_object_id = self.device_object_id + "."

        print("Running: " + _device_object_id + func.__name__)

        try:
            _result = func(*args, **kwargs)
        except exception as ex:
            _result = "ERR: " + str(ex)
        finally: 
            if _result == None:
                _result = _device_object_id + func.__name__ + ": " + "ACK"
            #print(str(_result))
            return _result
    return wrapper

class Device:
    def __init__(self, device_object_id, slot, gpio_pin, location, is_local=True):
        #print("Device init:" + str(device_object_id))
        self.__flagstop__ = False
        self.hooks = {}
        self.sub_devices = {}
        self.sub_devices_list = {}

        self.device_object_id = device_object_id
        self.slot = slot
        self.gpio_pin = gpio_pin
        self.location = location
        self.is_local = is_local
        self.commands = [method for method in dir(self) if callable(getattr(self, method)) and not method.startswith("__")]

    def add_hook(self, key, func):
        self.hooks.update({key: func})

    def __add_sub_device__(self, device_object_id=None, slot=None, gpio_pin=None, location=None, type=None, is_local=True, device=None):
        if device is not None:
            device = self.__register_device__(device)
        elif device_object_id is not None and slot is not None and location is not None and type is not None:
            _class = getattr(sys.modules[__name__ + "." + type.lower()], type)
            device = _class(device_object_id=device_object_id, slot=slot, location=location, gpio_pin=gpio_pin,is_local=is_local)
            device = self.__register_device__(device)
        return device

    def __register_device__(self, device=None):
        if isinstance(device, Device):
            self.sub_devices.setdefault(device.device_object_id, device)
            self.sub_devices_list.setdefault(device.device_object_id, device.commands)
        return device

    def is_sub_device_exists(self, device_object_id):
        result = False
        if device_object_id is not None:  
            if self.sub_devices.get(device_object_id, None) is not None:
                result = True
        return result

    def get_sub_device(self, device_object_id=None):
        if device_object_id is not None: return self.sub_devices.get(device_object_id, None)
        return None

    def cleanup(self):
        self.__flagstop__ = True
        for key, d in self.sub_devices.items():
            d.cleanup()
        self.sub_devices = []

    @command
    def get_commands(self):
        return self.commands

def cleanup():
    global _devices
    for key, d in _devices.items():
        d.cleanup()
    _devices = []
    GPIO.cleanup()

def register_device(device_object_id=None, slot=None, gpio_pin=None, location=None, type=None, is_local=True, device=None):
    #print(str(locals()))
    if device is not None: 
        device = __register_device__(device)
    elif device_object_id is not None and slot is not None and location is not None and type is not None:
        _class = getattr(sys.modules[__name__ + "." + type.lower()], type)
        device = _class(device_object_id=device_object_id, slot=slot, location=location, gpio_pin=gpio_pin,is_local=is_local)
        device = __register_device__(device)
    return device

def __register_device__(device=None):
    if isinstance(device, Device):
        _devices.setdefault(device.device_object_id, device)
        _devices_list.setdefault(device.device_object_id, device.commands)
    return device

def is_device_exists(device_object_id):
    result = False
    if device_object_id is not None:
        if _devices.get(device_object_id, None) is not None:
            result = True
    return result

def get_device(device_object_id=None):    
    if device_object_id is not None: return _devices.get(device_object_id, None)
    return None

def list_devices():
    return _devices_result


_plugins = glob.glob(os.path.join(os.path.dirname(__file__), "*.py"))
__all__ = [os.path.splitext(os.path.basename(f))[0] for f in _plugins
           if os.path.isfile(f) and not os.path.basename(f).startswith("_")]

