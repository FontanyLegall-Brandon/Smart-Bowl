import paho.mqtt.client as mqtt
import os
from urllib.parse import urlparse
import schedule
import json
from bricks.smartbowl import *

if __name__ == "__main__":
    Smartbowl(mqtt_cloud_url="mqtt://ddlpfjur:xYB7g87hyXyF@hairdresser.cloudmqtt.com:18320",
                          mqtt_rasp_url="mqtt://localhost:1883")