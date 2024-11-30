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
SHELL_NAME="saas-ee-install.sh"
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
      shell_error_log "Please create config file install.config in ../"
      exit
elif [ ! -f ./ee-install.config ];then
      shell_error_log "Please create config file ee-install.config"
      exit
     
else
    grep '^[A-Z]' ../install.config > install.env
    cat ./ee-install.config >> install.env
    source ./install.env && rm -f install.env
    if [ -z "$ADMIN_PASSWORD" ];then
        source ${INSTALL_PATH}/conf/.passwd_env
    fi
    export MYSQL_PWD=${MYSQL_ROOT_PASSWORD}
fi

# Install initialization
install_init(){
    #SaaS Log Directory
    mkdir -p ${INSTALL_PATH}/logs/{event,auto,kbase,log,k8s,pipeline,deploy,prom}
    /bin/cp ./conf/nginx/opsany_paas_ee.config ${INSTALL_PATH}/conf/nginx-conf.d/opsany_paas.conf
    /bin/cp ../init/mongodb-init/mongodb_init_ee.js  ${INSTALL_PATH}/init/mongodb-init/mongodb_init_ee.js
    sed -i "s/DOMAIN_NAME/${DOMAIN_NAME}/g" ${INSTALL_PATH}/conf/nginx-conf.d/opsany_paas.conf
    sed -i "s/LOCAL_IP/${LOCAL_IP}/g" ${INSTALL_PATH}/conf/nginx-conf.d/opsany_paas.conf
    sed -i "s/DOMAIN_NAME/${DOMAIN_NAME}/g" ${INSTALL_PATH}/conf/nginx-conf.d/opsany_proxy.conf
    sed -i "s/LOCAL_IP/${LOCAL_IP}/g" ${INSTALL_PATH}/conf/nginx-conf.d/opsany_proxy.conf
    docker restart opsany-base-openresty
}

# MonogDB Initialize
mongodb_init(){
    shell_log "======MongoDB Initialize======"
    sed -i "s/MONGO_AUTO_PASSWORD/${MONGO_AUTO_PASSWORD}/g" ${INSTALL_PATH}/init/mongodb-init/mongodb_init_ee.js
    sed -i "s/MONGO_EVENT_PASSWORD/${MONGO_EVENT_PASSWORD}/g" ${INSTALL_PATH}/init/mongodb-init/mongodb_init_ee.js
    sed -i "s/MONGO_PROM_PASSWORD/${MONGO_PROM_PASSWORD}/g" ${INSTALL_PATH}/init/mongodb-init/mongodb_init_ee.js
    sed -i "s/MONGO_KBASE_PASSWORD/${MONGO_KBASE_PASSWORD}/g" ${INSTALL_PATH}/init/mongodb-init/mongodb_init_ee.js

    docker cp ${INSTALL_PATH}/init/mongodb-init/mongodb_init_ee.js opsany-base-mongodb:/opt/
    docker exec -e MONGO_INITDB_ROOT_USERNAME=$MONGO_INITDB_ROOT_USERNAME \
                -e MONGO_INITDB_ROOT_PASSWORD=$MONGO_INITDB_ROOT_PASSWORD \
                opsany-base-mongodb /bin/bash -c "/usr/bin/mongo -u $MONGO_INITDB_ROOT_USERNAME -p $MONGO_INITDB_ROOT_PASSWORD /opt/mongodb_init_ee.js" >> ${SHELL_LOG}

    shell_log "======MongoDB Initialize End======"
}

