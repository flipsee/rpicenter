### Base Class for Sensors ###
from abc import ABCMeta, abstractmethod
import threading
import time

class Device(metaclass=ABCMeta):
    device_object_id = None
    gpio_pin = None
    location = None
    _interval = 3 #default 3S delay for Loop job
    _flagstop = False
    _hooks = None

    def __init__(self):
        print("DeviceObjID: {0}, Location: {1}, pin: {2} Initiated".format(str(self.device_object_id), str(self.location), str(self.gpio_pin)))

    @abstractmethod
    def _run_sensor(self, **kwargs):
        pass

    def run_sensor(self, **kwargs):
        if 'hooks' in kwargs:
            hooks = kwargs['hooks']
        else:
            hooks = self._hooks

        if (hooks != None):
            for hook in hooks:
                if hook[0] == "PRE": hook[1]()

        self._run_sensor(**kwargs)

        if (hooks != None):
            for hook in hooks:
                if hook[0] == "POST": hook[1]()
        return self

    def loop(self, **kwargs):
        counter = 0
        self._flagstop = False
        print("Reading Interval: " + str(self._interval))
        while counter <=3: #change to true, this only for testing.
            if self._flagstop: return
            self.run_sensor(**kwargs)
            counter += 1
            if self._flagstop: return
            time.sleep(self._interval)

    def loop_start(self, **kwargs):
        if 'interval' in kwargs:
            if kwargs['interval'] > 3 : self._interval = kwargs['interval']
        print("Device " + self.device_object_id + " Loop starting...")
        self.thread = threading.Thread(target=self.loop, kwargs=kwargs)
        if self.thread.isAlive() == False:
            self.thread.start()
        return self

    def loop_stop(self):
        print("Device " + self.device_object_id + " loop stoping...")
        self._flagstop = True
        return self
