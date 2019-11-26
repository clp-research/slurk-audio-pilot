#!/usr/bin/env bash

# define name
OPENVIDU_CONTAINER="openvidu-recording-server"
echo $OPENVIDU_CONTAINER


# kill existing containers
docker kill "${OPENVIDU_CONTAINER}"
docker rm "${OPENVIDU_CONTAINER}"

# start openvidu server for recording audio
docker run -p 4443:4443 --name=$OPENVIDU_CONTAINER -e openvidu.secret=YOUR_SECRET -e openvidu.publicurl=https://localhost:4443/ -e openvidu.cdr=true -e server.port=4443 openvidu/openvidu-server-kms:2.11.0