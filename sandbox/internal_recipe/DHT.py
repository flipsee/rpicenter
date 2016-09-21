from Device import Device
from datetime import datetime
import Adafruit_DHT #library for the the DHT sensor.

class DHT(Device):
    dhtsensors = { '11': Adafruit_DHT.DHT11,
                    '22': Adafruit_DHT.DHT22,
                    '2302': Adafruit_DHT.AM2302 }
    dhtsensortype = None
    temperature = None
    humidity = None
    lastreading = None

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)        
        Device.__init__(self)
        self._interval = 5 # 5S delay for reading job
        self.dhtsensortype = self.dhtsensors["11"]

    def _run_sensor(self, **kwargs):
        self.lastreading = datetime.now()
        print("{0} Reading at {1}".format(str(self.device_object_id), str(self.lastreading)))
        self.humidity, self.temperature = Adafruit_DHT.read_retry(self.dhtsensortype, self.gpio_pin)
        return self    
    
    def loop_stop(self):
        Device.loop_stop(self)
        print("Last Reading at " +  str(self.lastreading) + " Temperature " + str(self.temperature) + ", Humidity " + str(self.humidity))
        return self
