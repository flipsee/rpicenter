#include <DateTime.h>
#include <ESP8266WiFi.h>
#include <PubSubClient.h>
#include <DHT.h>
extern "C" {
    #include "user_interface.h"
}

#define D0 16
#define D1 5 // I2C Bus SCL (clock)
#define D2 4 // I2C Bus SDA (data)
#define D3 0
#define D4 2 // Same as "LED_BUILTIN", but inverted logic
#define D5 14 // SPI Bus SCK (clock)
#define D6 12 // SPI Bus MISO
#define D7 13 // SPI Bus MOSI
#define D8 15 // SPI Bus SS (CS)
#define D9 3 // RX0 (Serial console)
#define D10 1 // TX0 (Serial console)

//Wifi
#define wifi_ssid "XXXX"
#define wifi_password "XXXX"

//Mqtt
#define mqtt_server "192.168.1.XXX"
#define mqtt_port 1999
//tring humidity_topic = "reading/{0}/humidity/%/{1}";
//tring temperature_topic = "reading/{0}/temperature/C/{1}";
//tring humidity_message = "{'device_object_id': '{0}', 'parameter': 'humidity', 'Unit': '%', 'value': {2}, 'reading_datetime' : '{1}'}";
//tring temperature_message = "{'device_object_id': '{0}', 'parameter': 'temperature', 'Unit': 'C', 'value': {2}, 'reading_datetime' : '{1}'}";

//led
#define BLUE_LED_PIN 2

//DHT
#define DHTPIN 0     // what digital pin we're connected to
#define DHTTYPE DHT11   // DHT 11

//init
WiFiClient espClient;
PubSubClient client(espClient);
DHT dht(DHTPIN, DHTTYPE);


int reading_interval = 90000;
long lastMsg = 0;
float temperature = 0.0;
float humidity = 0.0;

void setup_wifi() {
  delay(10);

  Serial.println();
  Serial.print("Connecting to: ");
  Serial.println(wifi_ssid);

  WiFi.begin(wifi_ssid, wifi_password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println();
  Serial.println("WiFi connected, IP address: ");
  Serial.println(WiFi.localIP());
}

void reconnect() {
  while (!client.connected()) {// Loop until we're reconnected
    Serial.print("Attempting MQTT connection...");
    if (client.connect("ESP8266-1")) {
      Serial.println("MQTT connected");
      client.subscribe("ESP8266-1/inbox/#");
    } else {
      Serial.print("MQTT failed, rc=");
       Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      delay(5000);// Wait 5 seconds before retrying
    }
  }
}

String __get_current_time__(){
    #return String(millis()).c_str();
    return String(DateTime.now()).c_str();
}

String __get_topic__(String requestID){
    return "rpicenter/inbox/ESP8266-1/" + __get_current_time__() + "/" + requestID;
}

bool __publish_msg__(String topic, String msg){
    char topicArr[topic.length()+1];
    topic.toCharArray(topicArr, topic.length()+1);
    char msgArr[msg.length()+1];
    msg.toCharArray(msgArr, msg.length()+1);

    Serial.print("Message Published: ");
    Serial.print(topicArr);
    Serial.print(", Msg: ");
    Serial.print(msgArr);
    
    int result = client.publish(topicArr, msgArr);
    Serial.print(" ,Result: ");
    Serial.println(result);
}

void __publish_sensor_reading__() { // this method is for periodicaly send temp information to the rpicenter.
    String _humidity_message = "{'device_object_id':'ESP8266-1','parameter':'humidity','Unit':'%','value':" + String(humidity) + ",'reading_datetime':'" + __get_current_time__() + "'}";
    __publish_msg__("reading/ESP8266-1/humidity/%/" + __get_current_time__(), _humidity_message);

    String _temperature_message = "{'device_object_id':'ESP8266-1','parameter':'temperature','Unit':'C','value':" + String(temperature) + ",'reading_datetime':'" + __get_current_time__() + "'}";
    __publish_msg__("reading/ESP8266-1/temperature/C/" + __get_current_time__(), _temperature_message);
}

void get_temperature(String requestID) {
    __publish_msg__(__get_topic__(requestID), String(temperature) + "C");
}

void get_humidity(String requestID) {
    __publish_msg__(__get_topic__(requestID), String(humidity) + "%");
}

void get_current_time(String requestID) {
    __publish_msg__(__get_topic__(requestID), __get_current_time__());
}

void BlueLed_on(String requestID) {
    Serial.println("Running BlueLed_on");
    digitalWrite(BLUE_LED_PIN,LOW);
    __publish_msg__(__get_topic__(requestID), "ESP8266-1.BlueLed_on() ACK");
}

void BlueLed_off(String requestID) {
    Serial.println("Running BlueLed_off");
    digitalWrite(BLUE_LED_PIN,HIGH);
    __publish_msg__(__get_topic__(requestID), "ESP8266-1.BlueLed_off() ACK");
}

void get_commands(String requestID) {
    Serial.println("Running get_commands");// get_humidity BlueLed_on BlueLed_off
    __publish_msg__(__get_topic__(requestID), String("get_commands get_temperature"));
    //['get_commands','get_temperature','get_humidity','BlueLed_on','BlueLed_off']
}

void callback(char* topic, byte* payload, unsigned int length) {
  String _topic = String((char *)topic);
  String message = String((char *)payload);
  int lastslash = _topic.lastIndexOf('/');
  String requestID = _topic.substring(lastslash + 1);

  Serial.print("Message arrived: ");
  Serial.print(topic);
  Serial.print(", Msg: ");
  Serial.print(message);
  Serial.print(", requestID: ");
  Serial.println(requestID);

  // Switch on the LED if an 1 was received as first character
   if (message.startsWith("get_commands")) {
    get_commands(requestID);
  } else if (message.startsWith("get_temperature")) {
    get_temperature(requestID);
  } else if (message.startsWith("get_humidity")) {
    get_humidity(requestID);
  } else if (message.startsWith("BlueLed_on")) {
    BlueLed_on(requestID);
  } else if (message.startsWith("BlueLed_off")) {
    BlueLed_off(requestID);
  }else {
    __publish_msg__(__get_topic__(requestID), "ESP8266-1 Invalid Command");
  }
}

void get_dht_reading(){
    temperature = dht.readTemperature();
    humidity = dht.readHumidity();
    Serial.println("New temperature: " + String(temperature));
    Serial.println("New humidity: " + String(humidity));
}

void setup() {
  Serial.begin(115200);
  // led
  pinMode(BLUE_LED_PIN,OUTPUT);
  digitalWrite(BLUE_LED_PIN,LOW);
  //dht
  dht.begin();
  //Wifi
  wifi_station_set_hostname("ESP8266-1");
  setup_wifi();
  //MQTT
  client.setServer(mqtt_server, mqtt_port);
  client.setCallback(callback);

  get_dht_reading();
}

void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();

  long now = millis();
  if (now - lastMsg > reading_interval) {
    lastMsg = now;
    get_dht_reading();    
    __publish_sensor_reading__();
  }
}
