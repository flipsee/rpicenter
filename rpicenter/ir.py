import lirc

__callback__ = []

def input_ir():
    try:
        #this = sys.modules[__name__]
        print("Starting IR Input...")
        sockid = lirc.init("rpicenter", blocking = False)#IR-code

        while True:
            codeIR = lirc.nextcode()#IR-code
            if codeIR:
                action = codeIR[0]
                print("IR Input Received: " + action)
                #func(action)
                if (__callback__ != None):
                    for cb in __callback__:
                        if cb != None: cb(_msg)
                #method = getattr(this,action)
                #method()
    except KeyboardInterrupt:
        print("Shutdown requested...exiting ir")
    #finally:

def add_callback(callback):
    __callback__.append(callback)
