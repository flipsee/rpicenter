from abc import ABCMeta, abstractmethod
import config
import paho.mqtt.client as mq
import lirc
from flask import Flask, request, jsonify

class IInput:
    __metaclass__ = ABCMeta
    
    def __init__(self, callback=None):
        self.__flagstop__ = False
        self.__callback__ = []
        if callback != None: self.__callback__.append(callback)

    def add_callback(self, callback):
        self.__callback__.append(callback)

    def cleanup(self):
        self.__flagstop__ = True

    def reply(self, msg, requestID=None):
        _result = "Reply Msg: " + str(msg)
        if requestID != None: _result = "Reply RequestID: " + str(requestID) + " Msg: " + str(msg)
        print(_result)
    
    @abstractmethod
    def run(self): raise NotImplementedError


class mqtt(IInput):
    def __init__(self,server=None, port=None, subscribe_topic=None, publish_topic=None, callback=None):
        super(mqtt, self).__init__(callback)
        self.last_requestID = None

        self.client = mq.Client()
        self.client.on_connect = self.__client_connect__
        self.client.on_message = self.__client_message__

        cfg = config.get_config()        
        if cfg["mqtt_server"] is not None:
            self.subscribe_topic = cfg["mqtt_subscribe"]
            self.publish_topic = cfg["mqtt_publish"]
            server = str(cfg["mqtt_server"]) 
            port = int(cfg["mqtt_port"])
        else:
            self.subscribe_topic = subscribe_topic
            self.publish_topic = publish_topic
        self.client.connect(server, int(port), 60)

    def __client_connect__(self, client, userdata, flags, rc):
        print("Subscribing to: " + str(self.subscribe_topic))
        self.client.subscribe(self.subscribe_topic)

    def __client_message__(self, client, userdata, msg):
        print("MQTT Received Topic: " + msg.topic + " Msg: " + str(msg.payload))
        _msg = msg.payload.decode(encoding="utf-8", errors="ignore")
        
        requestID = msg.topic.replace(self.subscribe_topic.replace('+','').replace('#', ''),'')
        self.last_requestID = requestID     

        if (self.__callback__ != None):
            for cb in self.__callback__:
                try:
                    if cb != None: cb(msg=_msg, input=self, requestID=requestID)
                except Exception as ex:
                    print("MQTT Input Error: " + str(ex))

    def publish_msg(self, topic, msg):
        self.client.publish(topic, msg)

    def reply(self, requestID, msg):
        topic = str(self.publish_topic) + str(requestID)
        print("MQTT Input Publishing Message Topic: " + str(topic) + " Msg: " + str(msg))
        self.publish_msg(topic, str(msg))

    def run(self):
        print("Starting MQTT Input...")
        try:
            self.client.loop_forever()
        except Exception as ex:
            print("MQTT Input Error: " + str(ex))

    def cleanup(self):
        if self.client is not None: self.client.disconnect()

class console(IInput):
    def __init__(self, callback=None):
        super(console, self).__init__(callback)

    def run(self):
        self.__flagstop__ = False
        print("Starting Console Input...")

        while True:
            if self.__flagstop__: return
            
            try:
                _msg = input("Enter Console command:\n")
                if (self.__callback__ != None):
                    for cb in self.__callback__:
                        try:
                            if cb != None: cb(msg=_msg, input=self)
                        except Exception as ex:
                            print("Console Input Error: " + str(ex))
            except Exception as ex:
                print("Console Input Error: " + str(ex))            

class ir(IInput):
    __remote_command__ = {'KEY_0': 'RedLed.on',
            'KEY_1': 'RedLed.off',
            'KEY_2': 'GreenLed.on',
            'KEY_3': 'GreenLed.off',
            'KEY_4': 'BlueLed.on',
            'KEY_5': 'BlueLed.off',
            'KEY_6': 'Display.show_message("Hello World")',
            'KEY_7': 'Display.clear',
            'KEY_8': 'lambda: Display.show_message(TempSensor.temperature())',
            'KEY_9': 'Display.show_message(run_command("TempSensor.temperature"))',
            'KEY_UP': 'Display.show_message(Btn.get_state())',
            'KEY_DOWN': 'Display.show_message(Btn.get_laststatechange())'}

    def __init__(self, callback=None):
        super(ir, self).__init__(callback)

    def run(self):
        self.__flagstop__ = False
        print("Starting IR Input...")
        try:
            sockid = lirc.init("rpicenter", blocking = False)

            while True:
                if self.__flagstop__:
                    lirc.deinit() 
                    return
                try:
                    codeIR = lirc.nextcode()
                    if codeIR:
                        action = codeIR[0]
                        print("IR Input Received: " + action)
                        if (self.__callback__ != None):
                            for cb in self.__callback__:
                                if cb != None:
                                    try:
                                        #find the command from the dict
                                        command = ir.__remote_command__.get(action,"Empty")
                                        print("IR Remote Command: " + str(command))

                                        if command != "Empty": cb(msg=command, input=self)
                                    except Exception as ex:
                                        print("IR Input Error: " + str(ex))
                except Exception as ex:
                    print("IR Input Error: " + str(ex))
        except KeyboardInterrupt:
            print("Shutdown requested...exiting IR")

class webapi(IInput):
    def __init__(self, callback=None):
        super(webapi, self).__init__(callback)
        self.app = Flask(__name__)

        cfg = config.get_config()
        if cfg["webapi_port"] is not None:
            self.webapi_port = int(cfg["webapi_port"])
            self.webapi_address = cfg["webapi_address"]
        else:
            self.webapi_port = 9003
            self.webapi_address = '0.0.0.0'
        
        self.routes() #load all the routes

    def run(self):
        print("Starting WebAPI Input...")
        self.app.run(host=self.webapi_address, port=self.webapi_port, debug=True, use_reloader=False)
    
    def cleanup(self):
        try:
            func = request.environ.get('werkzeug.server.shutdown')
            if func is not None: func()
        except:
            pass

    def routes(self):
        #we use single route to catch all
        @self.app.route('/', defaults={'path': ''})
        @self.app.route('/<path:path>')
        def catch_all(path):
            command = self.__parse_input__(path)
            result = "" #self.__run_command__(command)
            return 'You enter: %s' % command + " Response: " + str(path)

    def __parse_input__(self, path):
        cmd = ""
        'convention: http://rpi.center/{Command}/{Parameter1}/{Parameter2}...'
        items = list(filter(None, path.split('/')))
        for idx, item in enumerate(items):
            cmd = cmd + item
            if idx == 0 and len(items) > 1: 
                cmd = cmd + "('"
            elif len(items) > 1 and idx < len(items)-1:
                cmd = cmd + "','"
            elif len(items) > 1 and idx == len(items)-1:
                cmd = cmd + "')"
        return cmd

    def __run_command__(self, command):
        try:
            if (self.__callback__ != None):
                for cb in self.__callback__:
                    try:
                        if cb != None: 
                            return cb(msg=command) #do not pass the input param here as synchronus
                    except Exception as ex:
                        print("WebAPI Input Error: " + str(ex))
        except Exception as ex:
            print("WebAPI Input Error: " + str(ex))