saas_event_deploy(){
    shell_log "======Start event======"
    #event
    mysql -h "${MYSQL_SERVER_IP}" -u root  -e "create database event DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;"
    mysql -h "${MYSQL_SERVER_IP}" -u root  -e "grant all on event.* to event@'%' identified by "\"${MYSQL_OPSANY_EVENT_PASSWORD}\"";"
    mysql -h "${MYSQL_SERVER_IP}" -u root  -e "grant all on event.* to opsany@'%' identified by "\"${MYSQL_OPSANY_PASSWORD}\"";" 

    # Register event
    EVENT_SECRET_KEY=$(uuid -v4)
    echo $EVENT_SECRET_KEY > ${INSTALL_PATH}/conf/.event_secret_key
    python3 ../../saas/register_online_saas.py --paas_domain https://${DOMAIN_NAME} --username admin --password ${ADMIN_PASSWORD} --saas_app_code event --saas_app_name 事件中心 --saas_app_version 2.2.3 --saas_app_secret_key ${EVENT_SECRET_KEY}

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
    
    
    #event
    sed -i "s/DOMAIN_NAME/$DOMAIN_NAME/g" ${INSTALL_PATH}/esb/apis/event/toolkit/configs.py
    sed -i "s#/t/event#/o/event#g" ${INSTALL_PATH}/esb/apis/event/toolkit/tools.py

    # Starter container
    docker pull ${PAAS_DOCKER_REG}/opsany-saas-ee-event:2.2.3
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
       ${PAAS_DOCKER_REG}/opsany-saas-ee-event:2.2.3
    
    # Django migrate
    docker exec -e BK_ENV="production" opsany-saas-ee-event /bin/sh -c \
    "python /opt/opsany/event/manage.py migrate --noinput && python /opt/opsany/event/manage.py createcachetable django_cache > /dev/null" >> ${SHELL_LOG}
}

saas_auto_deploy(){
    shell_log "======Start auto======"
    #auto
    mysql -h "${MYSQL_SERVER_IP}" -u root  -e "create database auto DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;"
    mysql -h "${MYSQL_SERVER_IP}" -u root  -e "grant all on auto.* to auto@'%' identified by "\"${MYSQL_OPSANY_AUTO_PASSWORD}\"";"
    mysql -h "${MYSQL_SERVER_IP}" -u root  -e "grant all on auto.* to opsany@'%' identified by "\"${MYSQL_OPSANY_PASSWORD}\"";" 

    # Register auto
    AUTO_SECRET_KEY=$(uuid -v4)
    echo $AUTO_SECRET_KEY > ${INSTALL_PATH}/conf/.auto_secret_key
    python3 ../../saas/register_online_saas.py --paas_domain https://${DOMAIN_NAME} --username admin --password ${ADMIN_PASSWORD} --saas_app_code auto --saas_app_name 智能巡检 --saas_app_version 2.2.3 --saas_app_secret_key ${AUTO_SECRET_KEY}

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
    
    #auto
    sed -i "s/DOMAIN_NAME/$DOMAIN_NAME/g" ${INSTALL_PATH}/esb/apis/auto/toolkit/configs.py
    sed -i "s#/t/auto#/o/auto#g" ${INSTALL_PATH}/esb/apis/auto/toolkit/tools.py

    # Starter container
    docker pull ${PAAS_DOCKER_REG}/opsany-saas-ee-auto:2.2.3
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
       ${PAAS_DOCKER_REG}/opsany-saas-ee-auto:2.2.3
    
    # Django migrate
    docker exec -e BK_ENV="production" opsany-saas-ee-auto /bin/sh -c \
    "python /opt/opsany/auto/manage.py migrate --noinput && python /opt/opsany/auto/manage.py createcachetable django_cache > /dev/null" >> ${SHELL_LOG}
}

