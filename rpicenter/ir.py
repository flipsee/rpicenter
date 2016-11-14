import lirc

__callback__ = []
__remote_command__ = {'KEY_0': 'RedLed.on', 
            'KEY_1': 'RedLed.off',
            'KEY_2': 'GreenLed.on',
            'KEY_3': 'GreenLed.off',
            'KEY_4': 'BlueLed.on',
            'KEY_5': 'BlueLed.off',
            'KEY_6': 'Display.show_message("Hello World")',
            'KEY_7': 'Display.clear',
            'KEY_8': 'Display.show_message(TempSensor.temperature())',
            'KEY_9': 'Display.show_message(TempSensor.humidity())',
            'KEY_UP': 'Display.show_message(Btn.get_state())', 
            'KEY_DOWN': 'Display.show_message(Btn.get_laststatechange())'}

def input_ir():
    try:
        #this = sys.modules[__name__]
        print("Starting IR Input...")
        sockid = lirc.init("rpicenter", blocking = False)#IR-code

        while True:
            codeIR = lirc.nextcode()#IR-code
            try:
                if codeIR:
                    action = codeIR[0]
                    print("IR Input Received: " + action)
                    if (__callback__ != None):
                        for cb in __callback__:
                            if cb != None:
                                try: 
                                    #find the command from the dict
                                    command = __remote_command__.get(action,"Empty")
                                    print("IR Remote Command: " + str(command))
                                    #if command != "Empty": cb(command)
                                except Exception as ex:
                                    print("IR Input Error: " + str(ex))
            except Exception as ex:
                print("IR Input Error: " + str(ex))
    except KeyboardInterrupt:
        print("Shutdown requested...exiting ir")
    #finally:

def add_callback(callback):
    __callback__.append(callback)
