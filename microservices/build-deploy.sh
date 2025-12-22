HUB=pechristakos

# build/deploy plugin-updater
MICROSERVICE_NAME=minecraft-plugin-updater
TAG=latest
docker build -t $HUB/$MICROSERVICE_NAME/$TAG plugin-updater
docker push $HUB/$MICROSERVICE_NAME:$TAG