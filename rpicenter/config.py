import os
import configparser

def get_config(config_name = None, config_section = None):
    if config_name == None: config_name = 'rpicenter.conf'
    if config_section == None: config_section = "DEFAULT"

    cfg = configparser.ConfigParser()
    if os.path.exists(config_name): #check the config file in the caller path
        cfg.read(config_name)
    else: #if not found check the config in the source path
        cfg.read(os.path.join(os.path.abspath(os.path.dirname(__file__)),config_name))
    
    config = cfg[config_section]
    return config
