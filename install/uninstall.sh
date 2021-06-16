#!/bin/bash
source ./install.config
docker stop $(docker ps -qa)
docker rm -f $(docker ps -qa)
docker volume rm $(docker volume ls -q)
#docker images | grep ${PAAS_VERSION} | awk '{print $3}' | xargs docker rmi
rm -rf ${INSTALL_PATH}