saas_kbase_deploy(){
    shell_log "======Start kbase======"
    #kbase
    mysql -h "${MYSQL_SERVER_IP}" -u root  -e "create database kbase DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;"
    mysql -h "${MYSQL_SERVER_IP}" -u root  -e "grant all on kbase.* to kbase@'%' identified by "\"${MYSQL_OPSANY_KBASE_PASSWORD}\"";"
    mysql -h "${MYSQL_SERVER_IP}" -u root  -e "grant all on kbase.* to opsany@'%' identified by "\"${MYSQL_OPSANY_PASSWORD}\"";" 

    # Register kbase
    KBASE_SECRET_KEY=$(uuid -v4)
    echo $KBASE_SECRET_KEY > ${INSTALL_PATH}/conf/.kbase_secret_key
    python3 ../../saas/register_online_saas.py --paas_domain https://${DOMAIN_NAME} --username admin --password ${ADMIN_PASSWORD} --saas_app_code kbase --saas_app_name 知识库 --saas_app_version 2.2.3 --saas_app_secret_key ${KBASE_SECRET_KEY}

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
    
    #kbase
    sed -i "s/DOMAIN_NAME/$DOMAIN_NAME/g" ${INSTALL_PATH}/esb/apis/kbase/toolkit/configs.py
    sed -i "s#/t/kbase#/o/kbase#g" ${INSTALL_PATH}/esb/apis/kbase/toolkit/tools.py

    # Starter container
    docker pull ${PAAS_DOCKER_REG}/opsany-saas-ee-kbase:2.2.3
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
       ${PAAS_DOCKER_REG}/opsany-saas-ee-kbase:2.2.3
    
    # Django migrate
    docker exec -e BK_ENV="production" opsany-saas-ee-kbase /bin/sh -c \
    "python /opt/opsany/kbase/manage.py migrate --noinput && python /opt/opsany/kbase/manage.py createcachetable django_cache > /dev/null" >> ${SHELL_LOG}
}

saas_prom_deploy(){
    shell_log "======Start prom======"
    #prom
    mysql -h "${MYSQL_SERVER_IP}" -u root  -e "create database prom DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;"
    mysql -h "${MYSQL_SERVER_IP}" -u root  -e "grant all on prom.* to prom@'%' identified by "\"${MYSQL_OPSANY_PROM_PASSWORD}\"";"
    mysql -h "${MYSQL_SERVER_IP}" -u root  -e "grant all on prom.* to opsany@'%' identified by "\"${MYSQL_OPSANY_PASSWORD}\"";" 

    # Register prom
    PROM_SECRET_KEY=$(uuid -v4)
    echo $PROM_SECRET_KEY > ${INSTALL_PATH}/conf/.prom_secret_key
    python3 ../../saas/register_online_saas.py --paas_domain https://${DOMAIN_NAME} --username admin --password ${ADMIN_PASSWORD} --saas_app_code prom --saas_app_name 应用监控 --saas_app_version 2.2.3 --saas_app_secret_key ${PROM_SECRET_KEY}

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
    
    #prom
    sed -i "s/DOMAIN_NAME/$DOMAIN_NAME/g" ${INSTALL_PATH}/esb/apis/prom/toolkit/configs.py
    sed -i "s#/t/prom#/o/prom#g" ${INSTALL_PATH}/esb/apis/prom/toolkit/tools.py

    # Starter container
    docker pull ${PAAS_DOCKER_REG}/opsany-saas-ee-prom:2.2.3
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
       ${PAAS_DOCKER_REG}/opsany-saas-ee-prom:2.2.3
    
    # Django migrate
    docker exec -e BK_ENV="production" opsany-saas-ee-prom /bin/sh -c \
    "python /opt/opsany/prom/manage.py migrate --noinput && python /opt/opsany/prom/manage.py createcachetable django_cache > /dev/null" >> ${SHELL_LOG}
}

