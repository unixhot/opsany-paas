#!/bin/bash
#******************************************
# Author:       Jason Zhao
# Email:        zhaoshundong@opsany.com
# Organization: OpsAny https://www.opsany.com/
# Description:  OpsAny Uninstall Script
#******************************************

# Get Data/Time
CTIME=$(date "+%Y-%m-%d-%H-%M")

# Shell Envionment Variables
CDIR=$(pwd)
SHELL_NAME="uninstall.sh"
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
fi

uninstall_paas(){
    echo "===Stop all containers==="
    docker stop $(docker ps -qa)

    echo "===Remove all containers==="
    docker rm -f $(docker ps -qa)
    docker volume rm $(docker volume ls -q)
    
    echo "===Remove Install file==="
    rm -rf ${INSTALL_PATH}
    rm -f /opt/opsany-paas/saas/*.tar.gz
    
    echo "===Autl remove the configuration content from /etc/rc.local==="
    sed -i '/saas-restart/d' /etc/rc.local
}


# Main
main(){
    case "$1" in
	uninstall)
        uninstall_paas
		;;
	help|*)
		echo $"Usage: $0 {uninstall|help}"
	        ;;
    esac
}

main $1
