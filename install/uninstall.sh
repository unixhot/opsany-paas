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

uninstall_paas(){
    echo -e "\033[32m---------------- Stop and remove PaaS Service ----------------\033[0m"
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
    docker stop opsany-base-mongodb && docker rm -f opsany-base-mongodb
    docker stop opsany-zabbix-web && docker rm -f opsany-zabbix-web
    docker stop opsany-zabbix-server-st2 && docker rm -f opsany-zabbix-server-st2
    docker stop opsany-zabbix-web-7.0.3 && docker rm -f opsany-zabbix-web-7.0.3
    docker stop opsany-zabbix-server-7.0.3 && docker rm -f opsany-zabbix-server-7.0.3
    docker stop opsany-zabbix-agent2 && docker rm -f opsany-zabbix-agent2
    docker stop opsany-zabbix-mysql8 && docker rm -f opsany-zabbix-mysql8
    docker stop opsany-devops-jenkins && docker rm -f opsany-devops-jenkins
    docker stop opsany-devops-nexus && docker rm -f opsany-devops-nexus
    rm -rf /tmp/alexanderzobnin-zabbix-app-4.3.1*
    grep '^[A-Z]' install.config > install.env
    source ./install.env && rm -f install.env
    rm -rf ${INSTALL_PATH}
    rm -f /opt/opsany-paas/saas/*.tar.gz
    echo -e "\033[32m---------------- PaaS Service Uninstall successfully  ----------------\033[0m"
}

uninstall_saas(){
    echo -e "\033[32m---------------- Stop and remove SaaS Service ----------------\033[0m"
    docker stop opsany-paas-proxy && docker rm -f opsany-paas-proxy
    docker stop opsany-saas-ce-rbac && docker rm -f opsany-saas-ce-rbac
    docker stop opsany-saas-ce-workbench && docker rm -f opsany-saas-ce-workbench
    docker stop opsany-saas-ce-cmdb && docker rm -f opsany-saas-ce-cmdb 
    docker stop opsany-saas-ce-control && docker rm -f opsany-saas-ce-control 
    docker stop opsany-saas-ce-job && docker rm -f opsany-saas-ce-job
    docker stop opsany-saas-ce-cmp && docker rm -f opsany-saas-ce-cmp
    docker stop opsany-saas-ce-bastion && docker rm -f opsany-saas-ce-bastion 
    docker stop opsany-saas-ce-monitor && docker rm -f opsany-saas-ce-monitor
    docker stop opsany-base-grafana && docker rm -f opsany-base-grafana
    docker stop opsany-saas-ce-devops && docker rm -f opsany-saas-ce-devops
    docker stop opsany-saas-ce-repo && docker rm -f opsany-saas-ce-repo
    docker stop opsany-saas-ce-pipeline && docker rm -f opsany-saas-ce-pipeline
    docker stop opsany-saas-ce-deploy && docker rm -f opsany-saas-ce-deploy
    docker stop opsany-saas-ce-llmops && docker rm -f opsany-saas-ce-llmops
    echo -e "\033[32m---------------- SaaS Service Uninstall successfully  ----------------\033[0m"
}

uninstall_k8s(){
    grep '^[A-Z]' install-k8s.config > install.env
    helm uninstall opsany-paas-paas -n opsany
    helm uninstall opsany-paas-login -n opsany
    helm uninstall opsany-paas-esb -n opsany
    helm uninstall opsany-paas-appengine -n opsany
    helm uninstall opsany-paas-openresty -n opsany
    helm uninstall opsany-paas-proxy -n opsany
    helm uninstall opsany-paas-websocket -n opsany
    helm uninstall opsany-saas-rbac -n opsany
    helm uninstall opsany-saas-workbench -n opsany
    helm uninstall opsany-saas-cmdb -n opsany
    helm uninstall opsany-saas-control -n opsany
    helm uninstall opsany-saas-job -n opsany
    helm uninstall opsany-saas-monitor -n opsany
    helm uninstall opsany-saas-cmp -n opsany
    helm uninstall opsany-saas-bastion -n opsany
    helm uninstall opsany-saas-devops -n opsany
    helm uninstall opsany-saas-dashboard -n opsany
    helm uninstall opsany-base-mysql -n opsany
    helm uninstall opsany-base-mongodb -n opsany
    helm uninstall opsany-base-redis -n opsany
    helm uninstall opsany-paas-grafana -n opsany
    helm uninstall opsany-paas-guacd -n opsany
    helm uninstall nfs-provisioner -n opsany
    kubectl delete pvc opsany-paas-grafana-data -n opsany
    kubectl delete pvc opsany-paas-esb-code -n opsany
    kubectl delete pvc opsany-uploads -n opsany
    kubectl delete pvc opsany-logs -n opsany
    kubectl delete sc nfs-sc-opsany
    source ./install.env && rm -f install.env
    kubectl delete -f ${INSTALL_PATH}/kubernetes/helm/opsany-paas/opsany-nfs.yaml -n opsany
    kubectl delete ns opsany
    rm -rf ${INSTALL_PATH}
    rm -rf /data/k8s-nfs/opsany-esb-code/*
    rm -rf /data/k8s-nfs/opsany-grafana-data/*
    rm -rf /data/k8s-nfs/opsany-logs/*
    rm -rf /data/k8s-nfs/opsany-proxy/*
    rm -rf /data/k8s-nfs/opsany-uploads/*
    echo -e "\033[32m---------------- I'll See You Again ----------------\033[0m"
}


# Main
main(){
    case "$1" in
	all)
        uninstall_paas
        uninstall_saas
		;;
    paas)
        uninstall_paas
        ;;
    saas)
        uninstall_saas
        ;;
    k8s)
        uninstall_k8s
        ;;
	help|*)
		echo $"Usage: $0 {all|saas|paas|k8s|help}"
	        ;;
    esac
}

main $1
