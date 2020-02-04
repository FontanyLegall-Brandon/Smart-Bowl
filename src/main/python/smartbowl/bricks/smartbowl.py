import paho.mqtt.client as mqtt
from urlparse import urlparse
import json
import schedule
import motor
import camera
import supersonic

class Smartbowl:
    motor = None
    camera = None
    supersonic = None
    supersonicSchedule = 1

    def __init__(self, mqtt_rasp_url):
        self.motor = motor.Motor()
        self.camera = camera.Camera()
        self.supersonic = supersonic.Supersonic()

        self.shared_topics = ['test', 'bowl-action', 'picture', 'range-finder-signal']

        # Configure mqtt clients
        self.rasp_mqtt = mqtt.Client()

        url_rasp = urlparse(mqtt_rasp_url)

        # Connect
        self.rasp_mqtt.connect(url_rasp.hostname, url_rasp.port)
        self.register_callbacks()
        for topic in self.shared_topics:
            self.rasp_mqtt.subscribe(topic)

        self.start()


    def start(self):
        # Continue the network loop, exit when an error occurs
        rc_rasp = 0
        self.init_scheduled_tasks()
        while rc_rasp == 0:
            schedule.run_pending()
            rc_rasp = self.rasp_mqtt.loop()
        print("rc_rasp: " + str(rc_rasp))

    def init_scheduled_tasks(self):
        schedule.every(self.supersonicSchedule).seconds.do(self.publish_range_finder_signal)

    def register_callbacks(self):
        self.rasp_mqtt.on_message = self.on_message
        self.rasp_mqtt.on_connect = self.on_connect
        self.rasp_mqtt.on_publish = self.on_publish
        self.rasp_mqtt.on_subscribe = self.on_subscribe

    def process_bowl_action(self, payload):
        payload = json.loads(payload)
        if payload['ACTION'] == "OPEN":
            print("OPENING BOWL")
            self.motor.open()
        if payload['ACTION'] == "CLOSE":
            print("MOCKUP : CLOSING BOWL")
            self.motor.close()
        if payload['ACTION'] == "TAKE PICTURE":
            print("TAKING PICTURE")
            imageName = self.camera.capture()
            encoded = self.camera.encode(imageName)
            print(encoded)
            self.rasp_mqtt.publish('picture', encoded)


    def redirect_message(self, topic, qos, payload):
        payload = payload.decode('utf-8')
        print('RECEIVE topic="{}" qos="{}" \n\tpayload="{}"'.format(topic, qos, payload))

        if topic == "bowl-action":
            self.process_bowl_action(payload)
        if topic == "picture":
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
        print("supersonic : " + str(self.supersonic.detect()))
        self.rasp_mqtt.publish('range-finder-signal', str(self.supersonic.detect()))

Smartbowl(mqtt_rasp_url="mqtt://localhost:1883")