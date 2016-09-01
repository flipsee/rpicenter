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

    def __init__(self):
        print("DeviceObjID: {0}, Location: {1}, pin: {2} Initiated".format(str(self.device_object_id), str(self.location), str(self.gpio_pin)))

    @abstractmethod
    def run_sensor(self):
        pass

    def loop(self):
        counter = 0
        self._flagstop = False
        print("Reading Interval: " + str(self._interval))
        while counter <=3: #change to true, this only for testing.
            if self._flagstop: return
            self.run_sensor()
            counter += 1
            if self._flagstop: return
            time.sleep(self._interval)

    def start_loop(self, interval=0):
        if interval > 0: self._interval = interval
        print("Device " + self.device_object_id + " Loop starting...")
        self.thread = threading.Thread(target=self.loop)
        if self.thread.isAlive() == False:
            self.thread.start()
        return self

    def stop_loop(self):
        print("Device " + self.device_object_id + " loop stoping...")
        self._flagstop = True
        return self
