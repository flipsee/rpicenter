import config
import paho.mqtt.client as mq

class mqtt():
    def __init__(self,server=None, port=None, topic=None, callback=None):
        self.client = mq.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.topic = None
        self.__callback__ = []
        cfg = config.get_config()
        if cfg["mqtt_server"] is not None:
            self.topic = cfg["mqtt_topic"]
            server = str(cfg["mqtt_server"]) 
            port = int(cfg["mqtt_port"])
        else:
            self.topic = topic

        if callback != None: self.__callback__.append(callback)

        self.client.connect(server, int(port), 60)

    def on_connect(self, client, userdata, flags, rc):
        print("Connected with result code "+str(rc))
        self.client.subscribe(self.topic)

    def on_message(self, client, userdata, msg):
        print(msg.topic+" "+str(msg.payload))
        _msg = msg.payload.decode(encoding="utf-8", errors="ignore")

        if (self.__callback__ != None):
            for cb in self.__callback__:
                if cb != None: cb(_msg)

    def add_callback(self, callback):
        self.__callback__.append(callback)

    def send_message(self, topic, message):
        self.client.publish(topic, message)

