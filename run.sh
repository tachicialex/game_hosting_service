#!/bin/sh

# remove images:
docker image rm -f gameclient
docker image rm -f gameservice
docker image rm -f gamelobby

# build the game lobby image:
sudo docker image build -t gamelobby GameLobby/

# build the game client image
sudo docker image build -t gameclient GameClient/

# build the game server image:
sudo docker image build -t gameservice GameService/
