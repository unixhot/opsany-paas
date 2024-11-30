#!/bin/bash
#******************************************
# Author:       Jason Zhao
# Email:        zhaoshundong@opsany.com
# Organization: OpsAny https://www.opsany.com/
# Description:  OpsAny SAAS Enterprise Edition Install Script
#******************************************

# Data/Time Variables
CTIME=$(date "+%Y-%m-%d-%H-%M")

# Shell Envionment Variables
CDIR=$(pwd)
SHELL_NAME="saas-ee-k8s-install.sh"
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

# Install initialization
install_init(){
    #SaaS Log Directory
    mkdir -p /data/k8s-nfs/opsany-logs/{event,auto,kbase,log,k8s,prom,apm}
    /bin/cp conf/nginx/opsany_paas_k8s_ee.config ${INSTALL_PATH}/conf/nginx-conf.d/opsany_paas.conf
    sed -i "s/DOMAIN_NAME/${DOMAIN_NAME}/g" ${INSTALL_PATH}/conf/nginx-conf.d/opsany_paas.conf
    sed -i "s/LOCAL_IP/${LOCAL_IP}/g" ${INSTALL_PATH}/conf/nginx-conf.d/opsany_paas.conf
    /bin/cp ${INSTALL_PATH}/conf/nginx-conf.d/opsany_paas.conf ${INSTALL_PATH}/kubernetes/helm/opsany-paas/opsany-paas-openresty/
    # Register event
    if [ -f ${INSTALL_PATH}/conf/.event_secret_key ];then
        EVENT_SECRET_KEY=$(cat ${INSTALL_PATH}/conf/.event_secret_key)
    else
        EVENT_SECRET_KEY=$(uuid -v4)
        echo $EVENT_SECRET_KEY > ${INSTALL_PATH}/conf/.event_secret_key
    fi
    python3 ./register_online_saas.py --paas_domain https://${DOMAIN_NAME} --username admin --password ${ADMIN_PASSWORD} --saas_app_code event --saas_app_name 事件中心 --saas_app_version 2.2.3 --saas_app_secret_key ${EVENT_SECRET_KEY}
    
    # Register auto
    if [ -f ${INSTALL_PATH}/conf/.auto_secret_key ];then
        AUTO_SECRET_KEY=$(cat ${INSTALL_PATH}/conf/.auto_secret_key)
    else
        AUTO_SECRET_KEY=$(uuid -v4)
        echo $AUTO_SECRET_KEY > ${INSTALL_PATH}/conf/.auto_secret_key
    fi
    python3 ./register_online_saas.py --paas_domain https://${DOMAIN_NAME} --username admin --password ${ADMIN_PASSWORD} --saas_app_code auto --saas_app_name 智能巡检 --saas_app_version 2.2.3 --saas_app_secret_key ${AUTO_SECRET_KEY}
    
    # Register kbase
    if [ -f ${INSTALL_PATH}/conf/.kbase_secret_key ];then
        KBASE_SECRET_KEY=$(cat ${INSTALL_PATH}/conf/.kbase_secret_key)
    else
        KBASE_SECRET_KEY=$(uuid -v4)
        echo $KBASE_SECRET_KEY > ${INSTALL_PATH}/conf/.kbase_secret_key
    fi
    python3 ./register_online_saas.py --paas_domain https://${DOMAIN_NAME} --username admin --password ${ADMIN_PASSWORD} --saas_app_code kbase --saas_app_name 知识库 --saas_app_version 2.2.3 --saas_app_secret_key ${KBASE_SECRET_KEY}
    
    # Register log
    if [ -f ${INSTALL_PATH}/conf/.log_secret_key ];then
        LOG_SECRET_KEY=$(cat ${INSTALL_PATH}/conf/.log_secret_key)
    else
        LOG_SECRET_KEY=$(uuid -v4)
        echo $LOG_SECRET_KEY > ${INSTALL_PATH}/conf/.log_secret_key
    fi
    python3 ./register_online_saas.py --paas_domain https://${DOMAIN_NAME} --username admin --password ${ADMIN_PASSWORD} --saas_app_code log --saas_app_name 日志平台 --saas_app_version 2.2.3 --saas_app_secret_key ${LOG_SECRET_KEY}
    
    # Register k8s
    if [ -f ${INSTALL_PATH}/conf/.k8s_secret_key ];then
        K8S_SECRET_KEY=$(cat ${INSTALL_PATH}/conf/.k8s_secret_key)
    else
        K8S_SECRET_KEY=$(uuid -v4)
        echo $K8S_SECRET_KEY > ${INSTALL_PATH}/conf/.k8s_secret_key
    fi
    python3 ./register_online_saas.py --paas_domain https://${DOMAIN_NAME} --username admin --password ${ADMIN_PASSWORD} --saas_app_code k8s --saas_app_name 容器平台 --saas_app_version 2.2.3 --saas_app_secret_key ${K8S_SECRET_KEY}
    
    # Register prom
    if [ -f ${INSTALL_PATH}/conf/.prom_secret_key ];then
        PROM_SECRET_KEY=$(cat ${INSTALL_PATH}/conf/.prom_secret_key)
    else
        PROM_SECRET_KEY=$(uuid -v4)
        echo $PROM_SECRET_KEY > ${INSTALL_PATH}/conf/.prom_secret_key
    fi
    python3 ./register_online_saas.py --paas_domain https://${DOMAIN_NAME} --username admin --password ${ADMIN_PASSWORD} --saas_app_code prom --saas_app_name 应用监控 --saas_app_version 2.2.3 --saas_app_secret_key ${PROM_SECRET_KEY}
    
    # Register apm
    if [ -f ${INSTALL_PATH}/conf/.apm_secret_key ];then
        APM_SECRET_KEY=$(cat ${INSTALL_PATH}/conf/.apm_secret_key)
    else
        APM_SECRET_KEY=$(uuid -v4)
        echo $APM_SECRET_KEY > ${INSTALL_PATH}/conf/.apm_secret_key
    fi
    python3 ./register_online_saas.py --paas_domain https://${DOMAIN_NAME} --username admin --password ${ADMIN_PASSWORD} --saas_app_code apm --saas_app_name APM平台 --saas_app_version 2.2.3 --saas_app_secret_key ${APM_SECRET_KEY}
}

