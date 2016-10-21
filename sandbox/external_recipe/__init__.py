from dht import DHT
from led import Led
from display import Display
import RPi.GPIO as GPIO
import time

def main():
    try:
        GPIO.setmode(GPIO.BCM)

        print("--- Loading Devices ---")
        dht = DHT(device_object_id="DHT1", slot="0", location="Living Room", gpio_pin=5)
        redLed = Led(device_object_id="Red-Led", slot="1", location="Living Room", gpio_pin=26,GPIO=GPIO)
        greenLed = Led(device_object_id="Green-Led", slot="2", location="Living Room", gpio_pin=19,GPIO=GPIO)
        blueLed = Led(device_object_id="Blue-Led", slot="3", location="Living Room", gpio_pin=13,GPIO=GPIO)

        disp = Display(device_object_id="Display", slot="4", location="Living Room", gpio_pin=24)

        print("Command in RedLed are: " + str(redLed.commands))
        redLed.on()
        time.sleep(2)
        redLed.off()        
        time.sleep(2)
        print("Command in dht are: " + str(dht.commands))
        print("Temperature@" + str(dht.location) + " is: " + str(dht.temperature()))

        try:
            print("Command in dht are: " + str(disp.commands))
            disp.show_message("happycat_oled_64.ppm")
            time.sleep(5)
        except KeyboardInterrupt:
            print("Shutdown requested...exiting")
        finally:
            disp.clear()

    except KeyboardInterrupt:
        print("Shutdown requested...exiting")
    finally:
        exit_handler()

def exit_handler():    
    print("App terminated, cleanup!")
    GPIO.cleanup()

if __name__ == '__main__':
    main()
