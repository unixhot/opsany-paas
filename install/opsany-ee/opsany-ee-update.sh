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
if [ ! -f ../install.config ];then
      shell_error_log "Please Change Directory to ${INSTALL_PATH}/install"
      exit
else
    grep '^[A-Z]' ../install.config > install.env
    cat ./ee-install.config >> install.env
    source install.env && rm -f install.env
    if [ -z "$ADMIN_PASSWORD" ];then
        source ${INSTALL_PATH}/conf/.passwd_env
    fi
fi

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
    
    # Starter container
    docker pull ${PAAS_DOCKER_REG}/opsany-saas-ee-event:${UPDATE_VERSION}
    docker stop opsany-saas-ee-event && docker rm opsany-saas-ee-event
    docker run -d --restart=always --name opsany-saas-ee-event \
       -p 7011:80 \
       -v ${INSTALL_PATH}/conf/opsany-saas/event/event-supervisor.ini:/etc/supervisord.d/event.ini \
       -v ${INSTALL_PATH}/conf/opsany-saas/event/event-uwsgi.ini:/opt/opsany/uwsgi/event.ini \
       -v ${INSTALL_PATH}/conf/opsany-saas/event/event-init.py:/opt/opsany/event/config/__init__.py \
       -v ${INSTALL_PATH}/conf/opsany-saas/event/event-prod.py:/opt/opsany/event/config/prod.py \
       -v ${INSTALL_PATH}/conf/opsany-saas/event/event-nginx.conf:/etc/nginx/http.d/default.conf \
       -v ${INSTALL_PATH}/conf/opsany-saas/event/event-nginx-main.conf:/etc/nginx/nginx.conf \
       -v ${INSTALL_PATH}/logs/event:/opt/opsany/logs/event \
       -v ${INSTALL_PATH}/uploads:/opt/opsany/uploads \
       -v /etc/localtime:/etc/localtime:ro \
       ${PAAS_DOCKER_REG}/opsany-saas-ee-event:${UPDATE_VERSION}
    
    # Django migrate
    docker exec -e BK_ENV="production" opsany-saas-ee-event /bin/sh -c \
    "python /opt/opsany/event/manage.py migrate --noinput >> ${SHELL_LOG} && python /opt/opsany/event/manage.py createcachetable django_cache > /dev/null"
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

    # Starter container
    docker pull ${PAAS_DOCKER_REG}/opsany-saas-ee-auto:${UPDATE_VERSION}
    docker stop opsany-saas-ee-auto && docker rm opsany-saas-ee-auto
    docker run -d --restart=always --name opsany-saas-ee-auto \
       -p 7012:80 \
       -v ${INSTALL_PATH}/conf/opsany-saas/auto/auto-supervisor.ini:/etc/supervisord.d/auto.ini \
       -v ${INSTALL_PATH}/conf/opsany-saas/auto/auto-uwsgi.ini:/opt/opsany/uwsgi/auto.ini \
       -v ${INSTALL_PATH}/conf/opsany-saas/auto/auto-init.py:/opt/opsany/auto/config/__init__.py \
       -v ${INSTALL_PATH}/conf/opsany-saas/auto/auto-prod.py:/opt/opsany/auto/config/prod.py \
       -v ${INSTALL_PATH}/conf/opsany-saas/auto/auto-nginx.conf:/etc/nginx/http.d/default.conf \
       -v ${INSTALL_PATH}/conf/opsany-saas/auto/auto-nginx-main.conf:/etc/nginx/nginx.conf \
       -v ${INSTALL_PATH}/logs/auto:/opt/opsany/logs/auto \
       -v ${INSTALL_PATH}/uploads:/opt/opsany/uploads \
       -v /etc/localtime:/etc/localtime:ro \
       ${PAAS_DOCKER_REG}/opsany-saas-ee-auto:${UPDATE_VERSION}
    
    # Django migrate
    docker exec -e BK_ENV="production" opsany-saas-ee-auto /bin/sh -c \
    "python /opt/opsany/auto/manage.py migrate --noinput >> ${SHELL_LOG} && python /opt/opsany/auto/manage.py createcachetable django_cache > /dev/null"
    update_saas_version auto 智能巡检 ${AUTO_SECRET_KEY}
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

    # Starter container
    docker pull ${PAAS_DOCKER_REG}/opsany-saas-ee-kbase:${UPDATE_VERSION}
    docker stop opsany-saas-ee-kbase && docker rm opsany-saas-ee-kbase
    docker run -d --restart=always --name opsany-saas-ee-kbase \
       -p 7013:80 \
       -v ${INSTALL_PATH}/conf/opsany-saas/kbase/kbase-supervisor.ini:/etc/supervisord.d/kbase.ini \
       -v ${INSTALL_PATH}/conf/opsany-saas/kbase/kbase-uwsgi.ini:/opt/opsany/uwsgi/kbase.ini \
       -v ${INSTALL_PATH}/conf/opsany-saas/kbase/kbase-init.py:/opt/opsany/kbase/config/__init__.py \
       -v ${INSTALL_PATH}/conf/opsany-saas/kbase/kbase-prod.py:/opt/opsany/kbase/config/prod.py \
       -v ${INSTALL_PATH}/conf/opsany-saas/kbase/kbase-nginx.conf:/etc/nginx/http.d/default.conf \
       -v ${INSTALL_PATH}/conf/opsany-saas/kbase/kbase-nginx-main.conf:/etc/nginx/nginx.conf \
       -v ${INSTALL_PATH}/logs/kbase:/opt/opsany/logs/kbase \
       -v ${INSTALL_PATH}/uploads:/opt/opsany/uploads \
       -v /etc/localtime:/etc/localtime:ro \
       ${PAAS_DOCKER_REG}/opsany-saas-ee-kbase:${UPDATE_VERSION}
    
    # Django migrate
    docker exec -e BK_ENV="production" opsany-saas-ee-kbase /bin/sh -c \
    "python /opt/opsany/kbase/manage.py migrate --noinput >> ${SHELL_LOG} && python /opt/opsany/kbase/manage.py createcachetable django_cache > /dev/null"
    update_saas_version kbase 知识库 ${KBASE_SECRET_KEY}
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

    # Starter container
    docker pull ${PAAS_DOCKER_REG}/opsany-saas-ee-prom:${UPDATE_VERSION}
    docker stop opsany-saas-ee-prom && docker rm opsany-saas-ee-prom
    docker run -d --restart=always --name opsany-saas-ee-prom \
       -p 7015:80 \
       -v ${INSTALL_PATH}/conf/opsany-saas/prom/prom-supervisor.ini:/etc/supervisord.d/prom.ini \
       -v ${INSTALL_PATH}/conf/opsany-saas/prom/prom-uwsgi.ini:/opt/opsany/uwsgi/prom.ini \
       -v ${INSTALL_PATH}/conf/opsany-saas/prom/prom-init.py:/opt/opsany/prom/config/__init__.py \
       -v ${INSTALL_PATH}/conf/opsany-saas/prom/prom-prod.py:/opt/opsany/prom/config/prod.py \
       -v ${INSTALL_PATH}/conf/opsany-saas/prom/prom-nginx.conf:/etc/nginx/http.d/default.conf \
       -v ${INSTALL_PATH}/conf/opsany-saas/prom/prom-nginx-main.conf:/etc/nginx/nginx.conf \
       -v ${INSTALL_PATH}/logs/prom:/opt/opsany/logs/prom \
       -v ${INSTALL_PATH}/uploads:/opt/opsany/uploads \
       -v /etc/localtime:/etc/localtime:ro \
       ${PAAS_DOCKER_REG}/opsany-saas-ee-prom:${UPDATE_VERSION}
    
    # Django migrate
    docker exec -e BK_ENV="production" opsany-saas-ee-prom /bin/sh -c \
    "python /opt/opsany/prom/manage.py migrate --noinput >> ${SHELL_LOG} && python /opt/opsany/prom/manage.py createcachetable django_cache > /dev/null"
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
    sed -i "s/MONGO_PROM_PASSWORD/${MONGO_PROM_PASSWORD}/g" ${INSTALL_PATH}/conf/opsany-saas/apm/apm-prod.py
    sed -i "s/REDIS_SERVER_IP/${REDIS_SERVER_IP}/g" ${INSTALL_PATH}/conf/opsany-saas/apm/apm-prod.py
    sed -i "s/REDIS_SERVER_PORT/${REDIS_SERVER_PORT}/g" ${INSTALL_PATH}/conf/opsany-saas/apm/apm-prod.py
    sed -i "s/REDIS_SERVER_USER/${REDIS_SERVER_USER}/g" ${INSTALL_PATH}/conf/opsany-saas/apm/apm-prod.py
    sed -i "s/REDIS_SERVER_PASSWORD/${REDIS_SERVER_PASSWORD}/g" ${INSTALL_PATH}/conf/opsany-saas/apm/apm-prod.py
    sed -i "s/ELASTIC_USERNAME/${ELASTIC_SEARCH_USERNAME}/g" ${INSTALL_PATH}/conf/opsany-saas/apm/apm-prod.py
    sed -i "s/ELASTIC_PASSWORD/${ES_PASSWORD}/g" ${INSTALL_PATH}/conf/opsany-saas/apm/apm-prod.py
    sed -i "s#ELASTIC_CLUSTER#${ES_SERVER_IP}#g" ${INSTALL_PATH}/conf/opsany-saas/apm/apm-prod.py
    sed -i "s/ELASTIC_SEARCH_INDEX/${ELASTIC_SEARCH_INDEX}/g" ${INSTALL_PATH}/conf/opsany-saas/apm/apm-prod.py
    sed -i "s/KIBANA_USERNAME/${KIBANA_USERNAME}/g" ${INSTALL_PATH}/conf/opsany-saas/apm/apm-prod.py
    sed -i "s/KIBANA_PASSWORD/${KIBANA_PASSWORD}/g" ${INSTALL_PATH}/conf/opsany-saas/apm/apm-prod.py
    sed -i "s#KIBANA_CLUSTER#${KIBANA_CLUSTER}#g" ${INSTALL_PATH}/conf/opsany-saas/apm/apm-prod.py

    # Starter container
    docker pull ${PAAS_DOCKER_REG}/opsany-saas-ee-apm:${UPDATE_VERSION}
    docker stop opsany-saas-ee-apm && docker rm opsany-saas-ee-apm
    docker run -d --restart=always --name opsany-saas-ee-apm \
       -p 7019:80 \
       -v ${INSTALL_PATH}/conf/opsany-saas/apm/apm-supervisor.ini:/etc/supervisord.d/apm.ini \
       -v ${INSTALL_PATH}/conf/opsany-saas/apm/apm-uwsgi.ini:/opt/opsany/uwsgi/apm.ini \
       -v ${INSTALL_PATH}/conf/opsany-saas/apm/apm-init.py:/opt/opsany/apm/config/__init__.py \
       -v ${INSTALL_PATH}/conf/opsany-saas/apm/apm-prod.py:/opt/opsany/apm/config/prod.py \
       -v ${INSTALL_PATH}/conf/opsany-saas/apm/apm-nginx.conf:/etc/nginx/http.d/default.conf \
       -v ${INSTALL_PATH}/conf/opsany-saas/apm/apm-nginx-main.conf:/etc/nginx/nginx.conf \
       -v ${INSTALL_PATH}/logs/apm:/opt/opsany/logs/apm \
       -v ${INSTALL_PATH}/uploads:/opt/opsany/uploads \
       -v /etc/localtime:/etc/localtime:ro \
       ${PAAS_DOCKER_REG}/opsany-saas-ee-apm:${UPDATE_VERSION}
    
    # Django migrate
    docker exec -e BK_ENV="production" opsany-saas-ee-apm /bin/sh -c \
    "python /opt/opsany/apm/manage.py migrate --noinput >> ${SHELL_LOG} && python /opt/opsany/apm/manage.py createcachetable django_cache > /dev/null"
    update_saas_version apm APM平台 ${APM_SECRET_KEY}
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

    # Starter container
    docker pull ${PAAS_DOCKER_REG}/opsany-saas-ee-log:${UPDATE_VERSION}
    docker stop opsany-saas-ee-log && docker rm opsany-saas-ee-log
    docker run -d --restart=always --name opsany-saas-ee-log \
       -p 7016:80 \
       -v ${INSTALL_PATH}/conf/opsany-saas/log/log-supervisor.ini:/etc/supervisord.d/log.ini \
       -v ${INSTALL_PATH}/conf/opsany-saas/log/log-uwsgi.ini:/opt/opsany/uwsgi/log.ini \
       -v ${INSTALL_PATH}/conf/opsany-saas/log/log-init.py:/opt/opsany/log/config/__init__.py \
       -v ${INSTALL_PATH}/conf/opsany-saas/log/log-prod.py:/opt/opsany/log/config/prod.py \
       -v ${INSTALL_PATH}/conf/opsany-saas/log/log-nginx.conf:/etc/nginx/http.d/default.conf \
       -v ${INSTALL_PATH}/conf/opsany-saas/log/log-nginx-main.conf:/etc/nginx/nginx.conf \
       -v ${INSTALL_PATH}/logs/log:/opt/opsany/logs/log \
       -v ${INSTALL_PATH}/uploads:/opt/opsany/uploads \
       -v /etc/localtime:/etc/localtime:ro \
       ${PAAS_DOCKER_REG}/opsany-saas-ee-log:${UPDATE_VERSION}
    
    # Django migrate
    docker exec -e BK_ENV="production" opsany-saas-ee-log /bin/sh -c \
    "python /opt/opsany/log/manage.py migrate --noinput >> ${SHELL_LOG} && python /opt/opsany/log/manage.py createcachetable django_cache > /dev/null"
    update_saas_version log 日志平台 ${LOG_SECRET_KEY}
}

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

    # Starter container
    docker pull ${PAAS_DOCKER_REG}/opsany-saas-ee-k8s:${UPDATE_VERSION}
    docker stop opsany-saas-ee-k8s && docker rm opsany-saas-ee-k8s
    docker run -d --restart=always --name opsany-saas-ee-k8s \
       -p 7014:80 \
       -v ${INSTALL_PATH}/conf/opsany-saas/k8s/k8s-supervisor.ini:/etc/supervisord.d/k8s.ini \
       -v ${INSTALL_PATH}/conf/opsany-saas/k8s/k8s-uwsgi.ini:/opt/opsany/uwsgi/k8s.ini \
       -v ${INSTALL_PATH}/conf/opsany-saas/k8s/k8s-init.py:/opt/opsany/k8s/config/__init__.py \
       -v ${INSTALL_PATH}/conf/opsany-saas/k8s/k8s-prod.py:/opt/opsany/k8s/config/prod.py \
       -v ${INSTALL_PATH}/conf/opsany-saas/k8s/k8s-nginx.conf:/etc/nginx/http.d/default.conf \
       -v ${INSTALL_PATH}/conf/opsany-saas/k8s/k8s-nginx-main.conf:/etc/nginx/nginx.conf \
       -v ${INSTALL_PATH}/logs/k8s:/opt/opsany/logs/k8s \
       -v ${INSTALL_PATH}/uploads:/opt/opsany/uploads \
       -v /etc/localtime:/etc/localtime:ro \
       ${PAAS_DOCKER_REG}/opsany-saas-ee-k8s:${UPDATE_VERSION}
    
    # Django migrate
    docker exec -e BK_ENV="production" opsany-saas-ee-k8s /bin/sh -c \
    "python /opt/opsany/k8s/manage.py migrate --noinput >> ${SHELL_LOG} && python /opt/opsany/k8s/manage.py createcachetable django_cache > /dev/null"
    update_saas_version k8s 容器平台 ${K8S_SECRET_KEY}

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
