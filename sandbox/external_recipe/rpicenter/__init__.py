import RPi.GPIO as gpio
from functools import wraps
import os, glob, asyncio

class Device:
    def __init__(self, device_object_id, slot, gpio_pin, location, is_local=True):
        #print("Device init:" + str(device_object_id))
        self.device_object_id = device_object_id
        self.slot = slot
        self.gpio_pin = gpio_pin
        self.location = location
        self.is_local = is_local
        self.commands = [method for method in dir(self) if callable(getattr(self, method)) and not method.startswith("__")]

    #def command(func):
    #    print("decorating: " + func.__name__)
    #    Device.commands.append(func.__name__)
    #    @wraps(func)
    #    def wrapper(*args, **kwargs):
    #        print("Running: " + func.__name__)
    #        #return asyncio.coroutine(func(*args, **kwargs))
    #        return func(*args, **kwargs)
    #    return wrapper

_devices = [] #type:Device[]

def command(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        print("Running: " + func.__name__)
        #return asyncio.coroutine(func(self, *args, **kwargs))
        return func(self,*args, **kwargs)
    return wrapper

def reg_device(device):
    for d in _devices:
        if id(d) == id(device):
            raise Exception('Device is already registered')
    _devices.append(device)

def cleanup():
    _devices = []
    gpio.cleanup()
