from Device import Device
from datetime import datetime
import Adafruit_DHT #library for the the DHT sensor.

class DHT(Device):
    temperature = None
    humidity = None
    lastreading = None

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        
        Device.__init__(self)
        self._interval = 5 # 5S delay for reading job

    def run_sensor(self):
        self.lastreading = datetime.now()
        print("Getting Current Reading at {0}".format(str(self.lastreading)))
        humidity, temperature = Adafruit_DHT.read_retry(Adafruit_DHT.DHT11, self.gpio_pin)
        self.temperature = '{0:0.2f}C'.format(temperature)
        self.humidity = '{0:0.2f}%'.format(humidity)
        return self    
    
    def stop_loop(self):
        Device.stop_loop(self)
        print("Last Reading at " +  str(self.lastreading) + " Temperature " + self.temperature+ ", Humidity " + self.humidity)
