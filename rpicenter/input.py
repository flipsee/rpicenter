from abc import ABCMeta, abstractmethod
from datetime import datetime, timedelta
from flask import Flask, request, jsonify
import threading, uuid, time, ast, logging
import paho.mqtt.client as mq
import lirc

logger = logging.getLogger("rpicenter.input")

class Message():
    msg_status = {'NEW': "New Message in Queue not send yet",
              'WAITING': "Message sent, waiting for response",
              'EXPIRED': "Message exceed retries or expired",
              'SUCCESS': "Response Received from remote"}

    def __init__(self, msg, sender, receiver, on_response=None, on_expiry=None, requestID=None, expiry=60):
        self.msg = msg
        self.sender = sender
        self.receiver = receiver        
        if requestID is not None:
            self.msg_id = str(requestID)
        else:
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

    def response_received(self, response): #if response is received, parse it and call on_response callback
        logger.debug("Message.response_received: " + str(response))
        if self.on_response is not None:
            self.status =  self.msg_status["SUCCESS"]
            self.response = response
            _old_sender = self.sender
            self.sender = self.receiver
            self.receiver = _old_sender
            return self.on_response(self)
        else: return


class IInput:
    __metaclass__ = ABCMeta
    
    def __init__(self, callback=None, queue=False):
        self.__flagstop__ = False
        self.__callback__ = []
        if queue == True:
            self.__queue__ = Queue()
            self.__queue__.send_message = self.send_message
        else: 
            self.__queue__ = None
        if callback != None: self.__callback__.append(callback)

    def get_queue(self):
        return self.__queue__

    def add_callback(self, callback):
        self.__callback__.append(callback)

    def cleanup(self):
        if self.__queue__ is not None: self.__queue__.cleanup()
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

class MQTT(IInput): #make mqtt class to also inherit the queue to simplify the structure???
    def __init__(self, server, port, subscribe_topic, publish_topic=None, callback=None, queue=None):
        super(MQTT, self).__init__(callback, queue)
        self.client = mq.Client()
        self.client.on_connect = self.__client_connect__
        self.client.on_message = self.__client_message__
        self.subscribe_topic = subscribe_topic
        self.publish_topic = publish_topic
        self.client.connect(server, int(port), 60)
        self.__event_subscriptions__ = {} #topic, callback method.
    
    def add_event_subscription(self, event_name, callback):
        self.client.subscribe(event_name)
        _event_name = event_name.replace("#", "").replace("+", "")
        logger.info("Subscribing to: " + _event_name + ", callback: " + str(callback))
        self.__event_subscriptions__.update({_event_name: callback})

    def __client_connect__(self, client, userdata, flags, rc):
        logger.info("Subscribing to: " + str(self.subscribe_topic))
        self.client.subscribe(self.subscribe_topic)

    def __client_message__(self, client, userdata, msg):
        logger.debug("MQTT Received Topic: " + msg.topic + " Msg: " + str(msg.payload))
        _msg = msg.payload.decode(encoding="utf-8", errors="ignore")

        _found_in_subscription = False
        for key, callback in self.__event_subscriptions__.items():
            if msg.topic.startswith(key):
                _found_in_subscription = True
                try:
                    #print(ast.literal_eval(_msg))
                    callback(**ast.literal_eval(_msg))
                    return
                except Exception as ex:
                    logger.error(ex, exc_info=True)
                    raise

        if _found_in_subscription == False:
            _topics = msg.topic.split("/")
            _requestID=_topics[-1]
            _message = None

            if self.__queue__ is not None:
                _message = self.__queue__.dequeue(_requestID)
        
            if _message is not None:            
                _message.response_received(response=_msg)
            else:
                _message = Message(msg=_msg, sender=_topics[0], receiver=_topics[2], requestID=_topics[-1])

                if (self.__callback__ != None):
                    for cb in self.__callback__:
                        try:
                            if cb != None: cb(msg=_message.msg, input=self, requestID=_message.msg_id, message=_message)
                        except Exception as ex:
                            logger.error("MQTT Input Error: " + str(ex), exc_info=True)
                            raise

    def publish_msg(self, msg, topic=None):
        _topic = self.publish_topic
        if topic is not None: _topic = topic        
        logger.debug("MQTT Publishing Message Topic: " + str(topic) + " Msg: " + str(msg))
        self.client.publish(_topic, str(msg))

    def send_message(self, message):
        try:
            self.reply(message=message)
            return True, "Message sent"
        except Exception as ex:
            logger.error(ex, exc_info=True)
            return False, "Failed to send message"

    def reply(self, **kwargs):
        _message = kwargs.get('message', None)
        logger.debug("Mqtt sendng Msg: " + str(_message))
        """ {ESP8266}/inbox/{RPiCenter}/{Date Time}/{Trx ID} """
        if _message is not None and isinstance(_message, Message):
            _topic = _message.receiver + "/inbox/" + _message.sender + "/" + str(_message.msg_timestamp) + "/" + str(_message.msg_id)
            #do we need to publish the Msg or the Response?
            if _message.response is not None:
                _msg = _message.response
            else:
                _msg = _message.msg
            logger.debug("MQTT Publishing Message Topic: " + str(_topic) + " Msg: " + str(_msg))
            self.client.publish(_topic, str(_msg))

    def run(self):
        logger.info("Starting MQTT Input...")
        try:
            if self.client is not None: self.client.loop_start()
        except Exception as ex:
            logger.error(ex, exc_info=True)

    def cleanup(self):
        super(MQTT, self).cleanup()
        if self.client is not None:
            self.client.loop_stop() 
            self.client.disconnect()

