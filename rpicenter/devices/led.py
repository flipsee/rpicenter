from . import Device, command, GPIO
from datetime import datetime
import threading
#from rpicenter import Device
#import rpicenter

class Led(Device):
    def __init__(self, device_object_id, slot, gpio_pin, location, is_local=True):
        super(Led, self).__init__(device_object_id, slot, gpio_pin, location, is_local)
        GPIO.setup(self.gpio_pin, GPIO.OUT)
        self.__change_state__(False) #reset

    def get_state(self):
        return self.state

    def get_laststatechange(self):
        return self.laststatechange

    def __change_state__(self, state):
        self.state = state
        self.laststatechange = datetime.now()
        GPIO.output(self.gpio_pin, self.state)        

    @command
    def on(self): 
        #print("on")
        self.__change_state__(True)
        return self
    
    @command
    def off(self):
        #print("off")
        #self.state = False
        #self.laststatechange = datetime.now()
        #GPIO.output(self.gpio_pin, self.state)
        self.__change_state__(False)
        return self    
    
    @command
    def toggle(self):            
        if self.state:
            self.off()
        else:
            self.on()
        #self.__change_state__((not self.state))
        return self
        
    @command
    def blink(self, repetition, interval):
        print("Device " + self.device_object_id + " Loop starting...")
        self.thread = threading.Thread(target=self.__blink__, kwargs=kwargs)
        if self.thread.isAlive() == False:
            self.thread.start()
        return self

    def __blink__(self, repetition, interval):
        self.toggle() 
        counter = 0
        while counter < repetition:
            counter += 1
            time.sleep(interval)
        return self
