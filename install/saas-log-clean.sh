#!/bin/bash
#******************************************
# Author:       Jason Zhao
# Email:        zhaoshundong@opsany.com
# Organization: OpsAny https://www.opsany.com/
# Description:  OpsAny SAAS Community Edition Install Script
#******************************************

# Data/Time Variables
CTIME=$(date "+%Y-%m-%d-%H-%M")

# Shell Envionment Variables
CDIR=$(pwd)
SHELL_NAME="opsany-log-clean.sh"
SHELL_LOG="${SHELL_NAME}.log"

# Shell Log Record
shell_log(){
    # Show green
    LOG_INFO=$1
    echo -e "\033[32m---------------- $CTIME ${SHELL_NAME} : ${LOG_INFO} ----------------\033[0m"
    echo "$CTIME ${SHELL_NAME} : ${LOG_INFO}" >> ${SHELL_LOG}
}

shell_warning_log(){
    # Show yellow
    LOG_INFO=$1
    echo -e "\033[33m---------------- $CTIME ${SHELL_NAME} : ${LOG_INFO} ----------------\033[0m"
    echo "$CTIME ${SHELL_NAME} : ${LOG_INFO}" >> ${SHELL_LOG}
}

shell_error_log(){
    # Show red
    LOG_INFO=$1
    echo -e "\033[31m---------------- $CTIME ${SHELL_NAME} : ${LOG_INFO} ----------------\033[0m"
    echo "$CTIME ${SHELL_NAME} : ${LOG_INFO}" >> ${SHELL_LOG}
}

# Install Inspection
if [ ! -f ./install.config ];then
      shell_error_log "Please Change Directory to ${INSTALL_PATH}/install"
      exit
else
    grep '^[A-Z]' install.config > install.env
    source ./install.env && rm -f install.env
fi


# Main
main(){
    case "$1" in
    rbac) 
        for i in `ls ${INSTALL_PATH}/logs/rbac`;do echo "" > ${INSTALL_PATH}/logs/rbac/$i;done
	;;
    workbench) 
        for i in `ls ${INSTALL_PATH}/logs/rbac`;do echo "" > ${INSTALL_PATH}/logs/workbench/$i;done
	;;
    all)
        install_init
        mongodb_init
        proxy_install
        saas_monitor_deploy
        saas_devops_deploy
        saas_base_init
        admin_password_init
        ;;
	help|*)
	    echo $"Usage: $0 {base|monitor|devops|all|help}"
	    ;;
    esac
}

main $1 