esb_init(){
    #event
    sed -i "s/DOMAIN_NAME/$DOMAIN_NAME/g" ${INSTALL_PATH}/esb/apis/event/toolkit/configs.py
    sed -i "s#/t/event#/o/event#g" ${INSTALL_PATH}/esb/apis/event/toolkit/tools.py
    #auto
    sed -i "s/DOMAIN_NAME/$DOMAIN_NAME/g" ${INSTALL_PATH}/esb/apis/auto/toolkit/configs.py
    sed -i "s#/t/auto#/o/auto#g" ${INSTALL_PATH}/esb/apis/auto/toolkit/tools.py
    #kbase
    sed -i "s/DOMAIN_NAME/$DOMAIN_NAME/g" ${INSTALL_PATH}/esb/apis/kbase/toolkit/configs.py
    sed -i "s#/t/kbase#/o/kbase#g" ${INSTALL_PATH}/esb/apis/kbase/toolkit/tools.py
    #log
    sed -i "s/DOMAIN_NAME/$DOMAIN_NAME/g" ${INSTALL_PATH}/esb/apis/log/toolkit/configs.py
    sed -i "s#/t/log#/o/log#g" ${INSTALL_PATH}/esb/apis/log/toolkit/tools.py
    #k8s
    sed -i "s/DOMAIN_NAME/$DOMAIN_NAME/g" ${INSTALL_PATH}/esb/apis/k8s/toolkit/configs.py
    sed -i "s#/t/k8s#/o/k8s#g" ${INSTALL_PATH}/esb/apis/k8s/toolkit/tools.py
    #prom
    sed -i "s/DOMAIN_NAME/$DOMAIN_NAME/g" ${INSTALL_PATH}/esb/apis/prom/toolkit/configs.py
    sed -i "s#/t/prom#/o/prom#g" ${INSTALL_PATH}/esb/apis/prom/toolkit/tools.py 
    #apm
    sed -i "s/DOMAIN_NAME/$DOMAIN_NAME/g" ${INSTALL_PATH}/esb/apis/apm/toolkit/configs.py
    sed -i "s#/t/apm#/o/apm#g" ${INSTALL_PATH}/esb/apis/apm/toolkit/tools.py     
}

