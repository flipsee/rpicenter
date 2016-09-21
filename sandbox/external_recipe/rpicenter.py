### this is just a test file, the actual rpicenter class still not implmented.
from DHT import DHT
from Led import Led
import RPi.GPIO as GPIO
import time

threads = []

def main():
    try:
        GPIO.setmode(GPIO.BCM)

        ### Loading Sensor ###
        print("--- Loading Devices ---")
        dht = DHT(device_object_id="DHT1", location="Room1", gpio_pin=5)
        redLed = Led(device_object_id="Red-Led", location="Room1", gpio_pin=26,GPIO=GPIO)
        greenLed = Led(device_object_id="Green-Led", location="Room2", gpio_pin=19,GPIO=GPIO)
        blueLed = Led(device_object_id="Blue-Led", location="Room2", gpio_pin=13,GPIO=GPIO)

        ### Loading Recipies ###
        #the recipes is user configurable, loaded at run times.
        #maybe using decorator will more neat??
        greenLedrecipes = []    #if green is on, blue is also on.
        greenLedrecipes.append(["POST",lambda: blueLed.run_sensor(status=greenLed.status)])

        redLedrecipes = []      #if red is on, turn off green vice versa.
        redLedrecipes.append(["POST",lambda: greenLed.run_sensor(status=not(redLed.status))])

        dht1recipes = []        #if temp = 30 then blink red led.
        dht1recipes.append(["POST",lambda: print("Temp above 30C!") if (dht.temperature > 30) else None])
        dht1recipes.append(["POST",lambda: print("Temp below 30C") if (dht.temperature < 30) else None])
        dht1recipes.append(["POST",lambda: threads.append(redLed.loop_start()) if (dht.temperature == 30) else None])

        print("--- Loading Recipies ---")
        greenLed._hooks = greenLedrecipes
        redLed._hooks = redLedrecipes
        dht._hooks = dht1recipes

        print("--- Manual Call ---")
        print(str(redLed.run_sensor().status))
        print(str(dht.run_sensor().temperature))
        redLed.run_sensor(status=False)
        time.sleep(2)

        #overwrite hooks for this call only
        print("--- Temporary Hooks ---")
        temprecipes = []      
        temprecipes.append(["POST",lambda: greenLed.run_sensor(status=redLed.status)])
        redLed.run_sensor(status=True, hooks=temprecipes)        
        time.sleep(2)
    
        print("--- Thread Call ---")
        threads.append(dht.loop_start())        
        #threads.append(redLed.loop_start())
        #threads.append(greenLed.loop_start())
        #threads.append(blueLed.loop_start())

        # while thread above run, continue with the below.
        userinput = input("Enter key to stop the thread...\n")
        if userinput == "d": # stop DHT thread only
            dht.loop_stop()
        elif userinput == "l": # stop led thread only
            redLed.loop_stop()
            greenLed.loop_stop()
            blueLed.loop_stop()
        elif userinput == "a": # stop all
            for item in threads:
                item.loop_stop()
        else:
            print("wrong input!!")
    except KeyboardInterrupt:
        print("Shutdown requested...exiting")
    finally:
        exit_handler()

def exit_handler():    
    print("App terminated, cleanup!")
    for item in threads:
        item.loop_stop()
    #how to wait that all the threads is off?
    GPIO.cleanup()

if __name__ == '__main__':
    #time.sleep(3)
    main()



