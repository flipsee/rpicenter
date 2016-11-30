from abc import ABCMeta, abstractmethod
from datetime import datetime, timedelta
from flask import Flask, request, jsonify
import threading, uuid, time
import paho.mqtt.client as mq
import lirc

class Message():
    msg_status = {'NEW': "New Message in Queue not send yet",
              'WAITING': "Message sent, waiting for response",
              'EXPIRED': "Message exceed retries or expired",
              'SUCCESS': "Response Received from remote"}

    def __init__(self, msg, sender, receiver, on_response=None, on_expiry=None, expiry=60):
        self.msg = msg
        self.sender = sender.lower()
        self.receiver = receiver.lower()
        self.msg_id = self.sender + "_" + str(uuid.uuid4())
        #self.msg_id = "12345"
        self.retry_count = 0
        self.last_retry = datetime.min
        self.msg_timestamp = datetime.now()
        self.msg_timestamp_utc = datetime.utcnow()
        self.msg_expiry = self.msg_timestamp + timedelta(seconds=expiry)
        self.response = None
        self.status = self.msg_status["NEW"]
        self.parameters = None
        self.on_response = on_response        
        if on_expiry is not None:
            self.on_expiry = on_expiry
        else:
            self.on_expiry = self.on_response

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

    def reply(self, **kwargs):
        _result = 'Reply'

        _requestID = kwargs.get('requestID', None)
        if _requestID is not None: _result = _result + " RequestID: " + str(_requestID)

        _msg = kwargs.get('msg', None)
        if _msg is not None: _result = _result + " Msg: " + str(_msg)

        _message = kwargs.get('message', None)
        if _message is not None: _result = "Reply RequestID: " + str(message.msg_id) + " Msg: " + str(message.msg) + " Response: " + str(message.response)

        print(_result)
    
    @abstractmethod
    def run(self): raise NotImplementedError

    @abstractmethod
    def send_message(self, message): raise NotImplementedError

class MQTT(IInput):
    def __init__(self, server, port, subscribe_topic, publish_topic=None, callback=None):
        super(MQTT, self).__init__(callback)
        self.last_requestID = None

        self.client = mq.Client()
        self.client.on_connect = self.__client_connect__
        self.client.on_message = self.__client_message__
        self.subscribe_topic = subscribe_topic
        self.publish_topic = publish_topic
        self.client.connect(server, int(port), 60)

    def __client_connect__(self, client, userdata, flags, rc):
        print("Subscribing to: " + str(self.subscribe_topic))
        self.client.subscribe(self.subscribe_topic)

    def __client_message__(self, client, userdata, msg):
        print("MQTT Received Topic: " + msg.topic + " Msg: " + str(msg.payload))
        _msg = msg.payload.decode(encoding="utf-8", errors="ignore")
        
        _topics = msg.topic.split("/")        
        requestID = _topics[-1] # last section is the msg_id
        self.last_requestID = requestID     

        if (self.__callback__ != None):
            for cb in self.__callback__:
                try:
                    if cb != None: cb(msg=_msg, input=self, requestID=requestID)
                except Exception as ex:
                    print("MQTT Input Error: " + str(ex))

    def publish_msg(self, msg, topic=None):
        _topic = self.publish_topic
        if topic is not None: _topic = topic        

        print("MQTT Publishing Message Topic: " + str(topic) + " Msg: " + str(msg))
        self.client.publish(_topic, str(msg))

    def send_message(self, message):
        try:
            self.reply(message)
            return True, "Message sent"
        except:
            return False, "Failed to send message"

    def reply(self, message):
        """ {ESP8266}/inbox/{RPiCenter}/{Date Time}/{Trx ID} """
        if message is not None and isinstance(message, Message):
            _topic = message.receiver + "/inbox/" + message.sender + "/" + str(message.msg_timestamp) + "/" + str(message.msg_id)
            print("MQTT Publishing Message Topic: " + str(_topic) + " Msg: " + str(message.msg))
            self.client.publish(_topic, str(message.msg))

    def run(self):
        print("Starting MQTT Input...")
        try:
            if self.client is not None: self.client.loop_start()
        except Exception as ex:
            print("MQTT Input Error: " + str(ex))

    def cleanup(self):
        if self.client is not None:
            self.client.loop_stop() 
            self.client.disconnect()

