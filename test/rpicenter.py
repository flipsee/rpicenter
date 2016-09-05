### this is just a test file, the actual rpicenter class still not implmented.
from DHT import DHT
from Led import Led
import RPi.GPIO as GPIO

def main():
    try:
        GPIO.setmode(GPIO.BCM)

        ### DHT Sensor ###
        dht = DHT(device_object_id="DHT1", location="Room1", gpio_pin=5)
        redLed = Led(device_object_id="Red-Led", location="Room1", gpio_pin=13)
        greenLed = Led(device_object_id="Green-Led", location="Room2", gpio_pin=19)
        blueLed = Led(device_object_id="Blue-Led", location="Room2", gpio_pin=26)

        #print("--- Manual Call ---")
        #redLed.run_sensor()
        #print(str(redLed.status))
        #dht.run_sensor()
        #print(str(dht.temperature))
        #print(str(dht.humidity))
        
        #the recipes is user configurable, loaded at run times.
        #maybe using decorator will more neat??
        redLedrecipes = []
        #if red is on, turn off green vice versa.
        redLedrecipes.append(lambda: greenLed.set_status(not(redLed.status)))
        
        dht1recipes = []
        dht1recipes.append(lambda: print("Temp above 30C!") if (dht.temperature > 30) else None)
        dht1recipes.append(lambda: print("Temp below 30C") if (dht.temperature < 30) else None)
        #if temp = 30 then blink red led.
        dht1recipes.append(lambda: redLed.start_loop(hooks=redLedrecipes) if (dht.temperature == 30) else None)
        dht.run_sensor(hooks=dht1recipes)

        #print("--- Thread Call ---")
        #threads = []
        #threads.append(dht.start_loop(hooks=dht1recipes))        
        #threads.append(redLed.start_loop())
        #threads.append(greenLed.start_loop())
        #threads.append(blueLed.start_loop())

        # while thread above run, continue with the below.
        #userinput = input("Enter key to stop the thread...\n")
        #if userinput == "d": # stop DHT thread only
        #    dht.stop_loop()
        #elif userinput == "l": # stop led thread only
        #    redLed.stop_loop()
        #    greenLed.stop_loop()
        #    blueLed.stop_loop()
        #elif userinput == "a": # stop all
        #    for item in threads:
        #        item.stop_loop()
        #else:
        #    print("wrong input!!")
    except KeyboardInterrupt:
        print("Shutdown requested...exiting")
    finally:
        exit_handler()

def exit_handler():    
    print("App terminated, cleanup!")
    GPIO.cleanup()

if __name__ == '__main__':
    main()



