#! /bin/python3

from bricks.smartbowl import *

"""
Entry point of smartbowl
"""
if __name__ == "__main__":
    Smartbowl(mqtt_cloud_url="mqtt://ddlpfjur:xYB7g87hyXyF@hairdresser.cloudmqtt.com:18320",
                          mqtt_rasp_url="mqtt://localhost:1883")
