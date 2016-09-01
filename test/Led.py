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

    def run_sensor(self):
        #lets blink this led.
        if self.status == True: #switch led status
            self.status = False
        else:
            self.status = True

        GPIO.output(self.gpio_pin, self.status)
        self.laststatuschange = datetime.now()
        print("Last Led Status Change at {0}, Status = {1}".format(str(self.laststatuschange), str(self.status)))
        return self
