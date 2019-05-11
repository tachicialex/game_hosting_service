FROM python:3.6-slim

MAINTAINER "andrei.tachici@stud.acs.upb.ro"

COPY . /app
WORKDIR /app

# expose lobby udp port
EXPOSE 5005

RUN pip3 install mysql-connector

ENTRYPOINT [ "python3", "-u", "GameLobby.py"]
