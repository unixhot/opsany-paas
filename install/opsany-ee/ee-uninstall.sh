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
if [ ! -f ../install.config ];then
      shell_error_log "Please Copy install.config and Change: cp install.config.example install.config"
      exit
else
    grep '^[A-Z]' ../install.config > install.env
    cat ./ee-install.config >> install.env
    source ./install.env && rm -f install.env
fi

uninstall_paas(){
    echo "===Stop and remove PaaS Service==="
    docker stop opsany-paas-paas && docker rm -f opsany-paas-paas
    docker stop opsany-paas-login && docker rm -f opsany-paas-login
    docker stop opsany-paas-esb && docker rm -f opsany-paas-esb
    docker stop opsany-paas-appengine && docker rm -f opsany-paas-appengine
    #docker stop opsany-paas-paasagent && docker rm -f opsany-paas-paasagent
    docker stop opsany-base-openresty && docker rm -f opsany-base-openresty
    docker stop opsany-paas-websocket && docker rm -f opsany-paas-websocket
    docker stop opsany-base-mysql && docker rm -f opsany-base-mysql
    docker stop opsany-base-redis && docker rm -f opsany-base-redis
    #docker stop opsany-base-rabbitmq && docker rm -f opsany-base-rabbitmq
    docker stop opsany-base-guacd && docker rm -f opsany-base-guacd
    docker stop opsany-base-grafana && docker rm -f opsany-base-grafana
    docker stop opsany-base-mongodb && docker rm -f opsany-base-mongodb
    docker stop opsany-base-prometheus-server  && docker rm -f opsany-base-prometheus-server
    docker stop opsany-base-consul  && docker rm -f opsany-base-consul
    rm -rf ${INSTALL_PATH}
    rm -f /opt/opsany-paas/saas/*.tar.gz
}

uninstall_saas(){
    echo "===Stop and remove SaaS Service==="
    docker stop opsany-paas-proxy && docker rm -f opsany-paas-proxy
    docker stop opsany-saas-ce-rbac && docker rm -f opsany-saas-ce-rbac
    docker stop opsany-saas-ce-workbench && docker rm -f opsany-saas-ce-workbench
    docker stop opsany-saas-ce-cmdb && docker rm -f opsany-saas-ce-cmdb 
    docker stop opsany-saas-ce-control && docker rm -f opsany-saas-ce-control 
    docker stop opsany-saas-ce-job && docker rm -f opsany-saas-ce-job
    docker stop opsany-saas-ce-monitor && docker rm -f opsany-saas-ce-monitor
    docker stop opsany-saas-ce-cmp && docker rm -f opsany-saas-ce-cmp
    docker stop opsany-saas-ce-bastion && docker rm -f opsany-saas-ce-bastion 
    docker stop opsany-saas-ce-devops && docker rm -f opsany-saas-ce-devops
    docker stop opsany-saas-ce-pipeline && docker rm -f opsany-saas-ce-pipeline
    docker stop opsany-saas-ce-deploy && docker rm -f opsany-saas-ce-deploy
    docker stop opsany-saas-ce-repo && docker rm -f opsany-saas-ce-repo
    docker stop opsany-saas-ee-event && docker rm -f opsany-saas-ee-event
    docker stop opsany-saas-ee-auto && docker rm -f opsany-saas-ee-auto
    docker stop opsany-saas-ee-k8s && docker rm -f opsany-saas-ee-k8s
    docker stop opsany-saas-ee-prom && docker rm -f opsany-saas-ee-prom
    docker stop opsany-saas-ee-kbase && docker rm -f opsany-saas-ee-kbase
    docker stop opsany-saas-ee-log && docker rm -f opsany-saas-ee-log
    docker stop opsany-saas-ee-apm && docker rm -f opsany-saas-ee-apm
}


# Main
main(){
    case "$1" in
	uninstall)
        uninstall_paas
        uninstall_saas
		;;
    paas)
        uninstall_paas
        ;;
    saas)
        uninstall_saas
        ;;
	help|*)
		echo $"Usage: $0 {uninstall|saas|paas|help}"
	        ;;
    esac
}

main $1
