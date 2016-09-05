from Device import Device
from datetime import datetime
import RPi.GPIO as GPIO

class Led(Device):
    status = None
    laststatuschange = None

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        Device.__init__(self)

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.gpio_pin, GPIO.OUT)
        self.status = False
        GPIO.output(self.gpio_pin, self.status) # reset status

    def set_status(self, status=True):
        self.status = status
        GPIO.output(self.gpio_pin, self.status)
        self.laststatuschange = datetime.now()
        print("Last Led Status Change at {0}, Status = {1}, Pin= {2}".format(str(self.laststatuschange), str(self.status), str(self.gpio_pin)))
        return self
    
    def run_sensor(self, hooks=None):
        #lets blink this led.
        if self.status == True: #switch led status
            status = False
        else:
            status = True
        self.set_status(status)
        Device.run_sensor(self, hooks)
        return self


