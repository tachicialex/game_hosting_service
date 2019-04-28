#!/bin/sh

# REMOVE LINES:
# delete containers:
# docker rm $(docker ps -a -q)
# delete images:
# docker rmi $(docker images -q)

# check if image exists:
exists=$(docker images -q airplaneservice)

# remove containers using that image:

# build the image if it does not exists:
if [ -z "$exists" ]; then
	echo $(docker build -f DockerFile -t airplaneservice .)
fi

# get the images id
image_id=$(docker images -q airplaneservice)

# get the ip of the database container:
db_container_ip=$(docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' airplane_database)

# run client, send script's first parameter(the service URL to client):
echo "Starting service: "
echo $(docker run --name=airplane_service $image_id ./AirplaneService.py $db_container_ip)


