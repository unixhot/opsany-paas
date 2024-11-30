#!/bin/bash
#******************************************
# Author:       Jason Zhao
# Email:        zhaoshundong@opsany.com
# Organization: OpsAny https://www.opsany.com/
# Description:  OpsAny SAAS Community Edition 1.7.0 Update Script
#******************************************

# Data/Time Variables
CTIME=$(date "+%Y-%m-%d-%H-%M")

# Shell Envionment Variables
CDIR=$(pwd)
SHELL_NAME="update-1.7.0.sh"
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
if [ ! -f ./install.config ];then
      shell_error_log "Please Change Directory to ${INSTALL_PATH}/install"
      exit
else
    echo 'MYSQL_OPSANY_LOG_PASSWORD="OpsAny@2020"' >> install.config
    echo 'MYSQL_OPSANY_PIPELINE_PASSWORD="OpsAny@2020"' >> install.config
    echo 'MYSQL_OPSANY_DEPLOY_PASSWORD="OpsAny@2020"' >> install.config
    grep '^[A-Z]' install.config > install.env
    source ./install.env && rm -f install.env
    if [ -z "$ADMIN_PASSWORD" ];then
        source ${INSTALL_PATH}/conf/.passwd_env
    fi
fi

# Install initialization
update_init(){
    #SaaS Log Directory
    mkdir -p ${INSTALL_PATH}/logs/{event,auto,kbase,log,k8s,pipeline,deploy,prom}
    echo '36e2a60c-9db7-11ec-be19-00163e105ceb' > ${INSTALL_PATH}/conf/.deploy_secret_key
    echo '821eab44-a9f5-11ec-8388-00163e105ceb' > ${INSTALL_PATH}/conf/.pipeline_secret_key
    echo '59fedda4-f740-11eb-8c90-00163e105ceb' > ${INSTALL_PATH}/conf/.event_secret_key
    echo '2c379640-f740-11eb-b0b0-00163e105ceb' > ${INSTALL_PATH}/conf/.auto_secret_key
    echo '17c7c922-205d-11ed-af64-fa163e075e0b' > ${INSTALL_PATH}/conf/.k8s_secret_key
    echo '2a609e1a-205d-11ed-9453-fa163e075e0b' > ${INSTALL_PATH}/conf/.prom_secret_key
    echo '8bae0d18-c226-11ed-8887-fa163e075e0b' > ${INSTALL_PATH}/conf/.kbase_secret_key
    echo '8bae0d18-c227-11ed-8887-fa163e075e0b' > ${INSTALL_PATH}/conf/.log_secret_key
}

openresty_update(){
    shell_log "======Update Openresty======"
    /bin/cp conf/nginx-conf.d/opsany_paas_ee.config ${INSTALL_PATH}/conf/nginx-conf.d/opsany_paas.conf
    sed -i "s/DOMAIN_NAME/${DOMAIN_NAME}/g" ${INSTALL_PATH}/conf/nginx-conf.d/opsany_paas.conf
    sed -i "s/LOCAL_IP/${LOCAL_IP}/g" ${INSTALL_PATH}/conf/nginx-conf.d/opsany_paas.conf
    docker restart opsany-openresty
}

