import paho.mqtt.client as mqtt
from urllib.parse import urlparse
import logging
import json
import random
import schedule

class Smartbowl:
    def __init__(self, mqtt_cloud_url, mqtt_rasp_url):
        self.shared_topics = ['test', 'bowl-action']

        # Configure mqtt clients
        self.cloud_mqtt = mqtt.Client()
        self.rasp_mqtt = mqtt.Client()

        url = urlparse(mqtt_cloud_url)
        url_rasp = urlparse(mqtt_rasp_url)

        # Connect
        self.cloud_mqtt.username_pw_set(url.username, url.password)
        self.cloud_mqtt.connect(url.hostname, url.port)
        self.rasp_mqtt.connect(url_rasp.hostname, url_rasp.port)
        self.register_callbacks()
        for topic in self.shared_topics:
            self.cloud_mqtt.subscribe(topic)
            self.rasp_mqtt.subscribe(topic)

        self.start()

    def start(self):
        # Continue the network loop, exit when an error occurs
        rc = 0
        rc_rasp = 0
        while rc == 0 and rc_rasp == 0:
            schedule.run_pending()
            rc = self.cloud_mqtt.loop()
            rc_rasp = self.rasp_mqtt.loop()
        print("rc: " + str(rc))
        print("rc_rasp: " + str(rc_rasp))

    def init_scheduled_tasks(self):
        schedule.every(30).seconds.do(self.publish_range_finder_signal)

    def register_callbacks(self):
        self.cloud_mqtt.on_message = self.on_message
        self.cloud_mqtt.on_connect = self.on_connect
        self.cloud_mqtt.on_publish = self.on_publish
        self.cloud_mqtt.on_subscribe = self.on_subscribe

        self.rasp_mqtt.on_message = self.on_message
        self.rasp_mqtt.on_connect = self.on_connect
        self.rasp_mqtt.on_publish = self.on_publish
        self.rasp_mqtt.on_subscribe = self.on_subscribe

    def process_bowl_action(self, payload):
        payload = json.loads(payload)
        if payload['ACTION'] == "OPEN":
            print("MOCKUP : OPENING BOWL")
        if payload['ACTION'] == "CLOSE":
            print("MOCKUP : CLOSING BOWL")

    def redirect_message(self, topic, qos, payload):
        payload = payload.decode('utf-8')
        print('RECEIVE topic="{}" qos="{}" \n\tpayload="{}"'.format(topic, qos, payload))

        if topic == "bowl-action":
            self.process_bowl_action(payload)

    def on_connect(self, client, userdata, flags, rc):
        print("rc: " + str(rc))

    def on_message(self, client, obj, msg):
        self.redirect_message(topic=msg.topic, qos=msg.qos, payload=msg.payload)
        print(msg.topic + " " + str(msg.qos) + " " + str(msg.payload))

    def on_publish(self, client, obj, mid):
        print("mid: " + str(mid))

    def on_subscribe(self, client, obj, mid, granted_qos):
        print("Subscribed: " + str(mid) + " " + str(granted_qos))

    def on_log(self, client, obj, level, string):
        print(string)

    def publish_range_finder_signal(self):
        self.cloud_mqtt.publish('range-finder-signal', random.randint(0,10))
        self.rasp_mqtt.publish('range-finder-signal', random.randint(0,10))

Smartbowl(mqtt_cloud_url="mqtt://ddlpfjur:xYB7g87hyXyF@hairdresser.cloudmqtt.com:18320",
                          mqtt_rasp_url="mqtt://localhost:1883")