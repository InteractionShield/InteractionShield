#!/bin/sh

mkdir -p artifact/Intermediate/als
mkdir -p artifact/Intermediate/apps
mkdir -p artifact/Intermediate/config
mkdir -p artifact/Intermediate/log

mkdir -p artifact/Intermediate/IoTCOM
mkdir -p artifact/Intermediate/IoTSan

docker build -t interaction_shield infrastructure/
xhost +
docker run -it -e DISPLAY=$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix:rw -v ${PWD}:/InteractionShield interaction_shield
