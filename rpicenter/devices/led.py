from . import Device, command, GPIO
from datetime import datetime
import threading

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
        self.__change_state__(True)
    
    @command
    def off(self):
        self.__change_state__(False)
    
    @command
    def toggle(self):            
        if self.state:
            self.off()
        else:
            self.on()
        
    @command
    def blink(self, repetition, interval):
        print("Device " + self.device_object_id + " Loop starting...")
        self.thread = threading.Thread(target=self.__blink__, kwargs=kwargs)
        if self.thread.isAlive() == False:
            self.thread.start()

    def __blink__(self, repetition, interval):
        self.__flagstop__ = False
        counter = 0
        while counter < repetition:
            if self.__flagstop__: return
            counter += 1
            self.toggle() 
            time.sleep(interval)
        return 
