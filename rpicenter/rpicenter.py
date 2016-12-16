import RPi.GPIO as GPIO
import threading, time, inspect, logging
import config 
from rpicenterModel import *
from input import MQTT, Console, IR, WebAPI, Message, Queue
from utils import parse_input
from devices import devices
from commands import commands

logger = logging.getLogger("rpicenter")

#1. load all devices from db.
#2. load recipies.
#3. wait input.
def insert_sample():
    db = rpicenterBL()
    try:
        with db.atomic() as txn:
            db.add_Device(DeviceObjectID="TempSensor", Slot="0", Location="Living Room", GPIOPin=5, Type="DHT", IsLocal=True)
            db.add_Device(DeviceObjectID="RedLed", Slot="1", Location="Living Room", GPIOPin=26, Type="Led", IsLocal=True)
            db.add_Device(DeviceObjectID="GreenLed", Slot="2", Location="Living Room", GPIOPin=19, Type="Led", IsLocal=True)
            db.add_Device(DeviceObjectID="BlueLed", Slot="3", Location="Living Room", GPIOPin=13, Type="Led", IsLocal=True)
            db.add_Device(DeviceObjectID="Display", Slot="4", Location="Living Room", GPIOPin=24, Type="Display", IsLocal=True)
            db.add_Device(DeviceObjectID="Btn", Slot="5", Location="Living Room", GPIOPin=12, Type="Switch", IsLocal=True)
            db.add_Device(DeviceObjectID="Buzzer", Slot="6", Location="Living Room", GPIOPin=21, Type="Buzzer", IsLocal=True)
            db.add_Device(DeviceObjectID="ESP8266-1", Slot="1", Location="Main Bed Room", GPIOPin=0, Type="Remote", IsLocal=False)
    finally:
        db.close()

def load_hooks():
    logger.debug("=== Adding Hooks ===")        
    RedLed = devices.get_device("RedLed")
    RedLed.add_hook("POST_on", "run_command('GreenLed.off')")
    RedLed.add_hook("POST_off", "run_command('GreenLed.on')")
    Btn = devices.get_device("Btn")
    Btn.add_callback("run_command('RedLed.toggle')")

class RPiCenter:
    def __init__(self):
        self.__input_channel__ = {}
        self.config = config.get_config()
        GPIO.setmode(eval("GPIO." + str(self.config["gpio_type"])))
        GPIO.setwarnings(False)
        self.device_name = self.config["device_name"]
        self.queue = None #<<< this queue is only for sending relay message to a remote device...

    def load_channels(self):
        self.__input_channel__.update({'WebAPI': WebAPI(callback=self.run_command, port=self.config["webapi_port"], address=self.config["webapi_address"])})
        self.__input_channel__.update({'IR': IR(callback=self.run_command)})
        self.__input_channel__.update({'Console': Console(callback=self.run_command)})
        #self.__input_channel__.update({'MQTT': MQTT(callback=self.run_command, server=self.config["mqtt_server"],port=self.config["mqtt_port"], subscribe_topic=self.config["mqtt_subscribe"], queue=True)})

        # we will use this to communicate with remote device also.
        _mqtt = MQTT(callback=self.run_command, server=self.config["mqtt_server"], port=self.config["mqtt_port"], subscribe_topic=self.config["mqtt_subscribe"], queue=True)
        self.__input_channel__.update({'MQTT': _mqtt})
        self.queue = _mqtt.get_queue()
        _mqtt.add_event_subscription(event_name='reading/#',callback=commands.get_command('log_sensor_reading'))

    def load_devices(self):
        db = rpicenterBL()
        try:
            data = db.get_Devices()

            if data.count() == 0:
                insert_sample()
                data = db.get_Devices()

            logger.debug("=== Loading Devices-Start: " + str(data.count()) + " ===")
            for entry in data:
                logger.debug("Device:" + entry.DeviceObjectID)
                devices.add_device(device_object_id=entry.DeviceObjectID, slot=entry.Slot, gpio_pin=entry.GPIOPin, location=entry.Location, is_local=entry.IsLocal, type=entry.Type)
        except Exception as ex:
            logger.error(ex, exc_info=True)
            raise
        finally:
            db.close()

    def load_hooks(self):
        #implement load hooks from DB???
        return load_hooks()

    def run_command(self, msg, input=None, requestID=None, *args, **kwargs):
        _result = None
        try:
            _device_name, _method_name, _param = parse_input(str(msg))

            if _device_name == None: ### call the public method ###
                _result = commands.run_command(_method_name, _param)
            else: ### call the devices method ###
                _result = devices.run_command(_device_name, _method_name, _param)

            if isinstance(_result, Message):
                if _result.sender is None: _result.sender = self.device_name
                if _result.on_response is None and input is not None: _result.on_response = input.reply
                _result = self.queue.enqueue(_result)

            _message = kwargs.get('message', None)
            if _message is not None and isinstance(_message, Message): _message.response = _result

            if input != None: input.reply(requestID=requestID, msg=_result, message=_message)
        except Exception as ex:
            logger.error(ex, exc_info=True)
            _result = "Unable to run the command: " + str(msg)
            raise
        finally:
            return _result

    def run(self):
        try:
            self.load_devices()
            self.load_hooks()
            #print("Public Commands: " + str(self.run_command("list_commands")))

            ### Input Channels ###
            self.load_channels()
            for key, input in self.__input_channel__.items():
                i = threading.Thread(target=input.run)
                i.daemon = True
                i.start()

            # the below is to suspend the thread so it will not quit
            while True:
                pass
        except Exception as ex:
            logger.error(ex, exc_info=True)
            raise

    def cleanup(self):
        for key, input in self.__input_channel__.items():
            input.cleanup()        
        devices.cleanup()
        commands.cleanup()
        GPIO.cleanup()
        time.sleep(0.5)

#singleton for RPiCenter
rpicenter = RPiCenter()
