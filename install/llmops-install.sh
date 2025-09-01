#!/bin/bash
#******************************************
# Author:       Jason Zhao
# Email:        zhaoshundong@opsany.com
# Organization: OpsAny https://www.opsany.com/
# Description:  OpsAI Install Script
#******************************************

# Data/Time
CTIME=$(date "+%Y-%m-%d-%H-%M")

# Shell Envionment Variables
CDIR=$(pwd)
SHELL_NAME="llmops-install.sh"
SHELL_LOG="${SHELL_NAME}.log"

# Install Inspection
if [ ! -f ./install.config ];then
      echo "Please Change Directory to ${INSTALL_PATH}/install"
      exit
else
    grep '^[A-Z]' install.config > install.env
    source ./install.env && rm -f install.env
    if [ -z "$ADMIN_PASSWORD" ];then
        source ${INSTALL_PATH}/conf/.passwd_env
    fi
fi

# Shell Log Record
shell_log(){
    LOG_INFO=$1
    echo "----------------$CTIME ${SHELL_NAME} : ${LOG_INFO}----------------"
    echo "$CTIME ${SHELL_NAME} : ${LOG_INFO}" >> ${SHELL_LOG}
}

# Check Install requirement
install_init(){
    shell_log "=====Begin: Init======"
    mkdir -p ${INSTALL_PATH}/{ollama-volume}
}

ollama_install(){
    shell_log "=====Ollama: Start Ollama======"
    docker run -d --restart=always --name opsany-base-ollama \
    -p 8020:11434 -v ${INSTALL_PATH}/ollama-volume:/root/.ollama \
    docker.m.daocloud.io/ollama/ollama:0.9.3
}

opsai_uninstall(){
    shell_log "=====Uninstall======"
    docker stop opsany-ollama
    docker rm opsany-ollama
    rm -rf ${INSTALL_PATH}/{ollama-volume}
}

# Main
main(){
    case "$1" in
    install)
        install_init
        ollama_install
        ;;
    uninstall)
        zabbix_uninstall
        ;;
        help|*)
                echo $"Usage: $0 {install|uninstall|help}"
                ;;
esac
}

main $1