mysql_init(){
    shell_log "MySQL Initialize Begin"
    MYSQL_SERVER_IP=$(kubectl get svc opsany-base-mysql -n opsany | awk -F ' ' '{print $3}' | tail -1)
    export MYSQL_PWD=${MYSQL_ROOT_PASSWORD}

    #event
    mysql -h "${MYSQL_SERVER_IP}" -P ${MYSQL_SERVER_PORT} -u root -p"${MYSQL_ROOT_PASSWORD}" -e "create database event DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;"
    mysql -h "${MYSQL_SERVER_IP}" -P ${MYSQL_SERVER_PORT} -u root -p"${MYSQL_ROOT_PASSWORD}" -e "CREATE USER 'event'@'%' identified by "\"${MYSQL_OPSANY_EVENT_PASSWORD}\"";"
    mysql -h "${MYSQL_SERVER_IP}" -P ${MYSQL_SERVER_PORT} -u root -p"${MYSQL_ROOT_PASSWORD}" -e "grant all on event.* to event@'%';"
    #auto
    mysql -h "${MYSQL_SERVER_IP}" -P ${MYSQL_SERVER_PORT} -u root -p"${MYSQL_ROOT_PASSWORD}" -e "create database auto DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;"
    mysql -h "${MYSQL_SERVER_IP}" -P ${MYSQL_SERVER_PORT} -u root -p"${MYSQL_ROOT_PASSWORD}" -e "CREATE USER 'auto'@'%' identified by "\"${MYSQL_OPSANY_AUTO_PASSWORD}\"";"
    mysql -h "${MYSQL_SERVER_IP}" -P ${MYSQL_SERVER_PORT} -u root -p"${MYSQL_ROOT_PASSWORD}" -e "grant all on auto.* to auto@'%';"
    #kbase
    mysql -h "${MYSQL_SERVER_IP}" -P ${MYSQL_SERVER_PORT} -u root -p"${MYSQL_ROOT_PASSWORD}" -e "create database kbase DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;"
    mysql -h "${MYSQL_SERVER_IP}" -P ${MYSQL_SERVER_PORT} -u root -p"${MYSQL_ROOT_PASSWORD}" -e "CREATE USER 'kbase'@'%' identified by "\"${MYSQL_OPSANY_KBASE_PASSWORD}\"";"
    mysql -h "${MYSQL_SERVER_IP}" -P ${MYSQL_SERVER_PORT} -u root -p"${MYSQL_ROOT_PASSWORD}" -e "grant all on kbase.* to kbase@'%';"
    #prom
    mysql -h "${MYSQL_SERVER_IP}" -P ${MYSQL_SERVER_PORT} -u root -p"${MYSQL_ROOT_PASSWORD}" -e "create database prom DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;"
    mysql -h "${MYSQL_SERVER_IP}" -P ${MYSQL_SERVER_PORT} -u root -p"${MYSQL_ROOT_PASSWORD}" -e "CREATE USER 'prom'@'%' identified by "\"${MYSQL_OPSANY_PROM_PASSWORD}\"";"
    mysql -h "${MYSQL_SERVER_IP}" -P ${MYSQL_SERVER_PORT} -u root -p"${MYSQL_ROOT_PASSWORD}" -e "grant all on prom.* to prom@'%';"
    #apm
    mysql -h "${MYSQL_SERVER_IP}" -P ${MYSQL_SERVER_PORT} -u root -p"${MYSQL_ROOT_PASSWORD}" -e "create database apm DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;"
    mysql -h "${MYSQL_SERVER_IP}" -P ${MYSQL_SERVER_PORT} -u root -p"${MYSQL_ROOT_PASSWORD}" -e "CREATE USER 'apm'@'%' identified by "\"${MYSQL_OPSANY_APM_PASSWORD}\"";"
    mysql -h "${MYSQL_SERVER_IP}" -P ${MYSQL_SERVER_PORT} -u root -p"${MYSQL_ROOT_PASSWORD}" -e "grant all on apm.* to apm@'%';"
    #log
    mysql -h "${MYSQL_SERVER_IP}" -P ${MYSQL_SERVER_PORT} -u root -p"${MYSQL_ROOT_PASSWORD}" -e "create database log DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;"
    mysql -h "${MYSQL_SERVER_IP}" -P ${MYSQL_SERVER_PORT} -u root -p"${MYSQL_ROOT_PASSWORD}" -e "CREATE USER log@'%' identified by "\"${MYSQL_OPSANY_LOG_PASSWORD}\"";"
    mysql -h "${MYSQL_SERVER_IP}" -u root -p"${MYSQL_ROOT_PASSWORD}" -e "grant all on log.* to log@'%';"
    #k8s
    mysql -h "${MYSQL_SERVER_IP}" -P ${MYSQL_SERVER_PORT} -u root -p"${MYSQL_ROOT_PASSWORD}" -e "create database k8s DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;"
    mysql -h "${MYSQL_SERVER_IP}" -P ${MYSQL_SERVER_PORT} -u root -p"${MYSQL_ROOT_PASSWORD}" -e "CREATE USER 'k8s'@'%' identified by "\"${MYSQL_OPSANY_K8S_PASSWORD}\"";"
    mysql -h "${MYSQL_SERVER_IP}" -P ${MYSQL_SERVER_PORT} -u root -p"${MYSQL_ROOT_PASSWORD}" -e "grant all on k8s.* to k8s@'%';"
}

