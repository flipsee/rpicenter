from devices.device import Device, command
import utils
import logging
import RPi.GPIO as GPIO
from datetime import datetime

logger = logging.getLogger("rpicenter.devices.switch")

class Switch(Device):
    def __init__(self, device_object_id, slot, gpio_pin, location, is_local=True):
        self.__state__ = False
        self.__last_state_changed__ = datetime.min
        self.__callbacks__ = []

        super(Switch, self).__init__(device_object_id, slot, gpio_pin, location, is_local)
        GPIO.setup(self.gpio_pin, GPIO.IN, GPIO.PUD_UP)
        GPIO.add_event_detect(self.gpio_pin, GPIO.RISING, callback=self.__state_changed__, bouncetime=300)
        self.__read_state__()

    @command
    def state(self):
        return self.__state__

    @command
    def last_state_changed(self):
        return self.__last_state_changed__

    @command
    def add_callback(self, callback):
        self.__callbacks__.append(callback)

    @command
    def run_callback(self):
        self.__last_state_changed__ = datetime.now()
        utils.run_hooks(self.__callbacks__)

    def __read_state__(self):
        if GPIO.input(self.gpio_pin) == GPIO.HIGH:
            self.__state__ = True
        else:
            self.__state__ = False

    def __state_changed__(self, channel):
        self.__read_state__()
        logger.debug("Button State changed, New State: " + str(self.__state__))
        self.__last_state_changed__ = datetime.now()
        utils.run_hooks(self.__callbacks__)
