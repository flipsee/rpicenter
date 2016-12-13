from functools import wraps
import sys, os, glob, inspect, importlib, logging, ast
import utils

logger = logging.getLogger("rpicenter.commands")

class CommandDispatcher:
    def __init__(self):
        self.__commands__ = {}
        self.__hooks__ = {}
    
    def register(self, *args):
        def wrapper(func):
            logger.debug("Registering: " + func.__name__)
            self.__commands__[func.__name__] = [func, str(func.__doc__)]
            return func
        # If there is one (and only one) positional argument and this argument is callable,
        # assume it is the decorator (without any optional keyword arguments)
        if len(args) == 1 and callable(args[0]):
            return wrapper(args[0])
        else:
            return wrapper

    def run_command(self, method_name, param, *args, **kwargs):
        logger.debug("Running Public Command: " + method_name)
        _result = None
        try:
            _func =  self.get_command(method_name)
            if _func != None:
                utils.run_hooks(self.__hooks__, "PRE_" + method_name)
                if param is not None:
                    _result = _func(ast.literal_eval(param))
                else:
                    _result = _func()
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
        self.__commands__ = None
        self.__hooks__ = None

    def get_command(self, method_name):
        _command = self.__commands__.get(method_name, None)
        if _command is not None:
            return _command[0]
        else: return None

    def list_commands(self):
        _command_list = {}
        for key, d in self.__commands__.items():
            _command_list.update({key: d[1]})
        return _command_list

commands = CommandDispatcher()

_plugins = glob.glob(os.path.join(os.path.dirname(__file__), "*.py"))
__all__ = [os.path.splitext(os.path.basename(f))[0] for f in _plugins
           if os.path.isfile(f) and not os.path.basename(f).startswith("_")]

from commands import *