# MonogDB Initialize
mongodb_init(){
    shell_log "======MongoDB Initialize======"
    sed -i "s/MONGO_AUTO_PASSWORD/${MONGO_AUTO_PASSWORD}/g" ${INSTALL_PATH}/init/mongodb-init/mongodb_init_ee.js
    sed -i "s/MONGO_EVENT_PASSWORD/${MONGO_EVENT_PASSWORD}/g" ${INSTALL_PATH}/init/mongodb-init/mongodb_init_ee.js
    sed -i "s/MONGO_PROM_PASSWORD/${MONGO_PROM_PASSWORD}/g" ${INSTALL_PATH}/init/mongodb-init/mongodb_init_ee.js
    sed -i "s/MONGO_KBASE_PASSWORD/${MONGO_KBASE_PASSWORD}/g" ${INSTALL_PATH}/init/mongodb-init/mongodb_init_ee.js

    kubectl -n opsany cp ${INSTALL_PATH}/init/mongodb-init/mongodb_init_ee.js opsany-base-mongodb-0:/opt/
    kubectl -n opsany exec opsany-base-mongodb-0 -- /opt/bitnami/mongodb/bin/mongosh -u $MONGO_INITDB_ROOT_USERNAME -p $MONGO_INITDB_ROOT_PASSWORD /opt/mongodb_init_ee.js
    shell_log "======MongoDB Initialize End======"
}

