#!/bin/bash

#create certificate used by registry
mkdir -p certs
if [ ! -f cert/server.key ] & [ ! -f certs/server.crt ]; then
    openssl req -subj '/CN=localhost/O=Registry Demo/C=US' -new -newkey rsa:2048 -days 365 -nodes -x509 -keyout certs/server.key -out certs/server.crt
fi

DOCKER_IP="0.0.0.0"
if [ "$(uname)" == "Darwin" ]; then
    DOCKER_IP="$(docker-machine ip default)"
fi

export DOCKER_IP

docker-compose build
docker-compose up -d
