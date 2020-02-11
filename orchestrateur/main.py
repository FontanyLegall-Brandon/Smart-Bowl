import paho.mqtt.client as mqtt
from urllib.parse import urlparse
import requests
import schedule
from core.calendarService import CalendarService
from core.notificationService import NotificationService

notificationService = NotificationService('tmahe.pro@gmail.com', "eivx9hcgxq@pomail.net")
calendarService = CalendarService("https://calendar.google.com/calendar/ical/5mvk2qo4dk7kp1vnum277hfar8%40group.calendar.google.com/public/basic.ics")

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
    if msg == "NO_FOOD":
        print("sending mail")
        notificationService.sendNotification("[SmartBowl] Votre gamelle est presque vide", """Votre gamelle SmartBowl vous envoi un signal inquiétant !\n
                                                                                           Celle-ci est presque vide, pensez à la remplir pour le bien-être de votre chat.""")
    if msg == "OPENED":
        notificationService.sendNotification("[SmartBowl] Ouverture de votre gammelle", """Votre gamelle SmartBowl vous envoi un signal !\n
                                                                                                   Celle-ci vient à peine de s'ouvrir.""")
    if msg == "CLOSED":
        notificationService.sendNotification("[SmartBowl] Fermeture de votre gammelle", """Votre gamelle SmartBowl vous envoi un signal !\n
                                                                                        Pour des raisons budgetaires, votre gammelle vient de se fermer, pour le plus grand désespoir de votre compagon.""")
    else:
        print("WUT")

def process_image(base64img):
    url = 'https://catveyor.appspot.com/post-image'
    requests.post(url, data=base64img, headers={'Content-Type': 'text/plain'})
    print("IMAGE UPDATED")


def redirect_message(topic, qos, payload):
    print('RECEIVE topic="{}" qos="{}" \n\tpayload="{}"'.format(topic, qos, payload))

    if topic == "smartbowl/camera-image":
        process_image(payload)
    elif topic == "smartbowl/bowl-state":
        process_bowl_status(payload.decode('utf-8'))


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

# Connect
mqtt_rasp = mqtt.Client()
mqtt_rasp.on_message = on_message
mqtt_rasp.on_connect = on_connect
mqtt_rasp.on_publish = on_publish
mqtt_rasp.on_subscribe = on_subscribe

mqtt_rasp.connect("192.168.43.233", 1883)

# Start subscribe, with QoS level 0
mqtt_rasp.subscribe('smartbowl/camera-image', 0)
mqtt_rasp.subscribe('smartbowl/bowl-state/update', 0)

#cloudmqtt
url_mqtt_cloud = urlparse("mqtt://ddlpfjur:xYB7g87hyXyF@hairdresser.cloudmqtt.com:18320")

cloud_mqtt = mqtt.Client()
cloud_mqtt.on_message = on_message
cloud_mqtt.on_connect = on_connect
cloud_mqtt.on_publish = on_publish
cloud_mqtt.on_subscribe = on_subscribe

print(url_mqtt_cloud.username)
print(url_mqtt_cloud.password)
print(url_mqtt_cloud.hostname)
print(url_mqtt_cloud.port)

cloud_mqtt.username_pw_set(url_mqtt_cloud.username, url_mqtt_cloud.password)
cloud_mqtt.connect(url_mqtt_cloud.hostname, url_mqtt_cloud.port)

cloud_mqtt.subscribe('test')

def sendBowlNewStatus():
    calendarStatus = calendarService.getCurrentEvent()
    if calendarStatus == "CLOSE":
        mqtt_rasp.publish("smartbowl/bowl-state", "SET_CLOSE")
    if calendarStatus == "OPEN":
        mqtt_rasp.publish("smartbowl/bowl-state", "SET_OPEN")

schedule.every(5).seconds.do(sendBowlNewStatus)

# Continue the network loop, exit when an error occurs
rc = 0
rc_rasp = 0
while rc == 0 and rc_rasp == 0:
    schedule.run_pending()
    rc_rasp = mqtt_rasp.loop()
    rc = cloud_mqtt.loop()