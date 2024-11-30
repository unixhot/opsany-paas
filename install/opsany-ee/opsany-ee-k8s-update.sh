#!/bin/bash
#******************************************
# Author:       Jason Zhao
# Email:        zhaoshundong@opsany.com
# Organization: OpsAny https://www.opsany.com/
# Description:  OpsAny SAAS Enterprise Edition Update Script
#******************************************

# Data/Time Variables
CTIME=$(date "+%Y-%m-%d-%H-%M")

# Shell Envionment Variables
CDIR=$(pwd)
SHELL_NAME="opsany-ee-update.sh"
SHELL_LOG="${SHELL_NAME}.log"
ADMIN_PASSWORD=""

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
if [ ! -f ../install-k8s.config ];then
      shell_error_log "Please Change Directory to ${INSTALL_PATH}/install"
      exit
else
    grep '^[A-Z]' ../install-k8s.config > install.env
    source ./install.env && rm -f install.env
    if [ -z "$ADMIN_PASSWORD" ];then
        source ${INSTALL_PATH}/conf/.passwd_env
    fi
fi

saas_k8s_update(){
    shell_log "======Update k8s======"
    # Modify configuration
    /bin/cp -r ../conf/opsany-saas/k8s/* ${INSTALL_PATH}/conf/opsany-saas/k8s/
    K8S_SECRET_KEY=$(cat ${INSTALL_PATH}/conf/.k8s_secret_key)
    sed -i "s/DOMAIN_NAME/${DOMAIN_NAME}/g" ${INSTALL_PATH}/conf/opsany-saas/k8s/k8s-init.py
    sed -i "s/K8S_SECRET_KEY/${K8S_SECRET_KEY}/g" ${INSTALL_PATH}/conf/opsany-saas/k8s/k8s-init.py
    sed -i "s/MYSQL_SERVER_IP/${MYSQL_SERVER_IP}/g" ${INSTALL_PATH}/conf/opsany-saas/k8s/k8s-prod.py
    sed -i "s/MYSQL_SERVER_PORT/${MYSQL_SERVER_PORT}/g" ${INSTALL_PATH}/conf/opsany-saas/k8s/k8s-prod.py
    sed -i "s/MYSQL_OPSANY_K8S_PASSWORD/${MYSQL_OPSANY_K8S_PASSWORD}/g" ${INSTALL_PATH}/conf/opsany-saas/k8s/k8s-prod.py
    sed -i "s/MONGO_SERVER_IP/${MONGO_SERVER_IP}/g" ${INSTALL_PATH}/conf/opsany-saas/k8s/k8s-prod.py
    sed -i "s/MONGO_SERVER_PORT/${MONGO_SERVER_PORT}/g" ${INSTALL_PATH}/conf/opsany-saas/k8s/k8s-prod.py
    sed -i "s/MONGO_K8S_PASSWORD/${MONGO_K8S_PASSWORD}/g" ${INSTALL_PATH}/conf/opsany-saas/k8s/k8s-prod.py
    sed -i "s/REDIS_SERVER_IP/${REDIS_SERVER_IP}/g" ${INSTALL_PATH}/conf/opsany-saas/k8s/k8s-prod.py
    sed -i "s/REDIS_SERVER_PORT/${REDIS_SERVER_PORT}/g" ${INSTALL_PATH}/conf/opsany-saas/k8s/k8s-prod.py
    sed -i "s/REDIS_SERVER_USER/${REDIS_SERVER_USER}/g" ${INSTALL_PATH}/conf/opsany-saas/k8s/k8s-prod.py
    sed -i "s/REDIS_SERVER_PASSWORD/${REDIS_SERVER_PASSWORD}/g" ${INSTALL_PATH}/conf/opsany-saas/k8s/k8s-prod.py
    /bin/cp -r ../../kubernetes/helm/opsany-ee/opsany-saas-k8s/* ${INSTALL_PATH}/kubernetes/helm/opsany-ee/opsany-saas-k8s/
    /bin/cp ${INSTALL_PATH}/conf/opsany-saas/k8s/*  ${INSTALL_PATH}/kubernetes/helm/opsany-ee/opsany-saas-k8s/

    # Restarter container
    sed -i "s/^.*appVersion:.*$/appVersion: \"${UPDATE_VERSION}\"/g" ${INSTALL_PATH}/kubernetes/helm/opsany-ee/opsany-saas-k8s/Chart.yaml 
    K8S_POD=$(kubectl get pod -n opsany | grep opsany-saas-k8s | awk '{print $1}')
    helm upgrade opsany-saas-k8s ${INSTALL_PATH}/kubernetes/helm/opsany-ee/opsany-saas-k8s/ -n opsany
    kubectl delete pod ${K8S_POD} -n opsany
    sleep 10

    # Django migrate
    update_saas_version k8s 容器平台 ${K8S_SECRET_KEY}
}

saas_prom_update(){
    shell_log "======Update prom======"
    # Modify configuration
    /bin/cp -r ../conf/opsany-saas/prom/* ${INSTALL_PATH}/conf/opsany-saas/prom/
    PROM_SECRET_KEY=$(cat ${INSTALL_PATH}/conf/.prom_secret_key)
    sed -i "s/DOMAIN_NAME/${DOMAIN_NAME}/g" ${INSTALL_PATH}/conf/opsany-saas/prom/prom-init.py
    sed -i "s/PROM_SECRET_KEY/${PROM_SECRET_KEY}/g" ${INSTALL_PATH}/conf/opsany-saas/prom/prom-init.py
    sed -i "s/MYSQL_SERVER_IP/${MYSQL_SERVER_IP}/g" ${INSTALL_PATH}/conf/opsany-saas/prom/prom-prod.py
    sed -i "s/MYSQL_SERVER_PORT/${MYSQL_SERVER_PORT}/g" ${INSTALL_PATH}/conf/opsany-saas/prom/prom-prod.py
    sed -i "s/MYSQL_OPSANY_PROM_PASSWORD/${MYSQL_OPSANY_PROM_PASSWORD}/g" ${INSTALL_PATH}/conf/opsany-saas/prom/prom-prod.py
    sed -i "s/MONGO_SERVER_IP/${MONGO_SERVER_IP}/g" ${INSTALL_PATH}/conf/opsany-saas/prom/prom-prod.py
    sed -i "s/MONGO_SERVER_PORT/${MONGO_SERVER_PORT}/g" ${INSTALL_PATH}/conf/opsany-saas/prom/prom-prod.py
    sed -i "s/MONGO_PROM_PASSWORD/${MONGO_PROM_PASSWORD}/g" ${INSTALL_PATH}/conf/opsany-saas/prom/prom-prod.py
    sed -i "s/REDIS_SERVER_IP/${REDIS_SERVER_IP}/g" ${INSTALL_PATH}/conf/opsany-saas/prom/prom-prod.py
    sed -i "s/REDIS_SERVER_PORT/${REDIS_SERVER_PORT}/g" ${INSTALL_PATH}/conf/opsany-saas/prom/prom-prod.py
    sed -i "s/REDIS_SERVER_USER/${REDIS_SERVER_USER}/g" ${INSTALL_PATH}/conf/opsany-saas/prom/prom-prod.py
    sed -i "s/REDIS_SERVER_PASSWORD/${REDIS_SERVER_PASSWORD}/g" ${INSTALL_PATH}/conf/opsany-saas/prom/prom-prod.py
    /bin/cp -r ../../kubernetes/helm/opsany-ee/opsany-saas-prom/* ${INSTALL_PATH}/kubernetes/helm/opsany-ee/opsany-saas-prom/
    /bin/cp ${INSTALL_PATH}/conf/opsany-saas/prom/*  ${INSTALL_PATH}/kubernetes/helm/opsany-ee/opsany-saas-prom/

    # Restarter container
    sed -i "s/^.*appVersion:.*$/appVersion: \"${UPDATE_VERSION}\"/g" ${INSTALL_PATH}/kubernetes/helm/opsany-ee/opsany-saas-prom/Chart.yaml
    PROM_POD=$(kubectl get pod -n opsany | grep opsany-saas-prom | awk '{print $1}')
    helm upgrade opsany-saas-prom ${INSTALL_PATH}/kubernetes/helm/opsany-ee/opsany-saas-prom/ -n opsany
    kubectl delete pod ${PROM_POD} -n opsany
    sleep 10

    # Django migrate
    update_saas_version prom 应用监控 ${PROM_SECRET_KEY}
}

saas_apm_update(){
    shell_log "======Update apm======"
    # Modify configuration
    /bin/cp -r ../conf/opsany-saas/apm/* ${INSTALL_PATH}/conf/opsany-saas/apm/
    APM_SECRET_KEY=$(cat ${INSTALL_PATH}/conf/.apm_secret_key)
    sed -i "s/DOMAIN_NAME/${DOMAIN_NAME}/g" ${INSTALL_PATH}/conf/opsany-saas/apm/apm-init.py
    sed -i "s/APM_SECRET_KEY/${APM_SECRET_KEY}/g" ${INSTALL_PATH}/conf/opsany-saas/apm/apm-init.py
    sed -i "s/MYSQL_SERVER_IP/${MYSQL_SERVER_IP}/g" ${INSTALL_PATH}/conf/opsany-saas/apm/apm-prod.py
    sed -i "s/MYSQL_SERVER_PORT/${MYSQL_SERVER_PORT}/g" ${INSTALL_PATH}/conf/opsany-saas/apm/apm-prod.py
    sed -i "s/MYSQL_OPSANY_APM_PASSWORD/${MYSQL_OPSANY_APM_PASSWORD}/g" ${INSTALL_PATH}/conf/opsany-saas/apm/apm-prod.py
    sed -i "s/MONGO_SERVER_IP/${MONGO_SERVER_IP}/g" ${INSTALL_PATH}/conf/opsany-saas/apm/apm-prod.py
    sed -i "s/MONGO_SERVER_PORT/${MONGO_SERVER_PORT}/g" ${INSTALL_PATH}/conf/opsany-saas/apm/apm-prod.py
    sed -i "s/MONGO_APM_PASSWORD/${MONGO_APM_PASSWORD}/g" ${INSTALL_PATH}/conf/opsany-saas/apm/apm-prod.py
    sed -i "s/REDIS_SERVER_IP/${REDIS_SERVER_IP}/g" ${INSTALL_PATH}/conf/opsany-saas/apm/apm-prod.py
    sed -i "s/REDIS_SERVER_PORT/${REDIS_SERVER_PORT}/g" ${INSTALL_PATH}/conf/opsany-saas/apm/apm-prod.py
    sed -i "s/REDIS_SERVER_USER/${REDIS_SERVER_USER}/g" ${INSTALL_PATH}/conf/opsany-saas/apm/apm-prod.py
    sed -i "s/REDIS_SERVER_PASSWORD/${REDIS_SERVER_PASSWORD}/g" ${INSTALL_PATH}/conf/opsany-saas/apm/apm-prod.py
    /bin/cp -r ../../kubernetes/helm/opsany-ee/opsany-saas-apm/* ${INSTALL_PATH}/kubernetes/helm/opsany-ee/opsany-saas-apm/
    /bin/cp ${INSTALL_PATH}/conf/opsany-saas/apm/*  ${INSTALL_PATH}/kubernetes/helm/opsany-ee/opsany-saas-apm/

    # Restarter container
    sed -i "s/^.*appVersion:.*$/appVersion: \"${UPDATE_VERSION}\"/g" ${INSTALL_PATH}/kubernetes/helm/opsany-ee/opsany-saas-apm/Chart.yaml
    APM_POD=$(kubectl get pod -n opsany | grep opsany-saas-apm | awk '{print $1}')
    helm upgrade opsany-saas-apm ${INSTALL_PATH}/kubernetes/helm/opsany-ee/opsany-saas-apm/ -n opsany
    kubectl delete pod ${APM_POD} -n opsany
    sleep 10

    # Django migrate
    update_saas_version apm APM平台 ${APM_SECRET_KEY}
}

saas_kbase_update(){
    shell_log "======Update kbase======"
    # Modify configuration
    /bin/cp -r ../conf/opsany-saas/kbase/* ${INSTALL_PATH}/conf/opsany-saas/kbase/
    KBASE_SECRET_KEY=$(cat ${INSTALL_PATH}/conf/.kbase_secret_key)
    sed -i "s/DOMAIN_NAME/${DOMAIN_NAME}/g" ${INSTALL_PATH}/conf/opsany-saas/kbase/kbase-init.py
    sed -i "s/KBASE_SECRET_KEY/${KBASE_SECRET_KEY}/g" ${INSTALL_PATH}/conf/opsany-saas/kbase/kbase-init.py
    sed -i "s/MYSQL_SERVER_IP/${MYSQL_SERVER_IP}/g" ${INSTALL_PATH}/conf/opsany-saas/kbase/kbase-prod.py
    sed -i "s/MYSQL_SERVER_PORT/${MYSQL_SERVER_PORT}/g" ${INSTALL_PATH}/conf/opsany-saas/kbase/kbase-prod.py
    sed -i "s/MYSQL_OPSANY_KBASE_PASSWORD/${MYSQL_OPSANY_KBASE_PASSWORD}/g" ${INSTALL_PATH}/conf/opsany-saas/kbase/kbase-prod.py
    sed -i "s/MONGO_SERVER_IP/${MONGO_SERVER_IP}/g" ${INSTALL_PATH}/conf/opsany-saas/kbase/kbase-prod.py
    sed -i "s/MONGO_SERVER_PORT/${MONGO_SERVER_PORT}/g" ${INSTALL_PATH}/conf/opsany-saas/kbase/kbase-prod.py
    sed -i "s/MONGO_KBASE_PASSWORD/${MONGO_KBASE_PASSWORD}/g" ${INSTALL_PATH}/conf/opsany-saas/kbase/kbase-prod.py
    sed -i "s/REDIS_SERVER_IP/${REDIS_SERVER_IP}/g" ${INSTALL_PATH}/conf/opsany-saas/kbase/kbase-prod.py
    sed -i "s/REDIS_SERVER_PORT/${REDIS_SERVER_PORT}/g" ${INSTALL_PATH}/conf/opsany-saas/kbase/kbase-prod.py
    sed -i "s/REDIS_SERVER_USER/${REDIS_SERVER_USER}/g" ${INSTALL_PATH}/conf/opsany-saas/kbase/kbase-prod.py
    sed -i "s/REDIS_SERVER_PASSWORD/${REDIS_SERVER_PASSWORD}/g" ${INSTALL_PATH}/conf/opsany-saas/kbase/kbase-prod.py
    /bin/cp -r ../../kubernetes/helm/opsany-ee/opsany-saas-kbase/* ${INSTALL_PATH}/kubernetes/helm/opsany-ee/opsany-saas-kbase/
    /bin/cp ${INSTALL_PATH}/conf/opsany-saas/kbase/*  ${INSTALL_PATH}/kubernetes/helm/opsany-ee/opsany-saas-kbase/

    # Restarter container
    sed -i "s/^.*appVersion:.*$/appVersion: \"${UPDATE_VERSION}\"/g" ${INSTALL_PATH}/kubernetes/helm/opsany-ee/opsany-saas-kbase/Chart.yaml 
    KBASE_POD=$(kubectl get pod -n opsany | grep opsany-saas-kbase | awk '{print $1}')
    helm upgrade opsany-saas-kbase ${INSTALL_PATH}/kubernetes/helm/opsany-ee/opsany-saas-kbase/ -n opsany
    kubectl delete pod ${KBASE_POD} -n opsany
    sleep 10

    # Django migrate
    update_saas_version kbase 知识库 ${KBASE_SECRET_KEY}
}

saas_event_update(){
    shell_log "======Update event======"
    # Modify configuration
    /bin/cp -r ../conf/opsany-saas/event/* ${INSTALL_PATH}/conf/opsany-saas/event/
    EVENT_SECRET_KEY=$(cat ${INSTALL_PATH}/conf/.event_secret_key)
    sed -i "s/DOMAIN_NAME/${DOMAIN_NAME}/g" ${INSTALL_PATH}/conf/opsany-saas/event/event-init.py
    sed -i "s/EVENT_SECRET_KEY/${EVENT_SECRET_KEY}/g" ${INSTALL_PATH}/conf/opsany-saas/event/event-init.py
    sed -i "s/MYSQL_SERVER_IP/${MYSQL_SERVER_IP}/g" ${INSTALL_PATH}/conf/opsany-saas/event/event-prod.py
    sed -i "s/MYSQL_SERVER_PORT/${MYSQL_SERVER_PORT}/g" ${INSTALL_PATH}/conf/opsany-saas/event/event-prod.py
    sed -i "s/MYSQL_OPSANY_EVENT_PASSWORD/${MYSQL_OPSANY_EVENT_PASSWORD}/g" ${INSTALL_PATH}/conf/opsany-saas/event/event-prod.py
    sed -i "s/MONGO_SERVER_IP/${MONGO_SERVER_IP}/g" ${INSTALL_PATH}/conf/opsany-saas/event/event-prod.py
    sed -i "s/MONGO_SERVER_PORT/${MONGO_SERVER_PORT}/g" ${INSTALL_PATH}/conf/opsany-saas/event/event-prod.py
    sed -i "s/MONGO_EVENT_PASSWORD/${MONGO_EVENT_PASSWORD}/g" ${INSTALL_PATH}/conf/opsany-saas/event/event-prod.py
    sed -i "s/REDIS_SERVER_IP/${REDIS_SERVER_IP}/g" ${INSTALL_PATH}/conf/opsany-saas/event/event-prod.py
    sed -i "s/REDIS_SERVER_PORT/${REDIS_SERVER_PORT}/g" ${INSTALL_PATH}/conf/opsany-saas/event/event-prod.py
    sed -i "s/REDIS_SERVER_USER/${REDIS_SERVER_USER}/g" ${INSTALL_PATH}/conf/opsany-saas/event/event-prod.py
    sed -i "s/REDIS_SERVER_PASSWORD/${REDIS_SERVER_PASSWORD}/g" ${INSTALL_PATH}/conf/opsany-saas/event/event-prod.py
    /bin/cp -r ../../kubernetes/helm/opsany-ee/opsany-saas-event/* ${INSTALL_PATH}/kubernetes/helm/opsany-ee/opsany-saas-event/
    /bin/cp ${INSTALL_PATH}/conf/opsany-saas/event/*  ${INSTALL_PATH}/kubernetes/helm/opsany-ee/opsany-saas-event/

    # Restarter container
    sed -i "s/^.*appVersion:.*$/appVersion: \"${UPDATE_VERSION}\"/g" ${INSTALL_PATH}/kubernetes/helm/opsany-ee/opsany-saas-event/Chart.yaml
    EVENT_POD=$(kubectl get pod -n opsany | grep opsany-saas-event | awk '{print $1}')
    helm upgrade opsany-saas-event ${INSTALL_PATH}/kubernetes/helm/opsany-ee/opsany-saas-event/ -n opsany
    kubectl delete pod ${EVENT_POD} -n opsany
    sleep 10

    # Django migrate
    update_saas_version event 稳定性平台 ${EVENT_SECRET_KEY}
}

saas_auto_update(){
    shell_log "======Update auto======"
    # Modify configuration
    /bin/cp -r ../conf/opsany-saas/auto/* ${INSTALL_PATH}/conf/opsany-saas/auto/
    AUTO_SECRET_KEY=$(cat ${INSTALL_PATH}/conf/.auto_secret_key)
    sed -i "s/DOMAIN_NAME/${DOMAIN_NAME}/g" ${INSTALL_PATH}/conf/opsany-saas/auto/auto-init.py
    sed -i "s/AUTO_SECRET_KEY/${AUTO_SECRET_KEY}/g" ${INSTALL_PATH}/conf/opsany-saas/auto/auto-init.py
    sed -i "s/MYSQL_SERVER_IP/${MYSQL_SERVER_IP}/g" ${INSTALL_PATH}/conf/opsany-saas/auto/auto-prod.py
    sed -i "s/MYSQL_SERVER_PORT/${MYSQL_SERVER_PORT}/g" ${INSTALL_PATH}/conf/opsany-saas/auto/auto-prod.py
    sed -i "s/MYSQL_OPSANY_AUTO_PASSWORD/${MYSQL_OPSANY_AUTO_PASSWORD}/g" ${INSTALL_PATH}/conf/opsany-saas/auto/auto-prod.py
    sed -i "s/MONGO_SERVER_IP/${MONGO_SERVER_IP}/g" ${INSTALL_PATH}/conf/opsany-saas/auto/auto-prod.py
    sed -i "s/MONGO_SERVER_PORT/${MONGO_SERVER_PORT}/g" ${INSTALL_PATH}/conf/opsany-saas/auto/auto-prod.py
    sed -i "s/MONGO_AUTO_PASSWORD/${MONGO_AUTO_PASSWORD}/g" ${INSTALL_PATH}/conf/opsany-saas/auto/auto-prod.py
    sed -i "s/REDIS_SERVER_IP/${REDIS_SERVER_IP}/g" ${INSTALL_PATH}/conf/opsany-saas/auto/auto-prod.py
    sed -i "s/REDIS_SERVER_PORT/${REDIS_SERVER_PORT}/g" ${INSTALL_PATH}/conf/opsany-saas/auto/auto-prod.py
    sed -i "s/REDIS_SERVER_USER/${REDIS_SERVER_USER}/g" ${INSTALL_PATH}/conf/opsany-saas/auto/auto-prod.py
    sed -i "s/REDIS_SERVER_PASSWORD/${REDIS_SERVER_PASSWORD}/g" ${INSTALL_PATH}/conf/opsany-saas/auto/auto-prod.py
    /bin/cp -r ../../kubernetes/helm/opsany-ee/opsany-saas-auto/* ${INSTALL_PATH}/kubernetes/helm/opsany-ee/opsany-saas-auto/
    /bin/cp ${INSTALL_PATH}/conf/opsany-saas/auto/*  ${INSTALL_PATH}/kubernetes/helm/opsany-ee/opsany-saas-auto/

    # Restarter container
    sed -i "s/^.*appVersion:.*$/appVersion: \"${UPDATE_VERSION}\"/g" ${INSTALL_PATH}/kubernetes/helm/opsany-ee/opsany-saas-auto/Chart.yaml
    AUTO_POD=$(kubectl get pod -n opsany | grep opsany-saas-auto | awk '{print $1}')
    helm upgrade opsany-saas-auto ${INSTALL_PATH}/kubernetes/helm/opsany-ee/opsany-saas-auto/ -n opsany
    kubectl delete pod ${AUTO_POD} -n opsany
    sleep 10

    # Django migrate
    update_saas_version auto 智能巡检 ${AUTO_SECRET_KEY}
}

saas_log_update(){
    shell_log "======Update log======"
    # Modify configuration
    /bin/cp -r ../conf/opsany-saas/log/* ${INSTALL_PATH}/conf/opsany-saas/log/
    LOG_SECRET_KEY=$(cat ${INSTALL_PATH}/conf/.log_secret_key)
    sed -i "s/DOMAIN_NAME/${DOMAIN_NAME}/g" ${INSTALL_PATH}/conf/opsany-saas/log/log-init.py
    sed -i "s/LOG_SECRET_KEY/${LOG_SECRET_KEY}/g" ${INSTALL_PATH}/conf/opsany-saas/log/log-init.py
    sed -i "s/MYSQL_SERVER_IP/${MYSQL_SERVER_IP}/g" ${INSTALL_PATH}/conf/opsany-saas/log/log-prod.py
    sed -i "s/MYSQL_SERVER_PORT/${MYSQL_SERVER_PORT}/g" ${INSTALL_PATH}/conf/opsany-saas/log/log-prod.py
    sed -i "s/MYSQL_OPSANY_LOG_PASSWORD/${MYSQL_OPSANY_LOG_PASSWORD}/g" ${INSTALL_PATH}/conf/opsany-saas/log/log-prod.py
    sed -i "s/MONGO_SERVER_IP/${MONGO_SERVER_IP}/g" ${INSTALL_PATH}/conf/opsany-saas/log/log-prod.py
    sed -i "s/MONGO_SERVER_PORT/${MONGO_SERVER_PORT}/g" ${INSTALL_PATH}/conf/opsany-saas/log/log-prod.py
    sed -i "s/MONGO_LOG_PASSWORD/${MONGO_LOG_PASSWORD}/g" ${INSTALL_PATH}/conf/opsany-saas/log/log-prod.py
    sed -i "s/REDIS_SERVER_IP/${REDIS_SERVER_IP}/g" ${INSTALL_PATH}/conf/opsany-saas/log/log-prod.py
    sed -i "s/REDIS_SERVER_PORT/${REDIS_SERVER_PORT}/g" ${INSTALL_PATH}/conf/opsany-saas/log/log-prod.py
    sed -i "s/REDIS_SERVER_USER/${REDIS_SERVER_USER}/g" ${INSTALL_PATH}/conf/opsany-saas/log/log-prod.py
    sed -i "s/REDIS_SERVER_PASSWORD/${REDIS_SERVER_PASSWORD}/g" ${INSTALL_PATH}/conf/opsany-saas/log/log-prod.py
    /bin/cp -r ../../kubernetes/helm/opsany-ee/opsany-saas-log/* ${INSTALL_PATH}/kubernetes/helm/opsany-ee/opsany-saas-log/
    /bin/cp ${INSTALL_PATH}/conf/opsany-saas/log/*  ${INSTALL_PATH}/kubernetes/helm/opsany-ee/opsany-saas-log/

    # Restarter container
    sed -i "s/^.*appVersion:.*$/appVersion: \"${UPDATE_VERSION}\"/g" ${INSTALL_PATH}/kubernetes/helm/opsany-ee/opsany-saas-log/Chart.yaml
    LOG_POD=$(kubectl get pod -n opsany | grep opsany-saas-log | awk '{print $1}')
    helm upgrade opsany-saas-log ${INSTALL_PATH}/kubernetes/helm/opsany-ee/opsany-saas-log/ -n opsany
    kubectl delete pod ${LOG_POD} -n opsany
    sleep 10

    # Django migrate
    update_saas_version log 日志平台 ${LOG_SECRET_KEY}
}

# $1 rbac $2 统一权限 $3 ${RBAC_SECRET_KEY}
update_saas_version(){
      python3 ../../saas/register_online_saas.py --paas_domain https://${DOMAIN_NAME} --username admin --password ${ADMIN_PASSWORD} --saas_app_code $1 --saas_app_name $2 --saas_app_version ${UPDATE_VERSION} --saas_app_secret_key $3 --is_update true
}

saas_ee_init(){
    shell_log "======OpsAny User Initialize======"
    sleep 3
    python3 ../../saas/sync-user-script.py --domain https://${DOMAIN_NAME} --paas_username admin --paas_password ${ADMIN_PASSWORD} --app_code event auto k8s kbase log prom
    shell_warning_log "======OpsAny: Make Ops Perfect======" 
}

# Main
main(){
    UPDATE_VERSION=$2
    case "$1" in
    k8s)
        saas_k8s_update $2
        ;;
    prom)
        saas_prom_update $2
        ;;
    apm)
        saas_apm_update $2
        ;;
    kbase)
        saas_kbase_update $2
        ;;
    event)
        saas_event_update $2
        ;;
    auto)
        saas_auto_update $2
        ;;
    log)
        saas_log_update $2
        ;;
    all)
	    saas_k8s_update $2
        saas_event_update $2
        saas_auto_update $2
        saas_kbase_update $2
        saas_prom_update $2
        saas_apm_update $2
        saas_log_update $2
        saas_ee_init
        ;;
	help|*)
	    echo $"Usage: $0 {event|auto|k8s|kbase|prom|log|apm|all|help version}"
	    ;;
    esac
}

main $1 $2
