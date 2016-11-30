from datetime import datetime
from devices.device import Device, command
import input, rpicenter

""" RemoteDevice is used to wrap message relaying process to a remote device.
Q: - how should handle the msg relay and response?
i.e. rpicenter in the living room, esp8266 as a clock in room1
- esp8266 has temp sensor, led, display module, we want to be able to control these value from the rpicenter.
"""

class Remote(Device):
    def __init__(self, device_object_id, slot, gpio_pin, location, is_local=False):
        super(Remote,self).__init__(device_object_id, slot, gpio_pin, location, is_local)
        self.master_device_object_id = rpicenter.rpicenter.device_name
        self.commands = None

    def set_value(self, message):
        _variable_name = None

        if message.msg == 'get_commands()': _variable_name = 'commands'

        setattr(self, _variable_name, message.response)
    
    def compose_message(self, method_name, param, on_response=None, on_expiry=None):
        _message = method_name + param
        _msgQueue = input.Message(msg=_message, sender=self.master_device_object_id, receiver=self.device_object_id, on_response=on_response, on_expiry=on_expiry)
        return _msgQueue
    
    def get_commands(self):
        if self.commands == None:
            return self.compose_message("get_commands", "()", self.set_value)
        else:
            return self.commands

