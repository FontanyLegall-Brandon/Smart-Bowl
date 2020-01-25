import paho.mqtt.client as mqtt
import os
from urllib.parse import urlparse
import schedule
import json
import smtplib

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

s = smtplib.SMTP(host='mail.hamlab.fr', port=587)
s.starttls()
s.login('smart-bowl@hamlab.fr', 'azerty1234%')


def sendEmail(name, email):
    msg = MIMEMultipart()  # create a message

    # setup the parameters of the message
    msg['From'] = 'smart-bowl@hamlab.fr'
    msg['To'] = email
    msg['Subject'] = "This is TEST"

    # add in the message body
    message = 'Salut ' + name + ', vous avez gagné un Iphone 10.'
    msg.attach(MIMEText(message, 'plain'))

    # send the message via the server set up earlier.
    s.send_message(msg)

    del msg


def sendToSmartBowl(msg):
    global mqttc
    mqttc.publish('SMARTBOWL', msg)

def sendToClient(msg):
    global mqttc
    mqttc.publish('CLIENT', msg)


def process_bowl_action(msg):
    if msg == "OPEN":
        print("MOCKUP : OPENING BOWL")
    elif msg == "CLOSE":
        print("MOCKUP : CLOSING BOWL")
    elif 'DROP' in msg:
        dose = msg[len(msg) - 1:]
        print('DROP ' + dose + ': DROPING FOOD')
    else:
        return
    sendToSmartBowl(msg)


def process_bowl_status(msg):
    if msg == "NO FOOD":
        print("sending mail")
        sendEmail('Brandon', 'brandon@fontany-legall.xyz')
    elif msg == "OPENED" or msg == "CLOSED":
        print("BOWLSTATUS: " + msg)
        sendToClient(msg)
    else:
        print("WUT")


def redirect_message(topic, qos, payload):
    payload = payload.decode('utf-8')
    print('RECEIVE topic="{}" qos="{}" \n\tpayload="{}"'.format(topic, qos, payload))

    if topic == "ACTION":
        process_bowl_action(payload)
    elif topic == "BOWLSTATUS":
        process_bowl_status(payload)


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
    schedule.run_pending()
    rc = mqttc.loop()
print("rc: " + str(rc))
print("rc_rasp: " + str(rc_rasp))