# SaaS Update
saas_event_update(){
    shell_log "======Update event======"
    # Modify configuration
    /bin/cp -r conf/opsany-saas/event/* ${INSTALL_PATH}/conf/opsany-saas/event/
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
    docker pull ${PAAS_DOCKER_REG}/opsany-saas-ee-event:1.7.0
    docker stop opsany-saas-ee-event && docker rm opsany-saas-ee-event
    docker run -d --restart=always --name opsany-saas-ee-event \
       -p 7011:80 \
       -v ${INSTALL_PATH}/conf/opsany-saas/event/event-supervisor.ini:/etc/supervisord.d/event.ini \
       -v ${INSTALL_PATH}/conf/opsany-saas/event/event-uwsgi.ini:/opt/opsany/uwsgi/event.ini \
       -v ${INSTALL_PATH}/conf/opsany-saas/event/event-init.py:/opt/opsany/event/config/__init__.py \
       -v ${INSTALL_PATH}/conf/opsany-saas/event/event-prod.py:/opt/opsany/event/config/prod.py \
       -v ${INSTALL_PATH}/conf/opsany-saas/event/event-nginx.conf:/etc/nginx/http.d/default.conf \
       -v ${INSTALL_PATH}/logs/event:/opt/opsany/logs/event \
       -v ${INSTALL_PATH}/uploads:/opt/opsany/uploads \
       -v /etc/localtime:/etc/localtime:ro \
       ${PAAS_DOCKER_REG}/opsany-saas-ee-event:1.7.0
    
    # Django migrate
    docker exec -e BK_ENV="production" opsany-saas-ee-event /bin/sh -c \
    "python /opt/opsany/event/manage.py migrate --noinput >> ${SHELL_LOG} && python /opt/opsany/event/manage.py createcachetable django_cache > /dev/null"
}

saas_auto_update(){
    shell_log "======Update auto======"

    # Modify configuration
    /bin/cp -r conf/opsany-saas/auto/* ${INSTALL_PATH}/conf/opsany-saas/auto/
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
    docker pull ${PAAS_DOCKER_REG}/opsany-saas-ee-auto:1.7.0
    docker stop opsany-saas-ee-auto && docker rm opsany-saas-ee-auto
    docker run -d --restart=always --name opsany-saas-ee-auto \
       -p 7012:80 \
       -v ${INSTALL_PATH}/conf/opsany-saas/auto/auto-supervisor.ini:/etc/supervisord.d/auto.ini \
       -v ${INSTALL_PATH}/conf/opsany-saas/auto/auto-uwsgi.ini:/opt/opsany/uwsgi/auto.ini \
       -v ${INSTALL_PATH}/conf/opsany-saas/auto/auto-init.py:/opt/opsany/auto/config/__init__.py \
       -v ${INSTALL_PATH}/conf/opsany-saas/auto/auto-prod.py:/opt/opsany/auto/config/prod.py \
       -v ${INSTALL_PATH}/conf/opsany-saas/auto/auto-nginx.conf:/etc/nginx/http.d/default.conf \
       -v ${INSTALL_PATH}/logs/auto:/opt/opsany/logs/auto \
       -v ${INSTALL_PATH}/uploads:/opt/opsany/uploads \
       -v /etc/localtime:/etc/localtime:ro \
       ${PAAS_DOCKER_REG}/opsany-saas-ee-auto:1.7.0
    
    # Django migrate
    docker exec -e BK_ENV="production" opsany-saas-ee-auto /bin/sh -c \
    "python /opt/opsany/auto/manage.py migrate --noinput >> ${SHELL_LOG} && python /opt/opsany/auto/manage.py createcachetable django_cache > /dev/null"
}

saas_kbase_update(){
    shell_log "======Update kbase======"

    # Modify configuration
    /bin/cp -r conf/opsany-saas/kbase/* ${INSTALL_PATH}/conf/opsany-saas/kbase/
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
    docker pull ${PAAS_DOCKER_REG}/opsany-saas-ee-kbase:1.7.0
    docker stop opsany-saas-ee-kbase && docker rm opsany-saas-ee-kbase
    docker run -d --restart=always --name opsany-saas-ee-kbase \
       -p 7013:80 \
       -v ${INSTALL_PATH}/conf/opsany-saas/kbase/kbase-supervisor.ini:/etc/supervisord.d/kbase.ini \
       -v ${INSTALL_PATH}/conf/opsany-saas/kbase/kbase-uwsgi.ini:/opt/opsany/uwsgi/kbase.ini \
       -v ${INSTALL_PATH}/conf/opsany-saas/kbase/kbase-init.py:/opt/opsany/kbase/config/__init__.py \
       -v ${INSTALL_PATH}/conf/opsany-saas/kbase/kbase-prod.py:/opt/opsany/kbase/config/prod.py \
       -v ${INSTALL_PATH}/conf/opsany-saas/kbase/kbase-nginx.conf:/etc/nginx/http.d/default.conf \
       -v ${INSTALL_PATH}/logs/kbase:/opt/opsany/logs/kbase \
       -v ${INSTALL_PATH}/uploads:/opt/opsany/uploads \
       -v /etc/localtime:/etc/localtime:ro \
       ${PAAS_DOCKER_REG}/opsany-saas-ee-kbase:1.7.0
    
    # Django migrate
    docker exec -e BK_ENV="production" opsany-saas-ee-kbase /bin/sh -c \
    "python /opt/opsany/kbase/manage.py migrate --noinput >> ${SHELL_LOG} && python /opt/opsany/kbase/manage.py createcachetable django_cache > /dev/null"
}

saas_prom_update(){
    shell_log "======Update prom======"

    # Modify configuration
    /bin/cp -r conf/opsany-saas/prom/* ${INSTALL_PATH}/conf/opsany-saas/prom/
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
    docker pull ${PAAS_DOCKER_REG}/opsany-saas-ee-prom:1.7.0
    docker stop opsany-saas-ee-prom && docker rm opsany-saas-ee-prom
    docker run -d --restart=always --name opsany-saas-ee-prom \
       -p 7015:80 \
       -v ${INSTALL_PATH}/conf/opsany-saas/prom/prom-supervisor.ini:/etc/supervisord.d/prom.ini \
       -v ${INSTALL_PATH}/conf/opsany-saas/prom/prom-uwsgi.ini:/opt/opsany/uwsgi/prom.ini \
       -v ${INSTALL_PATH}/conf/opsany-saas/prom/prom-init.py:/opt/opsany/prom/config/__init__.py \
       -v ${INSTALL_PATH}/conf/opsany-saas/prom/prom-prod.py:/opt/opsany/prom/config/prod.py \
       -v ${INSTALL_PATH}/conf/opsany-saas/prom/prom-nginx.conf:/etc/nginx/http.d/default.conf \
       -v ${INSTALL_PATH}/logs/prom:/opt/opsany/logs/prom \
       -v ${INSTALL_PATH}/uploads:/opt/opsany/uploads \
       -v /etc/localtime:/etc/localtime:ro \
       ${PAAS_DOCKER_REG}/opsany-saas-ee-prom:1.7.0
    
    # Django migrate
    docker exec -e BK_ENV="production" opsany-saas-ee-prom /bin/sh -c \
    "python /opt/opsany/prom/manage.py migrate --noinput >> ${SHELL_LOG} && python /opt/opsany/prom/manage.py createcachetable django_cache > /dev/null"
}

saas_pipeline_update(){
    shell_log "======Update pipeline======"
    # Modify configuration
    /bin/cp -r conf/opsany-saas/pipeline/* ${INSTALL_PATH}/conf/opsany-saas/pipeline/
    PIPELINE_SECRET_KEY=$(cat ${INSTALL_PATH}/conf/.pipeline_secret_key)
    sed -i "s/DOMAIN_NAME/${DOMAIN_NAME}/g" ${INSTALL_PATH}/conf/opsany-saas/pipeline/pipeline-init.py
    sed -i "s/PIPELINE_SECRET_KEY/${PIPELINE_SECRET_KEY}/g" ${INSTALL_PATH}/conf/opsany-saas/pipeline/pipeline-init.py
    sed -i "s/MYSQL_SERVER_IP/${MYSQL_SERVER_IP}/g" ${INSTALL_PATH}/conf/opsany-saas/pipeline/pipeline-prod.py
    sed -i "s/MYSQL_SERVER_PORT/${MYSQL_SERVER_PORT}/g" ${INSTALL_PATH}/conf/opsany-saas/pipeline/pipeline-prod.py
    sed -i "s/MYSQL_OPSANY_PIPELINE_PASSWORD/${MYSQL_OPSANY_PIPELINE_PASSWORD}/g" ${INSTALL_PATH}/conf/opsany-saas/pipeline/pipeline-prod.py
    sed -i "s/MONGO_SERVER_IP/${MONGO_SERVER_IP}/g" ${INSTALL_PATH}/conf/opsany-saas/pipeline/pipeline-prod.py
    sed -i "s/MONGO_SERVER_PORT/${MONGO_SERVER_PORT}/g" ${INSTALL_PATH}/conf/opsany-saas/pipeline/pipeline-prod.py
    sed -i "s/MONGO_DEVOPS_PASSWORD/${MONGO_DEVOPS_PASSWORD}/g" ${INSTALL_PATH}/conf/opsany-saas/pipeline/pipeline-prod.py
    sed -i "s/REDIS_SERVER_IP/${REDIS_SERVER_IP}/g" ${INSTALL_PATH}/conf/opsany-saas/pipeline/pipeline-prod.py
    sed -i "s/REDIS_SERVER_PORT/${REDIS_SERVER_PORT}/g" ${INSTALL_PATH}/conf/opsany-saas/pipeline/pipeline-prod.py
    sed -i "s/REDIS_SERVER_USER/${REDIS_SERVER_USER}/g" ${INSTALL_PATH}/conf/opsany-saas/pipeline/pipeline-prod.py
    sed -i "s/REDIS_SERVER_PASSWORD/${REDIS_SERVER_PASSWORD}/g" ${INSTALL_PATH}/conf/opsany-saas/pipeline/pipeline-prod.py

    # Starter container
    docker pull ${PAAS_DOCKER_REG}/opsany-saas-ee-pipeline:1.7.0
    docker stop opsany-saas-ee-pipeline && docker rm opsany-saas-ee-pipeline
    docker run -d --restart=always --name opsany-saas-ee-pipeline \
       -p 7017:80 \
       -v ${INSTALL_PATH}/conf/opsany-saas/pipeline/pipeline-supervisor.ini:/etc/supervisord.d/pipeline.ini \
       -v ${INSTALL_PATH}/conf/opsany-saas/pipeline/pipeline-uwsgi.ini:/opt/opsany/uwsgi/pipeline.ini \
       -v ${INSTALL_PATH}/conf/opsany-saas/pipeline/pipeline-init.py:/opt/opsany/pipeline/config/__init__.py \
       -v ${INSTALL_PATH}/conf/opsany-saas/pipeline/pipeline-prod.py:/opt/opsany/pipeline/config/prod.py \
       -v ${INSTALL_PATH}/conf/opsany-saas/pipeline/pipeline-nginx.conf:/etc/nginx/http.d/default.conf \
       -v ${INSTALL_PATH}/logs/pipeline:/opt/opsany/logs/pipeline \
       -v ${INSTALL_PATH}/uploads:/opt/opsany/uploads \
       -v /etc/localtime:/etc/localtime:ro \
       ${PAAS_DOCKER_REG}/opsany-saas-ee-pipeline:1.7.0
    
    # Django migrate
    docker exec -e BK_ENV="production" opsany-saas-ee-pipeline /bin/sh -c \
    "python /opt/opsany/pipeline/manage.py migrate --noinput >> ${SHELL_LOG} && python /opt/opsany/pipeline/manage.py createcachetable django_cache > /dev/null"
}

saas_deploy_update(){
    shell_log "======Update deploy======"
    # Modify configuration
    /bin/cp -r conf/opsany-saas/deploy/* ${INSTALL_PATH}/conf/opsany-saas/deploy/
    DEPLOY_SECRET_KEY=$(cat ${INSTALL_PATH}/conf/.deploy_secret_key)
    sed -i "s/DOMAIN_NAME/${DOMAIN_NAME}/g" ${INSTALL_PATH}/conf/opsany-saas/deploy/deploy-init.py
    sed -i "s/DEPLOY_SECRET_KEY/${DEPLOY_SECRET_KEY}/g" ${INSTALL_PATH}/conf/opsany-saas/deploy/deploy-init.py
    sed -i "s/MYSQL_SERVER_IP/${MYSQL_SERVER_IP}/g" ${INSTALL_PATH}/conf/opsany-saas/deploy/deploy-prod.py
    sed -i "s/MYSQL_SERVER_PORT/${MYSQL_SERVER_PORT}/g" ${INSTALL_PATH}/conf/opsany-saas/deploy/deploy-prod.py
    sed -i "s/MYSQL_OPSANY_DEPLOY_PASSWORD/${MYSQL_OPSANY_DEPLOY_PASSWORD}/g" ${INSTALL_PATH}/conf/opsany-saas/deploy/deploy-prod.py
    sed -i "s/MONGO_SERVER_IP/${MONGO_SERVER_IP}/g" ${INSTALL_PATH}/conf/opsany-saas/deploy/deploy-prod.py
    sed -i "s/MONGO_SERVER_PORT/${MONGO_SERVER_PORT}/g" ${INSTALL_PATH}/conf/opsany-saas/deploy/deploy-prod.py
    sed -i "s/MONGO_DEVOPS_PASSWORD/${MONGO_DEVOPS_PASSWORD}/g" ${INSTALL_PATH}/conf/opsany-saas/deploy/deploy-prod.py
    sed -i "s/REDIS_SERVER_IP/${REDIS_SERVER_IP}/g" ${INSTALL_PATH}/conf/opsany-saas/deploy/deploy-prod.py
    sed -i "s/REDIS_SERVER_PORT/${REDIS_SERVER_PORT}/g" ${INSTALL_PATH}/conf/opsany-saas/deploy/deploy-prod.py
    sed -i "s/REDIS_SERVER_USER/${REDIS_SERVER_USER}/g" ${INSTALL_PATH}/conf/opsany-saas/deploy/deploy-prod.py
    sed -i "s/REDIS_SERVER_PASSWORD/${REDIS_SERVER_PASSWORD}/g" ${INSTALL_PATH}/conf/opsany-saas/deploy/deploy-prod.py

    # Starter container
    docker pull ${PAAS_DOCKER_REG}/opsany-saas-ee-deploy:1.7.0
    docker stop opsany-saas-ee-deploy && docker rm opsany-saas-ee-deploy
    docker run -d --restart=always --name opsany-saas-ee-deploy \
       -p 7018:80 \
       -v ${INSTALL_PATH}/conf/opsany-saas/deploy/deploy-supervisor.ini:/etc/supervisord.d/deploy.ini \
       -v ${INSTALL_PATH}/conf/opsany-saas/deploy/deploy-uwsgi.ini:/opt/opsany/uwsgi/deploy.ini \
       -v ${INSTALL_PATH}/conf/opsany-saas/deploy/deploy-init.py:/opt/opsany/deploy/config/__init__.py \
       -v ${INSTALL_PATH}/conf/opsany-saas/deploy/deploy-prod.py:/opt/opsany/deploy/config/prod.py \
       -v ${INSTALL_PATH}/conf/opsany-saas/deploy/deploy-nginx.conf:/etc/nginx/http.d/default.conf \
       -v ${INSTALL_PATH}/logs/deploy:/opt/opsany/logs/deploy \
       -v ${INSTALL_PATH}/uploads:/opt/opsany/uploads \
       -v /etc/localtime:/etc/localtime:ro \
       ${PAAS_DOCKER_REG}/opsany-saas-ee-deploy:1.7.0
    
    # Django migrate
    docker exec -e BK_ENV="production" opsany-saas-ee-deploy /bin/sh -c \
    "python /opt/opsany/deploy/manage.py migrate --noinput >> ${SHELL_LOG} && python /opt/opsany/deploy/manage.py createcachetable django_cache > /dev/null"
}

saas_log_update(){
    shell_log "======Update log======"
    # Modify configuration
    /bin/cp -r conf/opsany-saas/log/* ${INSTALL_PATH}/conf/opsany-saas/log/
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
    docker pull ${PAAS_DOCKER_REG}/opsany-saas-ee-log:1.7.0
    docker stop opsany-saas-ee-log && docker rm opsany-saas-ee-log
    docker run -d --restart=always --name opsany-saas-ee-log \
       -p 7016:80 \
       -v ${INSTALL_PATH}/conf/opsany-saas/log/log-supervisor.ini:/etc/supervisord.d/log.ini \
       -v ${INSTALL_PATH}/conf/opsany-saas/log/log-uwsgi.ini:/opt/opsany/uwsgi/log.ini \
       -v ${INSTALL_PATH}/conf/opsany-saas/log/log-init.py:/opt/opsany/log/config/__init__.py \
       -v ${INSTALL_PATH}/conf/opsany-saas/log/log-prod.py:/opt/opsany/log/config/prod.py \
       -v ${INSTALL_PATH}/conf/opsany-saas/log/log-nginx.conf:/etc/nginx/http.d/default.conf \
       -v ${INSTALL_PATH}/logs/log:/opt/opsany/logs/log \
       -v ${INSTALL_PATH}/uploads:/opt/opsany/uploads \
       -v /etc/localtime:/etc/localtime:ro \
       ${PAAS_DOCKER_REG}/opsany-saas-ee-log:1.7.0
    
    # Django migrate
    docker exec -e BK_ENV="production" opsany-saas-ee-log /bin/sh -c \
    "python /opt/opsany/log/manage.py migrate --noinput >> ${SHELL_LOG} && python /opt/opsany/log/manage.py createcachetable django_cache > /dev/null"
}

saas_k8s_update(){
    shell_log "======Update k8s======"
    # Modify configuration
    /bin/cp -r conf/opsany-saas/k8s/* ${INSTALL_PATH}/conf/opsany-saas/k8s/
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
    docker pull ${PAAS_DOCKER_REG}/opsany-saas-ee-k8s:1.7.0
    docker stop opsany-saas-ee-k8s && docker rm opsany-saas-ee-k8s
    docker run -d --restart=always --name opsany-saas-ee-k8s \
       -p 7014:80 \
       -v ${INSTALL_PATH}/conf/opsany-saas/k8s/k8s-supervisor.ini:/etc/supervisord.d/k8s.ini \
       -v ${INSTALL_PATH}/conf/opsany-saas/k8s/k8s-uwsgi.ini:/opt/opsany/uwsgi/k8s.ini \
       -v ${INSTALL_PATH}/conf/opsany-saas/k8s/k8s-init.py:/opt/opsany/k8s/config/__init__.py \
       -v ${INSTALL_PATH}/conf/opsany-saas/k8s/k8s-prod.py:/opt/opsany/k8s/config/prod.py \
       -v ${INSTALL_PATH}/conf/opsany-saas/k8s/k8s-nginx.conf:/etc/nginx/http.d/default.conf \
       -v ${INSTALL_PATH}/k8ss/k8s:/opt/opsany/k8ss/k8s \
       -v ${INSTALL_PATH}/uploads:/opt/opsany/uploads \
       -v /etc/localtime:/etc/localtime:ro \
       ${PAAS_DOCKER_REG}/opsany-saas-ee-k8s:1.7.0
    
    # Django migrate
    docker exec -e BK_ENV="production" opsany-saas-ee-k8s /bin/sh -c \
    "python /opt/opsany/k8s/manage.py migrate --noinput >> ${SHELL_LOG} && python /opt/opsany/k8s/manage.py createcachetable django_cache > /dev/null"
}

saas_ee_init(){
    shell_log "======OpsAny User Initialize======"
    sleep 3
    python3 ../saas/sync-user-script.py --domain https://${DOMAIN_NAME} --paas_username admin --paas_password ${ADMIN_PASSWORD} --app_code event auto k8s kbase log prom
    shell_warning_log "======OpsAny: Make Ops Perfect======" 
}



# Main
# Main
main(){
    case "$1" in
    all)
        update_init
        openresty_update
	    saas_k8s_update
        saas_event_update
        saas_auto_update
        saas_kbase_update
        saas_prom_update
        saas_log_update
        saas_pipeline_update
        saas_deploy_update
        saas_ee_init
        ;;
	help|*)
	    echo $"Usage: $0 {all|help}"
	    ;;
    esac
}

main $1 

