#!/bin/sh

# remove images:
docker image rm -f gameclient
docker image rm -f gameservice

# build the game lobby image:

# build the game client image
sudo docker image build -t gameclient GameClient/

# build the game server image:
sudo docker image build -t gameservice GameService/
