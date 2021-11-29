import paho.mqtt.client as mqtt
import socket
from app import *
from datetime import datetime,timezone
from app import message

def log(message):
    s = datetime.now(timezone.utc).strftime("%x %X")+":"+message
    if debug_sock is None:
        print(s)
    else:
        debug_sock.send(s.encode('utf-8'))

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    log("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    for topic in topics_to_sub:
        client.subscribe(topic+"/#")

def on_disconnect(client, userdata, flags, rc):
    log("disconnected from server")

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    payload = msg.payload.decode("utf-8")
    log(msg.topic+" "+payload)
    m = message.message(MQTT_SERVER+msg.topic,payload)
    messages.append(m)
    

def process(msg):
    #check if message topic is already registered in the db
    if not msg.is_known_by_db():
        message.topic_db.new_topic(msg.topic,msg.payload)
    #store payload in db
    with Session() as session:
        try:
            session.add(msg.to_db_format())
            session.commit()
        except:
            log("Invlid payload format!")
    #FIXME: no payload structure validation is made against the registered format
    
MQTT_SERVER="127.0.0.1"
MQTT_PORT=1883
#connect to MQTT broker
client = mqtt.Client()
client.on_connect = on_connect
client.on_disconnect = on_disconnect
client.on_message = on_message

client.connect(MQTT_SERVER, MQTT_PORT, 60)

#debug_sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
#debug_sock.connect(("192.168.8.200",50000))
debug_sock = None

#topics to subscribe to
topics_to_sub=["/test","/test-json","/test-json-date","/test-csv-date"]

#messages queued for processing
messages=[]

#mqtt loop in a thread
client.loop_start()

run = True
while run:
    #loop over all received messages
    while len(messages)>0:
        process(messages[0])
        messages.pop(0)

client.loop_stop()
