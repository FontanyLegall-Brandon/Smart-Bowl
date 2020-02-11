import paho.mqtt.client as mqtt
from urllib.parse import urlparse

# Define event callbacks
def on_connect(client, userdata, flags, rc):
    print("rc: " + str(rc))


def on_message(client, obj, msg):
    redirect_message(topic=msg.topic, qos=msg.qos, payload=msg.payload)
    print(msg.topic + " " + str(msg.qos) + " " + str(msg.payload))

def on_message_rasp(client, obj, msg):
    redirect_message(topic=msg.topic,qos=msg.qos, payload=msg.payload)
    print("RASP", msg.topic + " " + str(msg.qos) + " " + str(msg.payload))

def on_publish(client, obj, mid):
    print("mid: " + str(mid))


def on_subscribe(client, obj, mid, granted_qos):
    print("Subscribed: " + str(mid) + " " + str(granted_qos))


def on_log(client, obj, level, string):
    print(string)


mqttc = mqtt.Client()

mqttc.on_message = on_message
mqttc.on_connect = on_connect
mqttc.on_publish = on_publish
mqttc.on_subscribe = on_subscribe

# Uncomment to enable debug messages
# mqttc.on_log = on_log

os.environ.setdefault('CLOUDMQTT_URL', 'mqtt://ddlpfjur:xYB7g87hyXyF@hairdresser.cloudmqtt.com:18320')
os.environ.setdefault('CLOUDMQTT_URL_RASP', 'mqtt://localhost:1883')

# Parse CLOUDMQTT_URL (or fallback to localhost)
url_str = os.environ.get('CLOUDMQTT_URL', 'mqtt://localhost:1883')
url = urlparse(url_str)
topic = url.path[1:] or 'test'

# Connect
mqttc.username_pw_set(url.username, url.password)
mqttc.connect(url.hostname, url.port)


# Start subscribe, with QoS level 0
mqttc.subscribe(topic, 0)
mqttc.subscribe("ACTION", 1)
mqttc.subscribe("BOWLSTATUS", 2)

# Publish a message
# mqttc.publish(topic, "my message")

def job():
    global mqttc
    mqttc.publish('test', "0.25")


# schedule.every(1).seconds.do(job)

# Continue the network loop, exit when an error occurs
rc = 0
rc_rasp = 0
while rc == 0 and rc_rasp == 0:
    rc = mqttc.loop()
print("rc: " + str(rc))
print("rc_rasp: " + str(rc_rasp))