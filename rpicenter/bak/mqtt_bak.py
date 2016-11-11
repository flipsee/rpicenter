import configparser, os
import paho.mqtt.client as mq

client = None
client_topic = None
__callback__ = []

def main(server=None, port=None, topic=None):
    global client
    global client_topic

    client = mq.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    if server == None:
        cfg = configparser.ConfigParser()
        configname = 'rpicenter.conf'
        if os.path.exists(configname): #check the config file in the caller path
            cfg.read(configname)
        else: #if not found check the config in the source path
            cfg.read(os.path.join(os.path.abspath(os.path.dirname(__file__)),configname))

        config = cfg["DEFAULT"]

        if config["mqtt_server"] is not None:
            client_topic = config["mqtt_topic"]
            server = str(config["mqtt_server"]) 
            port = int(config["mqtt_port"])
    else:
        client_topic = topic

    client.connect(server, int(port), 60)

def on_connect(client, userdata, flags, rc):
    global client_topic
    print("Connected with result code "+str(rc))
    client.subscribe(client_topic)

def on_message(client, userdata, msg):
    global __callback__
    print(msg.topic+" "+str(msg.payload))
    _msg = msg.payload.decode(encoding="utf-8", errors="ignore")

    if (__callback__ != None):
        for cb in __callback__:
            if cb != None: cb(_msg)

def add_callback(callback):
    global __callback__
    __callback__.append(callback)

def send_message(topic, message):
    global client
    client.publish(topic, message)

