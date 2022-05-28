#!/bin/bash
#******************************************
# Author:       Jason Zhao
# Email:        zhaoshundong@opsany.com
# Organization: OpsAny https://www.opsany.com/
# Description:  OpsAny Proxy Install Script
#******************************************

# Get Data/Time
CTIME=$(date "+%Y-%m-%d-%H-%M")

# Shell Envionment Variables
CDIR=$(pwd)
SHELL_NAME="proxy-install.sh"
SHELL_LOG="${CDIR}/${SHELL_NAME}.log"

# Shell Log Record
shell_log(){
    LOG_INFO=$1
    echo -e "\033[32m---------------- $CTIME ${SHELL_NAME} : ${LOG_INFO} ----------------\033[0m"
    echo "$CTIME ${SHELL_NAME} : ${LOG_INFO}" >> ${SHELL_LOG}
}

shell_warning_log(){
    LOG_INFO=$1
    echo -e "\033[33m---------------- $CTIME ${SHELL_NAME} : ${LOG_INFO} ----------------\033[0m"
    echo "$CTIME ${SHELL_NAME} : ${LOG_INFO}" >> ${SHELL_LOG}
}

shell_error_log(){
    LOG_INFO=$1
    echo -e "\031[32m---------------- $CTIME ${SHELL_NAME} : ${LOG_INFO} ----------------\033[0m"
    echo "$CTIME ${SHELL_NAME} : ${LOG_INFO}" >> ${SHELL_LOG}
}

# Install Inspection
if [ ! -f ./install.config ];then
      shell_error_log "Please Copy install.config and Change: cp install.config.example install.config"
      exit
else
    grep '^[A-Z]' install.config > install.env
    source ./install.env && rm -f install.env
    setenforce 0
fi

# Check Install requirement
install_check(){
  DOCKER_PID=$(ps aux | grep '/usr/bin/containerd' | grep -v 'grep' | wc -l)
  if [ ${DOCKER_PID} -lt 1 ];then
      shell_error_log "Please install and start docker first!!!"
      exit
  fi
}

# Install Initialize
install_init(){
    shell_log "Start: Install Init"
    mkdir -p ${INSTALL_PATH}/{uploads,conf,logs,prometheus-volume/conf,prometheus-volume/data}
    cd $CDIR
    /bin/cp -r ../install/conf ${INSTALL_PATH}/
    shell_log "End: Install Init"
}

prometheus_install(){
    # Prometheus
    shell_log "======Start Prometheus======"
    docker run -d --restart=always --name opsany-prometheus \
    -p 9090:9090 \
    -v ${INSTALL_PATH}/prometheus-volume/data/:/var/lib/prometheus \
    -v ${INSTALL_PATH}/prometheus-volume/conf/:/etc/prometheus/ \
    -v /etc/localtime:/etc/localtime:ro \
    ${PAAS_DOCKER_REG}/prometheus:v2.35.0
}
