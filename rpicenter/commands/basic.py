from commands import commands
from devices import devices
from rpicenterModel import *

@commands.register
def list_devices(msg=None):
    """ list devices in RPICenter"""
    if msg is not None: print("Msg: " + str(msg))
    for key, value in devices.list_devices().items():
        print("Key: " + key + " Value: " + str(value))
    return devices.list_devices()

@commands.register
def list_commands():
    print("i'm here")
    for key, value in commands.get_commands().items():
        print("Key: " + key + " Value: " + str(value))
    return commands.get_commands()

@commands.register
def show_temp_to_screen():
    """ get the temperature and display on screen """
    temp = devices.run_command("TempSensor.temperature")
    devices.run_command("Display.show_message('" + str(temp) + "')") 

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
        print("Err: " + str(ex))
        raise
    finally:
        db.close()

    return "Sensor Reading Logged"
