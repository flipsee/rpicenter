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

    def run_sensor(self, hooks=None):
        self.lastreading = datetime.now()
        print("Getting Current Reading at {0}".format(str(self.lastreading)))
        self.humidity, self.temperature = Adafruit_DHT.read_retry(self.dhtsensortype, self.gpio_pin)
        #self.temperature = '{0:0.2f}C'.format(temperature)
        #self.humidity = '{0:0.2f}%'.format(humidity)
        Device.run_sensor(self, hooks)
        return self    
    
    def stop_loop(self):
        Device.stop_loop(self)
        print("Last Reading at " +  str(self.lastreading) + " Temperature " + str(self.temperature) + ", Humidity " + str(self.humidity))
