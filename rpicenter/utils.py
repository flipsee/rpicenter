import rpicenter

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
            _param = "()"
        else:
            _method_name = str(cmd[(_classidx + 1):_paramidx])
            _param = str(cmd[_paramidx:len(cmd)])
        #print(_device_name + " : " + _method_name + " : " + _param)
        if _classidx < 0 or (_paramidx >= 0 and _paramidx < _classidx): _device_name = None
    return _device_name, _method_name, _param


def run_hooks(hooks, key, *args, **kwargs):
    #print(str(rpicenter))
    run_command = rpicenter.run_command

    #print(str(run_command))
    #print("Hooks: " + str(hooks) + " ; Key: " + str(key))
    if (hooks != None):
        for h_key, h_value in hooks.items():
            if h_key == key: 
                #print("Running: " + str(key) + " ; " + str(h_value))
                try:
                   eval(h_value)
                   #h_value()
                except Exception as ex:
                    print(str(ex))
