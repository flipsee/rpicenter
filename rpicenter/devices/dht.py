from devices.device import Device, command
from datetime import datetime
import Adafruit_DHT #library for the the DHT sensor.

class DHT(Device):
    min_read_interval = 5 #5S    
    dhtsensors = { '11': Adafruit_DHT.DHT11,
                    '22': Adafruit_DHT.DHT22,
                    '2302': Adafruit_DHT.AM2302 }    

    def __init__(self, device_object_id, slot, gpio_pin, location, is_local=True):
        super(DHT,self).__init__(device_object_id, slot, gpio_pin, location, is_local)
        self._sensor_type = self.dhtsensors["11"]
        self._last_reading = datetime.min
        self._read_interval = self.min_read_interval

    @command
    def temperature(self):
        self.__run_sensor__()
        return self._temperature

    @command
    def humidity(self):
        self.__run_sensor__()
        return self._humidity

    def __run_sensor__(self):
        if (datetime.now() - self._last_reading).total_seconds() > self._read_interval:
            self._last_reading = datetime.now()
            self._humidity, self._temperature = Adafruit_DHT.read_retry(self._sensor_type, self.gpio_pin)
        return self 
