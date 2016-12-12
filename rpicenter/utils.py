import logging
import rpicenter

logger = logging.getLogger("rpicenter.utils")

def parse_input(msg=None):
    _device_name = None
    _method_Name = None
    _param = None
    if msg is not None:
        cmd = str(msg)
        _classidx = cmd.find(".")
        _paramidx = cmd.find("(")

        _device_name = str(cmd[:_classidx])
        if _paramidx < 0: # means that it doesn't have any param
            _method_name = str(cmd[(_classidx + 1):])
            #_param = "()"
        else:
            if _paramidx < _classidx:
                _method_name = str(cmd[0:_paramidx])
            else:
                _method_name = str(cmd[(_classidx + 1):_paramidx])
            #_param = str(cmd[_paramidx:len(cmd)])
            _param = str(cmd[_paramidx +1 :len(cmd) -1])

        logger.debug(_device_name + " : " + _method_name + " : " + str(_param))
        if _classidx < 0 or (_paramidx >= 0 and _paramidx < _classidx): _device_name = None
    return _device_name, _method_name, _param


def run_hooks(hooks, key=None, *args, **kwargs):
    run_command = rpicenter.rpicenter.run_command
    logger.debug("Hooks: " + str(hooks) + " ; Key: " + str(key))
    if (hooks != None):
        if isinstance(hooks,dict):
            for h_key, h_value in hooks.items():
                if h_key == key or key == None: 
                    logger.debug("Running: " + str(key) + " ; " + str(h_value))
                    try:
                        #eval(h_value)
                        h_value()
                    except Exception as ex:
                        print(str(ex))
                        raise
        else:
            for item in hooks:
                try:
                    logger.debug("Running: " + str(item))
                    item()
                except Exception as ex:
                    logger.error(ex, exc_info=True)
                    raise
