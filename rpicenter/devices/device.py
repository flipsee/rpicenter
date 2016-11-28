from functools import wraps
import utils

### Device Command decorator ###
def command(func,*args, **kwargs):
    @wraps(func)
    def wrapper(*args, **kwargs):
        _result = None
        _device_object_id = ""

        if len(args) > 0 and isinstance(args[0], Device):
            self = args[0]
            _device_object_id = self.device_object_id + "."

        print("Running: " + _device_object_id + func.__name__)

        try:
            utils.run_hooks(self.hooks, "PRE_" + func.__name__)
            _result = func(*args, **kwargs)
            utils.run_hooks(self.hooks, "POST_" + func.__name__)
        except Exception as ex:
            print(str(ex))
            _result = "ERR: " + str(ex)
        finally:
            if _result == None:
                _result = _device_object_id + func.__name__ + ": " + "ACK"
            #print(str(_result))
            return _result
    return wrapper

class Device:
    def __init__(self, device_object_id, slot, gpio_pin, location, is_local=True):
        self.__flagstop__ = False
        self.hooks = {}
        self.device_object_id = device_object_id
        self.slot = slot
        self.gpio_pin = gpio_pin
        self.location = location
        self.is_local = is_local
        self.commands = [method for method in dir(self) if callable(getattr(self, method)) and not method.startswith("__")]

    def add_hook(self, key, func):
        self.hooks.update({key: func})

    def cleanup(self):
        self.__flagstop__ = True

    @command
    def get_commands(self):
        return self.commands
