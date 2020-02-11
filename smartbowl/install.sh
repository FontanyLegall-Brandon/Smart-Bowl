#! /bin/bash

## BUILD mqtt mosquitto brocker

sudo apt-get update -y
sudo apt-get install build-essential python quilt python-setuptools python3 -y
sudo apt-get install libssl-dev -y
sudo apt-get install cmake -y
sudo apt-get install libc-ares-dev -y
sudo apt-get install uuid-dev -y
sudo apt-get install daemon -y
sudo apt-get install libwebsockets-dev -y

wget http://mosquitto.org/files/source/mosquitto-1.4.10.tar.gz
tar zxvf mosquitto-1.4.10.tar.gz
cd mosquitto-1.4.10/

sudo sed -i 's/WITH_WEBSOCKETS:=no/WITH_WEBSOCKETS:=yes/g' config.mk

NB_PROC=$(cat /proc/cpuinfo | grep processor | wc -l)

make -j $NB_PROC
sudo make install
sudo cp ../etc/mosquitto/mosquitto.conf /etc/mosquitto

