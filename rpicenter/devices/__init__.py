import RPi.GPIO as GPIO
from functools import wraps
import sys, os, glob
import importlib

class Device:
    def __init__(self, device_object_id, slot, gpio_pin, location, is_local=True):
        #print("Device init:" + str(device_object_id))
        self.device_object_id = device_object_id
        self.slot = slot
        self.gpio_pin = gpio_pin
        self.location = location
        self.is_local = is_local
        self.commands = [method for method in dir(self) if callable(getattr(self, method)) and not method.startswith("__")]
        self.hooks = {}

    def add_hook(self, key, func):
        self.hooks.update({key: func})

    def cleanup(self):
        pass


GPIO = GPIO
_devices = [] #type:Device[]


def command(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        _result = None
        print("Running: " + self.device_object_id + "." +  func.__name__)
        #return asyncio.coroutine(func(self, *args, **kwargs))
        _result = func(self,*args, **kwargs)
        return _result
    return wrapper

def cleanup():
    global _devices
    for d in _devices:
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
        if not is_device_exists(device):
            _devices.append(device)
    return device

def is_device_exists(device):
    for d in _devices:
        if d.device_object_id == device.device_object_id:
            return True
    return False

def gpio_setmode(gpio_mode):
    GPIO.setmode(gpio_mode)

def get_device(device_object_id=None):    
    for d in _devices:
        if d.device_object_id == device_object_id:
            return d
    return None

def list_devices():
    _result = {}
    for d in _devices:
        _result[d.device_object_id] = d.commands
    return _result

_plugins = glob.glob(os.path.join(os.path.dirname(__file__), "*.py"))
__all__ = [os.path.splitext(os.path.basename(f))[0] for f in _plugins
           if os.path.isfile(f) and not os.path.basename(f).startswith("_")]

