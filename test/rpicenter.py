### this is just a test file, the actual rpicenter class still not implmented.
from DHT import DHT
from Led import Led
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)

### DHT Sensor ###
dht = DHT(device_object_id="DHT1", location="Room1", gpio_pin=5)
redLed = Led(device_object_id="Red-Led", location="Room1", gpio_pin=13)

print("--- Manual Call ---")
redLed.run_sensor()
print(str(redLed.status))
dht.run_sensor()
print(str(dht.temperature))
print(str(dht.humidity))

print("--- Thread Call ---")
threads = []
threads.append(dht.start_loop())
threads.append(redLed.start_loop())

## while thread above run, continue with the below.
userinput = input("Enter key to stop the thread...\n")
if userinput == "d": # stop DHT thread only
    dht.stop_loop()
elif userinput == "l": # stop led thread only
    redLed.stop_loop()
elif userinput == "a": # stop all
    for item in threads:
        item.stop_loop()
else:
    print("wrong input!!")

GPIO.cleanup()
