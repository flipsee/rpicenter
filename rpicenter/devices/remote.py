from devices.device import Device, command
from datetime import datetime
import uuid
import rpicenter

""" RemoteDevice is used to wrap message relaying process to a remote device.
Q: - how should handle the msg relay and response?
i.e. rpicenter in the living room, esp8266 as a clock in room1
- esp8266 has temp sensor, led, display module, we want to be able to control these value from the rpicenter.
"""

class Remote(Device):
    def __init__(self, device_object_id, slot, gpio_pin, location, is_local=False):
        super(Remote,self).__init__(device_object_id, slot, gpio_pin, location, is_local)
        self.master_device_object_id = rpicenter.rpic.device_name
        self.commands = "??"

    def compose_message(self, method_name, param):
        """ {ESP8266}/request/{RPiCenter}/{Date Time}/{Trx ID} """
        _topic = self.device_object_id + "/request/" + self.master_device_object_id + "/" + str(uuid.uuid4())
        _message = method_name + param
        return _topic, _message
        


