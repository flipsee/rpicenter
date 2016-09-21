from Device import Device
from datetime import datetime
#import RPi.GPIO as GPIO

class Led(Device):
    status = None
    laststatuschange = None
    GPIO = None

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        Device.__init__(self)
        self.status = False
        self.GPIO.setup(self.gpio_pin, self.GPIO.OUT)
        self.GPIO.output(self.gpio_pin, self.status) # reset status

    def set_status(self, **kwargs): #call here without trigger the hooks
        if 'status' in kwargs:
            self.status = kwargs['status']
        else:
            self.status = True    
        self.GPIO.output(self.gpio_pin, self.status)
        self.laststatuschange = datetime.now()
        print("{0} Status Change at {1}, Status = {2}, Pin= {3}".format(str(self.device_object_id), str(self.laststatuschange), str(self.status), str(self.gpio_pin)))
        return self
    
    def _run_sensor(self, **kwargs):
        #if status is not given, lets switch this led.
        if 'status' in kwargs:
            self.status = kwargs['status']
        else:
            self.status = not(self.status)
        self.GPIO.output(self.gpio_pin, self.status)
        self.laststatuschange = datetime.now()
        print("{0} Status Change at {1}, Status = {2}, Pin= {3}".format(str(self.device_object_id),str(self.laststatuschange), str(self.status), str(self.gpio_pin)))
        return self


