import RPi.GPIO as GPIO
from datetime import datetime
from devices.device import Device, command
import rpicenter

class Switch(Device):
    def __init__(self, device_object_id, slot, gpio_pin, location, is_local=True):
        self._state = False
        self._last_state_changed = datetime.min
        self.__callbacks = []

        super(Switch, self).__init__(device_object_id, slot, gpio_pin, location, is_local)
        GPIO.setup(self.gpio_pin, GPIO.IN, GPIO.PUD_UP)
        GPIO.add_event_detect(self.gpio_pin, GPIO.RISING, callback=self.__state_changed__, bouncetime=300)
        self.__read_state__()

    @command
    def state(self):
        return self._state

    @command
    def last_state_changed(self):
        return self._last_state_changed

    @command
    def add_callback(self, callback):
        self.__callbacks.append(callback)
        
    def __read_state__(self):
        if GPIO.input(self.gpio_pin) == GPIO.HIGH:
            self._state = True
        else:
            self._state = False

    def __state_changed__(self, channel):
        run_command = rpicenter.run_command
        self.__read_state__()
        print("Button State changed")
        self._last_state_changed = datetime.now()
        
        if (self.__callbacks is not None):
            for cb in self.__callbacks:
                try:
                    cb()
                except Exception as ex:
                    print(str(ex))
