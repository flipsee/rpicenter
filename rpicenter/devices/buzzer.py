from . import Device, command
import time
import RPi.GPIO as GPIO

class Buzzer(Device):
    def __init__(self, device_object_id, slot, gpio_pin, location, is_local=True):
        super(Buzzer,self).__init__(device_object_id, slot, gpio_pin, location, is_local)
        GPIO.setup(self.gpio_pin, GPIO.OUT)

    @command
    def buzz(self, duration=0.25):
        GPIO.output(self.gpio_pin, True)
        time.sleep(duration)
        GPIO.output(self.gpio_pin, False)        

#pin = 21
#GPIO.cleanup()
#GPIO.setmode(GPIO.BCM)
#GPIO.setup(pin, GPIO.OUT)

#while True:
#    print("True")
#    GPIO.output(pin, True)
#    time.sleep(2)
#    print("False")
#    GPIO.output(pin, False)
#    time.sleep(2)

