from devices.device import Device, command
import time
import RPi.GPIO as GPIO
import threading

class Buzzer(Device):
    def __init__(self, device_object_id, slot, gpio_pin, location, is_local=True):
        super(Buzzer, self).__init__(device_object_id, slot, gpio_pin, location, is_local)
        GPIO.setup(self.gpio_pin, GPIO.OUT)

    def __beep__(self, cycles=1, delay=0.5):
        self.__flagstop__ = False
        counter = 0
        while counter < cycles:
            if self.__flagstop__: return
            counter += 1

            GPIO.output(self.gpio_pin, True)
            time.sleep(delay)

            GPIO.output(self.gpio_pin, False)        
            time.sleep(delay)
        return

    @command
    def beep(self, cycles=1, delay=0.5):
        self.thread = threading.Thread(target=self.__beep__, args=(cycles, delay))
        if self.thread.isAlive() == False:
            self.thread.start()

    @command
    def play(self, pitches=[], durations=[]):
        for x in range(0, max(len(pitches), len(durations))):
            if x < len(pitches): 
                pitch = pitches[x] 
            else:
                pitch = 0
            
            if x < len(durations):
                duration = durations[x]
            else:
                duration = 0

            self.buzz(pitch, duration) #feed the pitch and duration to the function, “buzz”
            time.sleep(duration * 0.5)

    @command
    def buzz(self, pitch=0, duration=0): #create the function “buzz” and feed it the pitch and duration)
        if pitch == 0:
            time.sleep(duration)
            return

        if duration == 0: return

        period = 1.0 / pitch #in physics, the period (sec/cyc) is the inverse of the frequency (cyc/sec)
        delay = period / 2   #calcuate the time for half of the wave  
        cycles = int(duration * pitch) #the number of waves to produce is the duration times the frequency

        self.__beep__(cycles=cycles, delay=delay)

        #for i in range(cycles): #start a loop from 0 to the variable “cycles” calculated above
        #    self.__beep__(delay=delay)

#pin = 21
#GPIO.cleanup()
#GPIO.setmode(GPIO.BCM)
#GPIO.setup(pin, GPIO.OUT)

#while True:
#    print("True")
#    GPIO.output(pin, True)
#    time.sleep(2)
#    print("False")
#    GPIO.output(pin, False)
#    time.sleep(2)
