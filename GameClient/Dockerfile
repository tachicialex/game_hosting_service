FROM python:3.6-slim

MAINTAINER "andrei.tachici@stud.acs.upb.ro"

COPY . /app
WORKDIR /app

# Since Flask apps listen to port 5000  by default, we expose it
EXPOSE 5000

RUN pip3 install Flask
RUN pip3 install jsonrpcserver
RUN pip3 install jsonrpcclient
RUN pip install "jsonrpcclient[requests]"
RUN pip3 install flask-login

ENTRYPOINT [ "python3", "-u", "GameClient.py"]