saas_event_deploy(){
    shell_log "======Start event======"
    # Modify configuration
    /bin/cp -r ../conf/opsany-saas/event ${INSTALL_PATH}/conf/opsany-saas/
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
    /bin/cp ${INSTALL_PATH}/conf/opsany-saas/event/*  ${INSTALL_PATH}/kubernetes/helm/opsany-ee/opsany-saas-event/
}

saas_auto_deploy(){
    shell_log "======Start auto======"
    # Modify configuration
    /bin/cp -r ../conf/opsany-saas/auto ${INSTALL_PATH}/conf/opsany-saas/
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
    /bin/cp ${INSTALL_PATH}/conf/opsany-saas/auto/*  ${INSTALL_PATH}/kubernetes/helm/opsany-ee/opsany-saas-auto/
}

saas_kbase_deploy(){
    shell_log "======Start kbase======"
    # Modify configuration
    /bin/cp -r ../conf/opsany-saas/kbase ${INSTALL_PATH}/conf/opsany-saas/
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
    /bin/cp ${INSTALL_PATH}/conf/opsany-saas/kbase/*  ${INSTALL_PATH}/kubernetes/helm/opsany-ee/opsany-saas-kbase/
}

saas_prom_deploy(){
    shell_log "======Start prom======"
    # Modify configuration
    /bin/cp -r ../conf/opsany-saas/prom ${INSTALL_PATH}/conf/opsany-saas/
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
    /bin/cp ${INSTALL_PATH}/conf/opsany-saas/prom/*  ${INSTALL_PATH}/kubernetes/helm/opsany-ee/opsany-saas-prom/
}

saas_log_deploy(){
    shell_log "======Start log======"
    # Modify configuration
    /bin/cp -r ../conf/opsany-saas/log ${INSTALL_PATH}/conf/opsany-saas/
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
    /bin/cp ${INSTALL_PATH}/conf/opsany-saas/log/*  ${INSTALL_PATH}/kubernetes/helm/opsany-ee/opsany-saas-log/
}

saas_k8s_deploy(){
    shell_log "======Start k8s======"
    # Modify configuration
    /bin/cp -r ../conf/opsany-saas/k8s ${INSTALL_PATH}/conf/opsany-saas/
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
    /bin/cp ${INSTALL_PATH}/conf/opsany-saas/k8s/*  ${INSTALL_PATH}/kubernetes/helm/opsany-ee/opsany-saas-k8s/
}

saas_apm_deploy(){
    shell_log "======Start apm======"
    # Modify configuration
    /bin/cp -r ../conf/opsany-saas/apm ${INSTALL_PATH}/conf/opsany-saas/
    APM_SECRET_KEY=$(cat ${INSTALL_PATH}/conf/.apm_secret_key)
    sed -i "s/DOMAIN_NAME/${DOMAIN_NAME}/g" ${INSTALL_PATH}/conf/opsany-saas/apm/apm-init.py
    sed -i "s/APM_SECRET_KEY/${APM_SECRET_KEY}/g" ${INSTALL_PATH}/conf/opsany-saas/apm/apm-init.py
    sed -i "s/MYSQL_SERVER_IP/${MYSQL_SERVER_IP}/g" ${INSTALL_PATH}/conf/opsany-saas/apm/apm-prod.py
    sed -i "s/MYSQL_SERVER_PORT/${MYSQL_SERVER_PORT}/g" ${INSTALL_PATH}/conf/opsany-saas/apm/apm-prod.py
    sed -i "s/MYSQL_OPSANY_APM_PASSWORD/${MYSQL_OPSANY_APM_PASSWORD}/g" ${INSTALL_PATH}/conf/opsany-saas/apm/apm-prod.py
    sed -i "s/MONGO_SERVER_IP/${MONGO_SERVER_IP}/g" ${INSTALL_PATH}/conf/opsany-saas/apm/apm-prod.py
    sed -i "s/MONGO_SERVER_PORT/${MONGO_SERVER_PORT}/g" ${INSTALL_PATH}/conf/opsany-saas/apm/apm-prod.py
    sed -i "s/MONGO_PROM_PASSWORD/${MONGO_PROM_PASSWORD}/g" ${INSTALL_PATH}/conf/opsany-saas/apm/apm-prod.py
    sed -i "s/REDIS_SERVER_IP/${REDIS_SERVER_IP}/g" ${INSTALL_PATH}/conf/opsany-saas/apm/apm-prod.py
    sed -i "s/REDIS_SERVER_PORT/${REDIS_SERVER_PORT}/g" ${INSTALL_PATH}/conf/opsany-saas/apm/apm-prod.py
    sed -i "s/REDIS_SERVER_USER/${REDIS_SERVER_USER}/g" ${INSTALL_PATH}/conf/opsany-saas/apm/apm-prod.py
    sed -i "s/REDIS_SERVER_PASSWORD/${REDIS_SERVER_PASSWORD}/g" ${INSTALL_PATH}/conf/opsany-saas/apm/apm-prod.py
    /bin/cp ${INSTALL_PATH}/conf/opsany-saas/apm/*  ${INSTALL_PATH}/kubernetes/helm/opsany-ee/opsany-saas-apm/
}

saas_ee_init(){
    shell_log "======OpsAny User Initialize======"
    sleep 3
    python3 ./sync-user-script.py --domain https://${DOMAIN_NAME} --paas_username admin --paas_password ${ADMIN_PASSWORD} --app_code event auto k8s kbase log prom apm
    python3 ./saas-ee-init.py --domain https://${DOMAIN_NAME} --username admin --password ${ADMIN_PASSWORD} --init_type menu,nav,temp,home_page
    shell_warning_log "======OpsAny: Make Ops Perfect======" 
}

# Main
main(){
    case "$1" in
    install)
        install_init
        esb_init
        mysql_init
        mongodb_init
	    saas_event_deploy
        saas_auto_deploy
        saas_k8s_deploy
        saas_kbase_deploy
        saas_log_deploy
        saas_prom_deploy
        saas_apm_deploy
        ;;
    init)
        saas_ee_init
        ;;
	help|*)
	    echo $"Usage: $0 {install|help}"
	    ;;
    esac
}

main $1 
