#from functools import wraps
import RPi.GPIO as GPIO
import sys, os, glob, inspect, importlib
import utils
from devices.device import Device

class DeviceDispatcher:
    def __init__(self):
        self.relay_channel = None
        self.__devices__ = {}
        self.__device_list__ = {}
        self.__hooks__ = {}

    def add_device(self, device_object_id=None, slot=None, gpio_pin=None, location=None, type=None, is_local=True, device=None):
        #print(str(locals()))
        if device is not None: 
            device = self.register_device(device)
        elif device_object_id is not None and slot is not None and location is not None and type is not None:
            _class = getattr(sys.modules[__name__ + "." + type.lower()], type)
            device = _class(device_object_id=device_object_id, slot=slot, location=location, gpio_pin=gpio_pin,is_local=is_local)
            device = self.register_device(device)
        return device

    def register_device(self, device=None):
        if isinstance(device, Device):
            self.__devices__.setdefault(device.device_object_id, device)
            self.__device_list__.setdefault(device.device_object_id, device.commands)
        return device

    def is_device_exists(self, device_object_id):
        if device_object_id is not None and self.__devices__.get(device_object_id, None) is not None:
            return True
        else:
            return False

    def run_command(self, device_object_id, method_name, param, *args, **kwargs):
        print("devices run command called")
        _result = None
        _device = self.get_device(str(device_object_id))
        if _device is not None: 
            if _device.is_local == True:
                try:     
                    utils.run_hooks(self.__hooks__, "PRE_" + device_object_id + "." + method_name)        
                    _result = eval('getattr(_device, method_name)' + param)
                    utils.run_hooks(self.__hooks__, "POST_" + device_object_id + "." + method_name)
                except Exception as ex:
                    print(str(ex))
                    _result = "Err: " + str(ex) 
            elif device.is_local == False:
                print("Remote Device")
                try:
                    utils.run_hooks(self.__hooks__, "PRE_" + device_object_id + "." + method_name)
                    _topic, _message = eval('getattr(_device, method_name)' + param)
                    self.relay_channel.publish_msg(topic=_topic, msg=_message)
                    utils.run_hooks(self.__hooks__, "POST_" + device_object_id + "." + method_name)
                except Exception as ex:
                    print(str(ex))
                    _result = "Err: " + str(ex)

                #_topic, _message = eval('getattr(_device, method_name)' + param)
                #_topic = _device.device_object_id + "/request/rpicenter/12345"
                #_message = method_name + param
        else: _result = "Unable to find Device: " + device_object_id
        return _result

    def add_hook(self, key, func):
        self.__hooks__.update({key: func})
        return

    def get_device(self, device_object_id):    
        return self.__devices__.get(device_object_id, None)

    def list_devices(self):
        return self.__device_list__

    def cleanup(self):        
        for key, d in self.__devices__.items():
            d.cleanup()
        self.__devices__ = None
        GPIO.cleanup()

# Create singleton
devices = DeviceDispatcher()

_plugins = glob.glob(os.path.join(os.path.dirname(__file__), "*.py"))
__all__ = [os.path.splitext(os.path.basename(f))[0] for f in _plugins
           if os.path.isfile(f) and not os.path.basename(f).startswith("_")]

from devices import *
