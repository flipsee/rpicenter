from devices.device import Device, command
from datetime import datetime

""" RemoteDevice is used to wrap message relaying process to a remote device.
Q: - how should handle the msg relay and response?
i.e. rpicenter in the living room, esp8266 as a clock in room1
- esp8266 has temp sensor, led, display module, we want to be able to control these value from the rpicenter.
"""

class Remote(Device):
    def __init__(self, device_object_id, slot, gpio_pin, location, is_local=False):
        super(Remote,self).__init__(device_object_id, slot, gpio_pin, location, is_local)
        self.commands = "??"
    
    #def add_message(self, msg, on_response, on_expiry=None, expiry=5):
        

    #def relay_msg(self, msg):
    #    _topic = self.device_object_id + "/request/" + self.master_device_object_id + "/" + str(uuid.uuid4())
    #    remote_communication.publish_msg(topic=_topic, msg=msg)
       