saas_log_deploy(){
    shell_log "======Start log======"
    #log
    mysql -h "${MYSQL_SERVER_IP}" -u root  -e "create database log DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;"
    mysql -h "${MYSQL_SERVER_IP}" -u root  -e "grant all on log.* to log@'%' identified by "\"${MYSQL_OPSANY_LOG_PASSWORD}\"";"
    mysql -h "${MYSQL_SERVER_IP}" -u root  -e "grant all on log.* to opsany@'%' identified by "\"${MYSQL_OPSANY_PASSWORD}\"";" 

    # Register log
    LOG_SECRET_KEY=$(uuid -v4)
    echo $LOG_SECRET_KEY > ${INSTALL_PATH}/conf/.log_secret_key
    python3 ../../saas/register_online_saas.py --paas_domain https://${DOMAIN_NAME} --username admin --password ${ADMIN_PASSWORD} --saas_app_code log --saas_app_name 日志平台 --saas_app_version 2.2.3 --saas_app_secret_key ${LOG_SECRET_KEY}

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
    
    #log
    sed -i "s/DOMAIN_NAME/$DOMAIN_NAME/g" ${INSTALL_PATH}/esb/apis/log/toolkit/configs.py
    sed -i "s#/t/log#/o/log#g" ${INSTALL_PATH}/esb/apis/log/toolkit/tools.py

    # Starter container
    docker pull ${PAAS_DOCKER_REG}/opsany-saas-ee-log:2.2.3
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
       ${PAAS_DOCKER_REG}/opsany-saas-ee-log:2.2.3
    
    # Django migrate
    docker exec -e BK_ENV="production" opsany-saas-ee-log /bin/sh -c \
    "python /opt/opsany/log/manage.py migrate --noinput && python /opt/opsany/log/manage.py createcachetable django_cache > /dev/null" >> ${SHELL_LOG}
}

saas_apm_deploy(){
    shell_log "======Start apm======"
    #apm
    mysql -h "${MYSQL_SERVER_IP}" -u root  -e "create database apm DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;"
    mysql -h "${MYSQL_SERVER_IP}" -u root  -e "grant all on apm.* to apm@'%' identified by "\"${MYSQL_OPSANY_APM_PASSWORD}\"";"
    mysql -h "${MYSQL_SERVER_IP}" -u root  -e "grant all on apm.* to opsany@'%' identified by "\"${MYSQL_OPSANY_PASSWORD}\"";" 

    # Register apm
    APM_SECRET_KEY=$(uuid -v4)
    echo $APM_SECRET_KEY > ${INSTALL_PATH}/conf/.apm_secret_key
    python3 ../../saas/register_online_saas.py --paas_domain https://${DOMAIN_NAME} --username admin --password ${ADMIN_PASSWORD} --saas_app_code apm --saas_app_name APM平台 --saas_app_version 2.2.3 --saas_app_secret_key ${APM_SECRET_KEY}

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
    
    #apm
    sed -i "s/DOMAIN_NAME/$DOMAIN_NAME/g" ${INSTALL_PATH}/esb/apis/apm/toolkit/configs.py
    sed -i "s#/t/apm#/o/apm#g" ${INSTALL_PATH}/esb/apis/apm/toolkit/tools.py

    # Starter container
    docker pull ${PAAS_DOCKER_REG}/opsany-saas-ee-apm:2.2.3
    docker run -d --restart=always --name opsany-saas-ee-apm \
       -p 7019:80 \
       -v ${INSTALL_PATH}/conf/opsany-saas/apm/apm-supervisor.ini:/etc/supervisord.d/apm.ini \
       -v ${INSTALL_PATH}/conf/opsany-saas/apm/apm-uwsgi.ini:/opt/opsany/uwsgi/apm.ini \
       -v ${INSTALL_PATH}/conf/opsany-saas/apm/apm-init.py:/opt/opsany/apm/config/__init__.py \
       -v ${INSTALL_PATH}/conf/opsany-saas/apm/apm-prod.py:/opt/opsany/apm/config/prod.py \
       -v ${INSTALL_PATH}/conf/opsany-saas/apm/apm-nginx.conf:/etc/nginx/http.d/default.conf \
       -v ${INSTALL_PATH}/logs/apm:/opt/opsany/logs/apm \
       -v ${INSTALL_PATH}/uploads:/opt/opsany/uploads \
       -v /etc/localtime:/etc/localtime:ro \
       ${PAAS_DOCKER_REG}/opsany-saas-ee-apm:2.2.3
 # Django migrate
    docker exec -e BK_ENV="production" opsany-saas-ee-apm /bin/sh -c \
    "python /opt/opsany/apm/manage.py migrate --noinput && python /opt/opsany/apm/manage.py createcachetable django_cache > /dev/null" >> ${SHELL_LOG}
}

