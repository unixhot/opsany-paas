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
        for i in `ls ${INSTALL_PATH}/logs/workbench`;do echo "" > ${INSTALL_PATH}/logs/workbench/$i;done
	;;
    job) 
        for i in `ls ${INSTALL_PATH}/logs/job`;do echo "" > ${INSTALL_PATH}/logs/job/$i;done
	;;
    monitor) 
        for i in `ls ${INSTALL_PATH}/logs/monitor`;do echo "" > ${INSTALL_PATH}/logs/monitor/$i;done
	;;
    cmp) 
        for i in `ls ${INSTALL_PATH}/logs/cmp`;do echo "" > ${INSTALL_PATH}/logs/cmp/$i;done
	;;
    cmdb) 
        for i in `ls ${INSTALL_PATH}/logs/cmdb`;do echo "" > ${INSTALL_PATH}/logs/cmdb/$i;done
	;;
    bastion) 
        for i in `ls ${INSTALL_PATH}/logs/bastion`;do echo "" > ${INSTALL_PATH}/logs/bastion/$i;done
	;;
    devops) 
        for i in `ls ${INSTALL_PATH}/logs/devops`;do echo "" > ${INSTALL_PATH}/logs/devops/$i;done
	;;
    control) 
        for i in `ls ${INSTALL_PATH}/logs/control`;do echo "" > ${INSTALL_PATH}/logs/control/$i;done
	;;
    all)
        for i in `ls ${INSTALL_PATH}/logs/*.log`;do echo "" > $i;done
        for i in `ls ${INSTALL_PATH}/logs/rbac`;do echo "" > ${INSTALL_PATH}/logs/rbac/$i;done
        for i in `ls ${INSTALL_PATH}/logs/workbench`;do echo "" > ${INSTALL_PATH}/logs/workbench/$i;done
        for i in `ls ${INSTALL_PATH}/logs/job`;do echo "" > ${INSTALL_PATH}/logs/job/$i;done
        for i in `ls ${INSTALL_PATH}/logs/monitor`;do echo "" > ${INSTALL_PATH}/logs/monitor/$i;done
        for i in `ls ${INSTALL_PATH}/logs/cmp`;do echo "" > ${INSTALL_PATH}/logs/cmp/$i;done
        for i in `ls ${INSTALL_PATH}/logs/cmdb`;do echo "" > ${INSTALL_PATH}/logs/cmdb/$i;done
        for i in `ls ${INSTALL_PATH}/logs/bastion`;do echo "" > ${INSTALL_PATH}/logs/bastion/$i;done
        for i in `ls ${INSTALL_PATH}/logs/devops`;do echo "" > ${INSTALL_PATH}/logs/devops/$i;done
        for i in `ls ${INSTALL_PATH}/logs/control`;do echo "" > ${INSTALL_PATH}/logs/control/$i;done
        for i in `ls ${INSTALL_PATH}/logs/llmops`;do echo "" > ${INSTALL_PATH}/logs/llmops/$i;done
        for i in `ls ${INSTALL_PATH}/logs/devops`;do echo "" > ${INSTALL_PATH}/logs/devops/$i;done
        for i in `ls ${INSTALL_PATH}/logs/pipeline`;do echo "" > ${INSTALL_PATH}/logs/pipeline/$i;done
        for i in `ls ${INSTALL_PATH}/logs/repo`;do echo "" > ${INSTALL_PATH}/logs/repo/$i;done
        for i in `ls ${INSTALL_PATH}/logs/deploy`;do echo "" > ${INSTALL_PATH}/logs/deploy/$i;done
        ;;
	help|*)
	    echo $"Usage: $0 {rbac|workbench|cmdb|control|job|monitor|cmp|bastion|devops|dashboard|all|help}"
	    ;;
    esac
}

main $1 
