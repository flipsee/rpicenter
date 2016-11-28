from commands import commands
from devices import devices

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
