import logging
from commands import commands
from devices import devices
from rpicenterModel import *
import rpicenter

logger = logging.getLogger("rpicenter.commands.basic")

@commands.register
def list_devices(msg=None):
    """ list Devices in RPiCenter"""
    #if msg is not None: print("Msg: " + str(msg))
    #for key, value in devices.list_devices().items():
    #    print("Key: " + key + " Value: " + str(value))
    return devices.list_devices()

@commands.register
def list_commands():
    """ list Commands in RPiCenter """
    #for key, value in commands.list_commands().items():
    #    print("Key: " + key + " Value: " + str(value))
    return commands.list_commands()

@commands.register
def show_temp_to_screen():
    """ get the temperature and display it on screen """
    run_command = rpicenter.rpicenter.run_command
    temp = run_command("TempSensor.temperature")
    run_command("Display.show_message('" + str(temp) + "')") 

@commands.register
def log_sensor_reading(device_object_id, reading_datetime, parameter, value, unit):
    """ store the sensor reading in the Database.
        - reading_datetime
        - device_object_id
        - parameter
        - value
        - unit
    """
    db = rpicenterBL()
    try:
        with db.atomic() as txn:
            db.add_DeviceReading(DeviceObjectID=device_object_id, ReadingDateTime=reading_datetime, Parameter=parameter, Value=value, Unit=unit)
    except Exception as ex:
        logger.error(ex, exc_info=True)
        raise
    finally:
        db.close()

    return "Sensor Reading Logged"
