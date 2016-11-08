from . import Device, command, GPIO
from datetime import datetime
import inspect

class Switch(Device):
    def __init__(self, device_object_id, slot, gpio_pin, location, is_local=True):
        super(Switch, self).__init__(device_object_id, slot, gpio_pin, location, is_local)
        GPIO.setup(self.gpio_pin, GPIO.IN, GPIO.PUD_UP)
        GPIO.add_event_detect(self.gpio_pin, GPIO.RISING, callback=self.__state_changed__, bouncetime=300)
        self.__callbacks = []

    def get_state(self):
        return self.state

    def get_laststatechange(self):
        return self.laststatechange

    @command
    def add_callback(self, callback):
        #print(str(inspect.getsourcelines(callback)))
        #callback()
        self.__callbacks.append(callback)
        return self
        
    def __state_changed__(self, channel):
        if GPIO.input(self.gpio_pin) == GPIO.HIGH:
            self.state = True
        else:
            self.state = False

        print("Button State changed")
        self.laststatechange = datetime.now()
        
        if (self.__callbacks is not None):
            for cb in self.__callbacks:
                #print(str(inspect.getsourcelines(cb)))
                try:
                    cb()
                except Exception as ex:
                    print(str(ex))
