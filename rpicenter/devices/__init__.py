import RPi.GPIO as GPIO
import sys, os, glob, inspect, importlib, logging
import utils
from devices.device import Device

logger = logging.getLogger("rpicenter.devices")

class DeviceDispatcher:
    def __init__(self):
        self.__devices__ = {}
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
            self.__devices__.setdefault(device.device_object_id, [device, device.commands])
        return device

    def is_device_exists(self, device_object_id):
        if device_object_id is not None and self.__devices__.get(device_object_id, None) is not None:
            return True
        else:
            return False

    def run_command(self, device_object_id, method_name, param, *args, **kwargs):
        logger.debug("devices run command called: " + device_object_id)
        _result = None
        _device = self.get_device(str(device_object_id))
        if _device is not None: 
            try:     
                utils.run_hooks(self.__hooks__, "PRE_" + device_object_id + "." + method_name)        
                _func = getattr(_device, method_name, None)
                if _func is not None:
                    _result = eval('_func' + param)
                elif _device.is_local == False:
                    _result = _device.compose_message(method_name=method_name, param=param) 
                utils.run_hooks(self.__hooks__, "POST_" + device_object_id + "." + method_name)
            except Exception as ex:
                logger.error(ex, exc_info=True)
                _result = "Err: " + str(ex) 
                raise
        else: 
            _result = "Unable to find Device: " + device_object_id
        return _result

    def add_hook(self, key, func):
        self.__hooks__.update({key: func})
        return

    def get_device(self, device_object_id):    
        _device = self.__devices__.get(device_object_id, None)
        if _device is not None: 
            return _device[0]
        else: 
            return None

    def list_devices(self):
        _device_list = {}
        for key, d in self.__devices__.items():
            _device_list.update({key: d[1]})
        return _device_list

    def cleanup(self):        
        for key, d in self.__devices__.items():
            (d[0]).cleanup()
        self.__devices__ = None
        self.__hooks__ = None
        GPIO.cleanup()

# Create singleton
devices = DeviceDispatcher()

_plugins = glob.glob(os.path.join(os.path.dirname(__file__), "*.py"))
__all__ = [os.path.splitext(os.path.basename(f))[0] for f in _plugins
           if os.path.isfile(f) and not os.path.basename(f).startswith("_")]

from devices import *
