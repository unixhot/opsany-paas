#!/bin/bash
grep '^[A-Z]' install.config > install.env
source ./install.env && rm -f install.env
docker stop $(docker ps -qa)
docker rm -f $(docker ps -qa)
docker volume rm $(docker volume ls -q)
rm -rf ${INSTALL_PATH}
echo "===Manually remove the configuration content from /etc/rc.local======"
