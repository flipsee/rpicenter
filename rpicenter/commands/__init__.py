import sys, os, glob, inspect, importlib
from functools import wraps
import utils

class CommandDispatcher:
    def __init__(self):
        self.__commands__ = {}
        self.__command_list__ = {}
        self.__hooks__ = {}
    
    def register(self, *args):
        def wrapper(func):
            #print("Registering: " + func.__name__ + " Key: " + str(keyword))
            self.__commands__[func.__name__] = func
            self.__command_list__[func.__name__] = str(func.__doc__)
            return func

        # If there is one (and only one) positional argument and this argument is callable,
        # assume it is the decorator (without any optional keyword arguments)
        if len(args) == 1 and callable(args[0]):
            return wrapper(args[0])
        else:
            return wrapper

    def run_command(self, method_name, param, *args, **kwargs):
        #print("Running Public Command: " + method_name)
        _result = None
        try:
            _func =  self.__commands__.get(method_name, None)
            #print(str(_func))
            if _func != None:
                utils.run_hooks(self.__hooks__, "PRE_" + method_name)
                _result = eval('_func' + param)
                utils.run_hooks(self.__hooks__, "POST_" + method_name)
            else: 
                _result = "Unknown Command! "
        except Exception as ex:
            _result = "Err: " + str(ex)
            raise
        finally:
            return _result
            
    def add_hook(self, key, func):
        self.__hooks__.update({key: func})

    def cleanup(self):
        self.__commands__ = {}
        self.__command_list__ = {}
        self.__hooks__ = {}

    def get_command(self, method_name):
        return self.__commands__.get(method_name, None)

    def get_commands(self):
        return self.__command_list__

commands = CommandDispatcher()

_plugins = glob.glob(os.path.join(os.path.dirname(__file__), "*.py"))
__all__ = [os.path.splitext(os.path.basename(f))[0] for f in _plugins
           if os.path.isfile(f) and not os.path.basename(f).startswith("_")]

from commands import *