class Console(IInput):
    def __init__(self, callback=None):
        super(Console, self).__init__(callback)

    def run(self):
        self.__flagstop__ = False
        logger.info("Starting Console Input...")

        while True:
            if self.__flagstop__: return
            
            try:
                _msg = input("Enter Console command:\n")
                if (self.__callback__ != None):
                    for cb in self.__callback__:
                        try:
                            if cb != None: cb(msg=_msg, input=self)
                        except Exception as ex:
                            logger.error("Console Input Error: " + str(ex), exc_info=True)
            except Exception as ex:
                logger.error("Console Input Error: " + str(ex), exc_info=True)            
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
            'KEY_8': 'show_temp_to_screen',
            'KEY_9': 'Display.show_message(TempSensor.temperature())',
            'KEY_UP': 'Display.show_message(run_command("TempSensor.temperature"))',
            'KEY_DOWN': 'Display.show_message(rpicenter.run_command("Btn.get_laststatechange"))'}

    def __init__(self, callback=None):
        super(IR, self).__init__(callback)

    def run(self):
        self.__flagstop__ = False
        logger.info("Starting IR Input...")
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
                        logger.debug("IR Input Received: " + action)
                        if (self.__callback__ != None):
                            for cb in self.__callback__:
                                if cb != None:
                                    try:
                                        #find the command from the dict
                                        command = self.__remote_command__.get(action,"Empty")
                                        logger.debug("IR Remote Command: " + str(command))

                                        if command != "Empty": cb(msg=command, input=self)
                                    except Exception as ex:
                                        logger.error("IR Input Error: " + str(ex), exc_info=True)
                                        raise
                except Exception as ex:
                    logger.error("IR Input Error: " + str(ex), exc_info=True)
                    raise
        except KeyboardInterrupt:
            logger.debug("Shutdown requested...exiting IR")
            raise

class WebAPI(IInput):
    def __init__(self, address, port, callback=None):
        super(WebAPI, self).__init__(callback)
        self.app = Flask(__name__)
        self.webapi_port = int(port)
        self.webapi_address = str(address)
        self.routes() #load all the routes

    def run(self):
        logger.info("Starting WebAPI Input...")
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
                        logger.error("WebAPI Input Error: " + str(ex), exc_info=True)
        except Exception as ex:
            logger.error("WebAPI Input Error: " + str(ex), exc_info=True)
            raise


class Queue:
    def __init__(self, send_message=None, message_notfound=None):
        self.max_retry = 3
        self.retry_waiting_time = 5
        self.send_message = send_message
        #self.message_notfound = message_notfound
        self.queue = {}
        self.queue_thread = None
        self.queue_flagstop = False
        self.queue_waiting_time = 15

    def enqueue(self, message): #add msg to queue
        if isinstance(message, Message):
            self.queue.setdefault(message.msg_id, message)
            print(str(self.queue))
            self.queue_flagstop = False
            self.run()
            return "Message Queued, MsgID: " + message.msg_id
        else: return "Message is invalid"

    def dequeue(self, msg_id): #remove msg from queue manually
        return self.queue.pop(msg_id, None)
        
    def expired(self, msg_id): #if max retries reach or message expired we remove it from the queue, run on on_expired
        message = self.queue.pop(msg_id, None)
        logger.debug("Expired Msg:" + message.msg_id + " " +  message.status + " " + str(message.last_retry))
        if message is not None:
            message.status =  message.msg_status["EXPIRED"]
            if message.on_expiry is not None: return message.on_expiry(message)
        return

    def send(self, message):
        logger.debug("Sending Msg:" + message.msg_id + " " +  message.status + " " + str(message.last_retry))
        message.retry_count = message.retry_count + 1
        message.last_retry = datetime.now()
        message.status =  message.msg_status["WAITING"]
        send_status, response = self.send_message(message)
        if send_status == True and message.on_response == None: #fire and forget
            self.dequeue(message.msg_id)

    def __run_queue__(self):
        while True:
            try:
                #lets check if there is an item in the queue if not stop.
                if len(self.queue) < 1 or self.queue_flagstop == True: 
                    logger.debug("Stoping Queue Job...")
                    return
                for key, msg in list(self.queue.items()):
                    #check which one need tobe send
                    if msg.status == msg.msg_status["NEW"] or (msg.retry_count <= self.max_retry and msg.last_retry + timedelta(seconds=self.retry_waiting_time) <= datetime.now()):
                        self.send(msg)
                    elif msg.retry_count > self.max_retry or msg.msg_expiry < datetime.now():
                        self.expired(msg.msg_id)
                time.sleep(self.queue_waiting_time)
            except Exception as ex:
                logger.error("Queue Error: " + str(ex), exc_info=True)

    def run(self):
        logger.debug("Starting Queue Job...")
        self.queue_thread = threading.Thread(target=self.__run_queue__)
        if self.queue_thread is not None and self.queue_thread.isAlive() == False:
            self.queue_thread.start()
        return self

    def cleanup(self):
        self.queue_flagstop = True
        self.queue.clear()

