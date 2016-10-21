from rpicenter import Device
from datetime import datetime
import rpicenter

class Led(Device):
    def __init__(self, device_object_id, slot, gpio_pin, location, GPIO, is_local=True):
        #print("led init")
        super(Led, self).__init__(device_object_id, slot, gpio_pin, location, is_local)
        self.GPIO = GPIO
        self.status = False # reset status
        self.GPIO.setup(self.gpio_pin, self.GPIO.OUT)
        self.GPIO.output(self.gpio_pin, self.status)

    @rpicenter.command
    def on(self): 
        #print("on")
        self.status = True
        self.laststatuschange = datetime.now()
        self.GPIO.output(self.gpio_pin, self.status)
        return self
    
    @rpicenter.command
    def off(self):
        #print("off")
        self.status = False
        self.laststatuschange = datetime.now()
        self.GPIO.output(self.gpio_pin, self.status)
        return self    
    
