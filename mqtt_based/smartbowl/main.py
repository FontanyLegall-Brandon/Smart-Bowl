# Copyright (c) 2010,2011 Roger Light <roger@atchoo.org>
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice,
#   this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#   notice, this list of conditions and the following disclaimer in the
#   documentation and/or other materials provided with the distribution.
# 3. Neither the name of mosquitto nor the names of its
#   contributors may be used to endorse or promote products derived from
#   this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

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


def process_send_email(msg):
    if msg == "NO FOOD":
        print("sending mail")
        sendEmail('Brandon', 'brandon@fontany-legall.xyz')


def redirect_message(topic, qos, payload):
    payload = payload.decode('utf-8')
    print('RECEIVE topic="{}" qos="{}" \n\tpayload="{}"'.format(topic, qos, payload))

    if topic == "ACTION":
        process_bowl_action(payload)
    elif topic == "BOWLSTATUS":
        process_send_email(payload)


# Define event callbacks
def on_connect(client, userdata, flags, rc):
    print("rc: " + str(rc))


def on_message(client, obj, msg):
    redirect_message(topic=msg.topic, qos=msg.qos, payload=msg.payload)
    print(msg.topic + " " + str(msg.qos) + " " + str(msg.payload))


def on_publish(client, obj, mid):
    print("mid: " + str(mid))


def on_subscribe(client, obj, mid, granted_qos):
    print("Subscribed: " + str(mid) + " " + str(granted_qos))


def on_log(client, obj, level, string):
    print(string)


mqttc = mqtt.Client()
# Assign event callbacks
mqttc.on_message = on_message
mqttc.on_connect = on_connect
mqttc.on_publish = on_publish
mqttc.on_subscribe = on_subscribe

# Uncomment to enable debug messages
# mqttc.on_log = on_log

os.environ.setdefault('CLOUDMQTT_URL', 'mqtt://ddlpfjur:xYB7g87hyXyF@hairdresser.cloudmqtt.com:18320')

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
while rc == 0:
    schedule.run_pending()
    rc = mqttc.loop()
print("rc: " + str(rc))