from devices.device import Device, command
from datetime import datetime
import RPi.GPIO as GPIO
import threading, time

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
    def blink(self, repetition=3, interval=1):
        print("Device " + self.device_object_id + " Loop starting...")
        _repetition = repetition * 2
        self.thread = threading.Thread(target=self.__blink__, args=(_repetition,interval))
        if self.thread.isAlive() == False:
            self.thread.start()

    def __blink__(self, repetition, interval):
        _old_state = self.state
        self.__flagstop__ = False
        counter = 0
        while True:
            if counter >= repetition or self.__flagstop__: 
                self.__change_state__(_old_state) #assign old state
                return
            counter += 1
            self.toggle() 
            time.sleep(interval)
        return 