saas_k8s_deploy(){
    shell_log "======Start k8s======"
    #k8s
    mysql -h "${MYSQL_SERVER_IP}" -u root  -e "create database k8s DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;"
    mysql -h "${MYSQL_SERVER_IP}" -u root  -e "grant all on k8s.* to k8s@'%' identified by "\"${MYSQL_OPSANY_K8S_PASSWORD}\"";"
    mysql -h "${MYSQL_SERVER_IP}" -u root  -e "grant all on k8s.* to opsany@'%' identified by "\"${MYSQL_OPSANY_PASSWORD}\"";" 

    # Register k8s
    K8S_SECRET_KEY=$(uuid -v4)
    echo $K8S_SECRET_KEY > ${INSTALL_PATH}/conf/.k8s_secret_key
    python3 ../../saas/register_online_saas.py --paas_domain https://${DOMAIN_NAME} --username admin --password ${ADMIN_PASSWORD} --saas_app_code k8s --saas_app_name 容器平台 --saas_app_version 2.2.3 --saas_app_secret_key ${K8S_SECRET_KEY}

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
    
    #k8s
    sed -i "s/DOMAIN_NAME/$DOMAIN_NAME/g" ${INSTALL_PATH}/esb/apis/k8s/toolkit/configs.py
    sed -i "s#/t/k8s#/o/k8s#g" ${INSTALL_PATH}/esb/apis/k8s/toolkit/tools.py

    # Starter container
    docker pull ${PAAS_DOCKER_REG}/opsany-saas-ee-k8s:2.2.3
    docker run -d --restart=always --name opsany-saas-ee-k8s \
       -p 7014:80 \
       -v ${INSTALL_PATH}/conf/opsany-saas/k8s/k8s-supervisor.ini:/etc/supervisord.d/k8s.ini \
       -v ${INSTALL_PATH}/conf/opsany-saas/k8s/k8s-uwsgi.ini:/opt/opsany/uwsgi/k8s.ini \
       -v ${INSTALL_PATH}/conf/opsany-saas/k8s/k8s-init.py:/opt/opsany/k8s/config/__init__.py \
       -v ${INSTALL_PATH}/conf/opsany-saas/k8s/k8s-prod.py:/opt/opsany/k8s/config/prod.py \
       -v ${INSTALL_PATH}/conf/opsany-saas/k8s/k8s-nginx.conf:/etc/nginx/http.d/default.conf \
       -v ${INSTALL_PATH}/logs/k8s:/opt/opsany/logs/k8s \
       -v ${INSTALL_PATH}/uploads:/opt/opsany/uploads \
       -v /etc/localtime:/etc/localtime:ro \
       ${PAAS_DOCKER_REG}/opsany-saas-ee-k8s:2.2.3
    
    # Django migrate
    docker exec -e BK_ENV="production" opsany-saas-ee-k8s /bin/sh -c \
    "python /opt/opsany/k8s/manage.py migrate --noinput && python /opt/opsany/k8s/manage.py createcachetable django_cache > /dev/null" >> ${SHELL_LOG}
}

saas_ee_init(){
    shell_log "======OpsAny User Initialize======"
    sleep 3
    python3 ./sync-user-script.py --domain https://${DOMAIN_NAME} --paas_username admin --paas_password ${ADMIN_PASSWORD} --app_code event auto k8s kbase log prom
    python3 ./saas-ee-init.py --domain https://${DOMAIN_NAME} --username admin --password ${ADMIN_PASSWORD} --init_type menu,nav,temp,home_page
    docker restart opsany-paas-esb
    shell_warning_log "======OpsAny: Make Ops Perfect======" 
}

# Main
main(){
    case "$1" in
    apm)
        saas_apm_deploy
        ;;
    all)
        install_init
        mongodb_init
        saas_event_deploy
        saas_auto_deploy
        saas_k8s_deploy
        saas_kbase_deploy
        saas_log_deploy
        saas_apm_deploy
        saas_prom_deploy
        saas_ee_init
        ;;
	help|*)
	    echo $"Usage: $0 {apm|all|help}"
	    ;;
    esac
}

main $1 
