import json
import threading

import paho.mqtt.client as mqtt
from urllib.parse import urlparse
import requests
import schedule
from core.calendarService import CalendarService
from core.notificationService import NotificationService
import datetime

schedules_jobs = {}
__BOWL_CLOSE_LOCK__ = False
__BOWL_OPEN_LOCK__ = False

notificationService = NotificationService('tmahe.pro@gmail.com', "eivx9hcgxq@pomail.net")
calendarService = CalendarService("https://calendar.google.com/calendar/ical/5mvk2qo4dk7kp1vnum277hfar8%40group.calendar.google.com/public/basic.ics")

def run_threaded(job_func):
    job_thread = threading.Thread(target=job_func)
    job_thread.start()

def sendToSmartBowl(msg):
    global mqttc
    mqtt_rasp.publish('SMARTBOWL', msg)

def sendToClient(msg):
    global mqttc
    cloud_mqtt.publish('CLIENT', msg)

def open_bowl_job():
    global __BOWL_CLOSE_LOCK__
    print("Running scheduled open command")
    __BOWL_CLOSE_LOCK__ = False
    process_bowl_action("OPEN")
    return schedule.CancelJob

def close_bowl_job():
    global __BOWL_OPEN_LOCK__
    print("Running scheduled close command")
    __BOWL_OPEN_LOCK__ = False
    process_bowl_action("CLOSE")
    return schedule.CancelJob

def drop_job(dose):
    process_bowl_action("DROP {}".format(dose))

def process_bowl_action(msg):
    if msg == "OPEN":
        mqtt_rasp.publish("smartbowl/bowl-state", "SET_OPEN")
    elif msg == "CLOSE":
       mqtt_rasp.publish("smartbowl/bowl-state", "SET_CLOSE")
    elif 'DROP' in msg:
        mqtt_rasp.publish("smartbowl/bowl-state", "SET_CLOSE")
        print(msg + ': DROPING FOOD')
        mqtt_rasp.publish("smartbowl/bowl-state", msg)
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

def process_user_commands(payload):
    global __BOWL_CLOSE_LOCK__
    global __BOWL_OPEN_LOCK__
    j_object = json.loads(payload)
    print(j_object)
    if j_object['action'] == "DROP":
        count = j_object['dose']
        drop_job(count)

    if j_object['action'] == "OPEN":
        __BOWL_OPEN_LOCK__ = True
        __BOWL_CLOSE_LOCK__ = False
        open_duration_minutes = j_object['duration']
        delayed = datetime.datetime.now() + datetime.timedelta(minutes=open_duration_minutes)

        run_threaded(open_bowl_job)

        close_job = schedule.every().day.at("{}:{}:{}".format(delayed.hour,
                                                              delayed.minute,
                                                              delayed.second)).do(run_threaded, close_bowl_job)
        if 'open_job' in schedules_jobs.keys():
            # remove previous open command
            schedule.cancel_job(schedules_jobs['open_job'])
            schedules_jobs.pop('open_job')

        if 'close_job' in schedules_jobs.keys():
            # remove previous close command
            schedule.cancel_job(schedules_jobs['close_job'])
            schedules_jobs.pop('close_job')

        schedules_jobs['close_job'] = close_job

    if j_object['action'] == "CLOSE":

        __BOWL_CLOSE_LOCK__ = True
        print("CLOSE LOCK UPDATE", __BOWL_CLOSE_LOCK__)
        __BOWL_OPEN_LOCK__ = False
        open_duration_minutes = j_object['duration']

        delayed = datetime.datetime.now() + datetime.timedelta(minutes=open_duration_minutes)

        run_threaded(close_bowl_job)

        open_job = schedule.every().day.at("{}:{}:{}".format(delayed.hour,
                                                              delayed.minute,
                                                              delayed.second)).do(run_threaded, open_bowl_job)

        # release lock

        if 'close_job' in schedules_jobs.keys():
            schedule.cancel_job(schedules_jobs['close_job'])
            schedules_jobs.pop('close_job')

        if 'open_job' in schedules_jobs.keys():
            schedule.cancel_job(schedules_jobs['open_job'])
            schedules_jobs.pop('open_job')

        schedules_jobs['open_job'] = open_job


def redirect_message(topic, qos, payload):
    print('RECEIVE topic="{}" qos="{}" \n\tpayload="{}"'.format(topic, qos, payload))

    if topic == "smartbowl/camera-image":
        process_image(payload)
    elif topic == "smartbowl/bowl-state/update":
        process_bowl_status(payload.decode('utf-8'))
    elif topic == "smartbowl/commands":
        process_user_commands(payload.decode('utf-8'))


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

try:
    mqtt_rasp.connect("raspberrypi.local", 1883)
except:
    print("DEV MODE - RASP UNREACHABLE")
    print("MQTT_RASP REDIRECTED TO localhost")
    mqtt_rasp.connect("localhost", 1883)
    print("Connection to raspberrypi not found")

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

try:
    cloud_mqtt.username_pw_set(url_mqtt_cloud.username, url_mqtt_cloud.password)
    cloud_mqtt.connect(url_mqtt_cloud.hostname, url_mqtt_cloud.port)
except:
    print("Connection to cloudmqtt not found")



cloud_mqtt.subscribe('smartbowl/commands')

def sendBowlNewStatus():
    global __BOWL_CLOSE_LOCK__
    global __BOWL_OPEN_LOCK__
    print(schedules_jobs)
    calendarStatus = calendarService.getCurrentEvent()
    print("CLOSE LOCK :", __BOWL_CLOSE_LOCK__)
    print("OPEN LOCK :", __BOWL_OPEN_LOCK__)
    if calendarStatus == "CLOSE" and not __BOWL_OPEN_LOCK__:
        mqtt_rasp.publish("smartbowl/bowl-state", "SET_CLOSE")
    if calendarStatus == "OPEN" and not __BOWL_CLOSE_LOCK__:
        mqtt_rasp.publish("smartbowl/bowl-state", "SET_OPEN")

schedule.every(10).seconds.do(sendBowlNewStatus)

# Continue the network loop, exit when an error occurs
rc = 0
rc_rasp = 0

while True:
    schedule.run_pending()

    rc_rasp = mqtt_rasp.loop()
    cloud_mqtt.loop()

    if rc_rasp != 0:
        mqtt_rasp.connect("raspberrypi.local", 1883)