class Console(IInput):
    def __init__(self, callback=None):
        super(Console, self).__init__(callback)

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
                raise

class IR(IInput):
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
            'KEY_UP': 'show_temp_to_screen',
            'KEY_DOWN': 'Display.show_message(Btn.get_laststatechange())'}

    def __init__(self, callback=None):
        super(IR, self).__init__(callback)

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
                                        raise
                except Exception as ex:
                    print("IR Input Error: " + str(ex))
                    raise
        except KeyboardInterrupt:
            print("Shutdown requested...exiting IR")
            raise

class WebAPI(IInput):
    def __init__(self, address, port, callback=None):
        super(WebAPI, self).__init__(callback)
        self.app = Flask(__name__)
        self.webapi_port = int(port)
        self.webapi_address = str(address)
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
            result = self.__run_command__(command)
            return 'You enter: %s' % command + " Response: " + str(result)

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
            raise


class Queue:
    def __init__(self, send_message=None, message_notfound=None):
        self.max_retry = 3
        self.retry_waiting_time = 5
        self.send_message = send_message
        self.message_notfound = message_notfound
        self.queue = {}
        self.queue_thread = None
        self.queue_flagstop = False

    def enqueue(self, message): #add msg to queue
        print("add Msg to Queue")
        if isinstance(message, Message):
            self.queue.setdefault(message.msg_id, message)
            print(str(self.queue))
            self.queue_flagstop = False
            self.run()
            return "Message Queued, MsgID: " + message.msg_id
        else: return "Message Queue is invalid"

    def dequeue(self, msg_id): #remove msg from queue manually
        return self.queue.pop(msg_id, None)
        
    def expired(self, msg_id): #if max retries reach or message expired we remove it from the queue, run on on_expired
        message = self.queue.pop(msg_id, None)
        print("Expired Msg:" + message.msg_id + " " +  message.status + " " + str(message.last_retry))
        if message is not None:
            message.status =  message.msg_status["EXPIRED"]
            if message.on_expiry is not None: return message.on_expiry(message)
        return

    def response(self, msg, requestID, *args, **kwargs): #if response is received, parse it and call on_response, remove it from the queue.
        message = self.queue.pop(requestID, None)
        if message is not None:
            if message.on_response is not None:
                message.status =  message.msg_status["SUCCESS"]
                message.response = msg
                old_sender = message.sender
                message.sender = message.receiver
                message.receiver = old_sender
                return message.on_response(message)
            else: return
        else: return self.message_notfound(msg=msg, requestID=requestID, *args, **kwargs)

    def send(self, message):
        print("Sending Msg:" + message.msg_id + " " +  message.status + " " + str(message.last_retry))
        message.retry_count = message.retry_count + 1
        message.last_retry = datetime.now()
        message.status =  message.msg_status["WAITING"]
        send_status, response = self.send_message(message)
        if send_status == True and message.on_response == None: #fire and forget
            self.dequeue(msg.msg_id)

    def __run_queue__(self):
        while True:
            #lets check if there is an item in the queue if not stop.
            if len(self.queue) < 1 or self.queue_flagstop == True: 
                print("Stoping Queue Job...")
                return
            for key, msg in list(self.queue.items()):
                #check which one need tobe send
                if msg.status == msg.msg_status["NEW"] or (msg.retry_count <= self.max_retry and msg.last_retry + timedelta(seconds=self.retry_waiting_time) <= datetime.now()):
                    self.send(msg)
                elif msg.retry_count > self.max_retry or msg.msg_expiry < datetime.now():
                    self.expired(msg.msg_id)
            time.sleep(10)

    def run(self):
        print("Starting Queue Job...")
        self.queue_thread = threading.Thread(target=self.__run_queue__)
        if self.queue_thread is not None and self.queue_thread.isAlive() == False:
            self.queue_thread.start()
        return self

    def cleanup(self):
        self.queue_flagstop = True
        self.queue.clear()

