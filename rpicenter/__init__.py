#import os, glob

# Build list of commands
#_plugins = glob.glob(os.path.join(os.path.dirname(__file__), "*.py"))
#__all__ = [os.path.splitext(os.path.basename(f))[0] for f in _plugins
#           if os.path.isfile(f) and not os.path.basename(f).startswith("_")]

# Load all commands
#from rpicenter import *

#from os.path import dirname, basename, isfile
#import glob
#modules = glob.glob(dirname(__file__)+"/*.py")
#__all__ = [ basename(f)[:-3] for f in modules if isfile(f)]
