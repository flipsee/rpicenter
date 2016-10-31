from . import Device, command, GPIO
from datetime import datetime
#from rpicenter import Device
#import rpicenter

class Led(Device):
    def __init__(self, device_object_id, slot, gpio_pin, location, is_local=True):
        super(Led, self).__init__(device_object_id, slot, gpio_pin, location, is_local)
        GPIO.setup(self.gpio_pin, GPIO.OUT)
        self.off() #reset

    @command
    def on(self): 
        #print("on")
        self.status = True
        self.laststatuschange = datetime.now()
        GPIO.output(self.gpio_pin, self.status)
        return self
    
    @command
    def off(self):
        #print("off")
        self.status = False
        self.laststatuschange = datetime.now()
        GPIO.output(self.gpio_pin, self.status)
        return self    
    
