#! /bin/python3

from bricks.smartbowl import *

"""
Entry point of smartbowl
"""
if __name__ == "__main__":
    Smartbowl(mqtt_rasp_url="mqtt://localhost:1883")