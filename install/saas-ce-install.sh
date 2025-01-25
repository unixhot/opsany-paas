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
SHELL_NAME="saas-ce-install.sh"
SHELL_LOG="${SHELL_NAME}.log"
ADMIN_PASSWORD="admin"
SAAS_VERSION=2.2.4

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
      shell_error_log "======Error: Please Change Directory to ${INSTALL_PATH}/install======"
      exit
else
    grep '^[A-Z]' install.config > install.env
    source ./install.env && rm -f install.env
    export MYSQL_PWD=${MYSQL_ROOT_PASSWORD}
fi

# Install initialization
install_init(){
    #SaaS Log Directory
    mkdir -p ${INSTALL_PATH}/logs/{rbac,workbench,cmdb,control,job,monitor,cmp,bastion,devops,pipeline,repo,code,deploy,proxy}
}

# Start Proxy
proxy_install(){
    cd ${CDIR}
    # Proxy config
    CONTROL_SECRET_KEY=$(uuid -v4)
    echo $CONTROL_SECRET_KEY > ${INSTALL_PATH}/conf/.control_secret_key
    CONTROL_SECRET_KEY_PROXY=$(cat ${INSTALL_PATH}/conf/.control_secret_key)
    sed -i "s/REDIS_SERVER_IP/${REDIS_SERVER_IP}/g" ${INSTALL_PATH}/conf/proxy/settings_production.py.proxy
    sed -i "s/REDIS_SERVER_PASSWORD/${REDIS_SERVER_PASSWORD}/g" ${INSTALL_PATH}/conf/proxy/settings_production.py.proxy
    sed -i "s/MYSQL_SERVER_IP/${MYSQL_SERVER_IP}/g" ${INSTALL_PATH}/conf/proxy/settings_production.py.proxy
    sed -i "s/MYSQL_OPSANY_PASSWORD/${MYSQL_OPSANY_PASSWORD}/g" ${INSTALL_PATH}/conf/proxy/settings_production.py.proxy
    sed -i "s/local-proxy.opsany.com/${PROXY_LOCAL_IP}/g" ${INSTALL_PATH}/conf/proxy/settings_production.py.proxy
    sed -i "s/public-proxy.opsany.com/${PROXY_PUBLIC_IP}/g" ${INSTALL_PATH}/conf/proxy/settings_production.py.proxy
    sed -i "s/LOCAL_IP/${PROXY_PUBLIC_IP} ${PROXY_LOCAL_IP}/g" ${INSTALL_PATH}/conf/proxy/nginx-conf.d/nginx_proxy.conf
    sed -i "s/DOMAIN_NAME/${PROXY_PUBLIC_IP} ${PROXY_LOCAL_IP}/g" ${INSTALL_PATH}/conf/proxy/nginx-conf.d/nginx_proxy.conf
    #sed -i "s/RABBIT_SERVER_IP/${RABBIT_SERVER_IP}/g" ${INSTALL_PATH}/conf/proxy/settings_production.py.proxy
    #sed -i "s/RABBITMQ_DEFAULT_USER/${RABBITMQ_DEFAULT_USER}/g" ${INSTALL_PATH}/conf/proxy/settings_production.py.proxy
    #sed -i "s/RABBITMQ_DEFAULT_PASS/${RABBITMQ_DEFAULT_PASS}/g" ${INSTALL_PATH}/conf/proxy/settings_production.py.proxy
    sed -i "s/CONTROL_SECRET_KEY_PROXY/${CONTROL_SECRET_KEY_PROXY}/g" ${INSTALL_PATH}/conf/proxy/settings_production.py.proxy

    # For Ansible
    cp ../saas/invscript_proxy.py ${INSTALL_PATH}/conf/proxy/
    sed -i "s/LOCALHOST/${MYSQL_SERVER_IP}/g" ${INSTALL_PATH}/conf/proxy/invscript_proxy.py
    sed -i "s/PROXY_PASSWORD/${MYSQL_OPSANY_PASSWORD}/g" ${INSTALL_PATH}/conf/proxy/invscript_proxy.py
    sed -i "s/CONTROL_SECRET_KEY/${CONTROL_SECRET_KEY}/g" ${INSTALL_PATH}/conf/proxy/invscript_proxy.py
    chmod +x ${INSTALL_PATH}/conf/proxy/invscript_proxy.py

    shell_log "======Proxy: Start Proxy======"
    docker pull ${PAAS_DOCKER_REG}/opsany-paas-proxy:${SAAS_VERSION}
    docker run --restart=always --name opsany-paas-proxy -d \
        -p 4505:4505 -p 4506:4506 -p 8010:8010 \
        -v ${INSTALL_PATH}/logs/proxy:/opt/opsany/logs/proxy \
        -v ${INSTALL_PATH}/proxy-volume/certs/:/etc/pki/tls/certs/ \
        -v ${INSTALL_PATH}/proxy-volume/etc/salt/:/etc/salt/ \
        -v ${INSTALL_PATH}/proxy-volume/cache/:/var/cache/salt/ \
        -v ${INSTALL_PATH}/proxy-volume/srv/salt:/srv/salt/ \
        -v ${INSTALL_PATH}/proxy-volume/srv/pillar:/srv/pillar/ \
        -v ${INSTALL_PATH}/proxy-volume/srv/playbook:/srv/playbook/ \
        -v ${INSTALL_PATH}/proxy-volume/pki:/opt/opsany/pki \
        -v ${INSTALL_PATH}/uploads:/opt/opsany/uploads \
        -v ${INSTALL_PATH}/conf/proxy/settings_production.py.proxy:/opt/opsany-proxy/config/prod.py \
        -v ${INSTALL_PATH}/conf/proxy/invscript_proxy.py:/opt/opsany-proxy/invscript_proxy.py \
        -v ${INSTALL_PATH}/conf/proxy/proxy.ini:/etc/supervisord.d/proxy.ini \
        -v ${INSTALL_PATH}/conf/proxy/saltapi.ini:/etc/supervisord.d/saltapi.ini \
        -v ${INSTALL_PATH}/conf/proxy/saltmaster.ini:/etc/supervisord.d/saltmaster.ini \
        -v ${INSTALL_PATH}/prometheus-volume/conf/alertmanager.yml:/opt/opsany/alertmanager.yml \
        -v /etc/localtime:/etc/localtime:ro \
        ${PAAS_DOCKER_REG}/opsany-paas-proxy:${SAAS_VERSION}

    # OpsAny Database Init
    docker exec -e OPS_ANY_ENV=production \
        opsany-paas-proxy /bin/sh -c "/usr/local/bin/python3 /opt/opsany-proxy/manage.py migrate --noinput" >> ${SHELL_LOG} 2>&1
    docker exec -e OPS_ANY_ENV=production \
        opsany-paas-proxy /bin/sh -c "/usr/local/bin/python3 /opt/opsany-proxy/manage.py create_superuser --username=opsany --email=proxy@example.com --password=$MYSQL_OPSANY_PASSWORD"
}

# MonogDB Initialize
mongodb_init(){
    shell_log "======MongoDB: MongoDB Initialize======"
    cd ${CDIR}
    sed -i "s/MONGO_WORKBENCH_PASSWORD/${MONGO_WORKBENCH_PASSWORD}/g" ${INSTALL_PATH}/init/mongodb-init/mongodb_init.js
    sed -i "s/MONGO_CMDB_PASSWORD/${MONGO_CMDB_PASSWORD}/g" ${INSTALL_PATH}/init/mongodb-init/mongodb_init.js
    sed -i "s/MONGO_JOB_PASSWORD/${MONGO_JOB_PASSWORD}/g" ${INSTALL_PATH}/init/mongodb-init/mongodb_init.js
    sed -i "s/MONGO_DEVOPS_PASSWORD/${MONGO_DEVOPS_PASSWORD}/g" ${INSTALL_PATH}/init/mongodb-init/mongodb_init.js
    sed -i "s/MONGO_CMP_PASSWORD/${MONGO_CMP_PASSWORD}/g" ${INSTALL_PATH}/init/mongodb-init/mongodb_init.js
    sed -i "s/MONGO_MONITOR_PASSWORD/${MONGO_MONITOR_PASSWORD}/g" ${INSTALL_PATH}/init/mongodb-init/mongodb_init.js
    sed -i "s/MONGO_AUTO_PASSWORD/${MONGO_AUTO_PASSWORD}/g" ${INSTALL_PATH}/init/mongodb-init/mongodb_init.js
    sed -i "s/MONGO_EVENT_PASSWORD/${MONGO_EVENT_PASSWORD}/g" ${INSTALL_PATH}/init/mongodb-init/mongodb_init.js
    sed -i "s/MONGO_PROM_PASSWORD/${MONGO_PROM_PASSWORD}/g" ${INSTALL_PATH}/init/mongodb-init/mongodb_init.js
    sed -i "s/MONGO_KBASE_PASSWORD/${MONGO_KBASE_PASSWORD}/g" ${INSTALL_PATH}/init/mongodb-init/mongodb_init.js

    docker cp ${INSTALL_PATH}/init/mongodb-init/mongodb_init.js opsany-base-mongodb:/opt/
    docker exec -e MONGO_INITDB_ROOT_USERNAME=$MONGO_INITDB_ROOT_USERNAME \
                -e MONGO_INITDB_ROOT_PASSWORD=$MONGO_INITDB_ROOT_PASSWORD \
                opsany-base-mongodb /bin/bash -c "/usr/bin/mongo -u $MONGO_INITDB_ROOT_USERNAME -p $MONGO_INITDB_ROOT_PASSWORD /opt/mongodb_init.js" >> ${SHELL_LOG} 2>&1
    shell_log "======MongoDB: MongoDB Initialize End======"
}

# SaaS Deploy

saas_rbac_deploy(){
    shell_log "======RBAC: Start RBAC======"
    cd ${CDIR}
    # Database 
    export MYSQL_PWD=${MYSQL_ROOT_PASSWORD}
    mysql -h "${MYSQL_SERVER_IP}" -P ${MYSQL_SERVER_PORT} -u root -e "create database rbac DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;"
    mysql -h "${MYSQL_SERVER_IP}" -P ${MYSQL_SERVER_PORT} -u root -e "CREATE USER 'rbac'@'%' identified by "\"${MYSQL_OPSANY_RBAC_PASSWORD}\"";"
    mysql -h "${MYSQL_SERVER_IP}" -P ${MYSQL_SERVER_PORT} -u root -e "grant all on rbac.* to rbac@'%';"

    # Register rbac
    RBAC_SECRET_KEY=$(cat ${INSTALL_PATH}/conf/.rbac_secret_key)
    docker exec opsany-paas-websocket /bin/sh -c "python3 /opt/opsany/saas/register_online_saas.py --paas_domain https://${DOMAIN_NAME} --username admin --password ${ADMIN_PASSWORD} --saas_app_code rbac --saas_app_name 统一权限 --saas_app_version ${SAAS_VERSION} --saas_app_secret_key ${RBAC_SECRET_KEY}"

    #python3 ../saas/register_online_saas.py --paas_domain https://${DOMAIN_NAME} --username admin --password ${ADMIN_PASSWORD} --saas_app_code rbac --saas_app_name 统一权限 --saas_app_version ${SAAS_VERSION} --saas_app_secret_key ${RBAC_SECRET_KEY}

    # Modify configuration
    sed -i "s/DOMAIN_NAME/${DOMAIN_NAME}/g" ${INSTALL_PATH}/conf/opsany-saas/rbac/rbac-init.py
    sed -i "s/RBAC_SECRET_KEY/${RBAC_SECRET_KEY}/g" ${INSTALL_PATH}/conf/opsany-saas/rbac/rbac-init.py
    sed -i "s/MYSQL_SERVER_IP/${MYSQL_SERVER_IP}/g" ${INSTALL_PATH}/conf/opsany-saas/rbac/rbac-prod.py
    sed -i "s/MYSQL_SERVER_PORT/${MYSQL_SERVER_PORT}/g" ${INSTALL_PATH}/conf/opsany-saas/rbac/rbac-prod.py
    sed -i "s/MYSQL_OPSANY_RBAC_PASSWORD/${MYSQL_OPSANY_RBAC_PASSWORD}/g" ${INSTALL_PATH}/conf/opsany-saas/rbac/rbac-prod.py
    sed -i "s/REDIS_SERVER_IP/${REDIS_SERVER_IP}/g" ${INSTALL_PATH}/conf/opsany-saas/rbac/rbac-prod.py
    sed -i "s/REDIS_SERVER_PORT/${REDIS_SERVER_PORT}/g" ${INSTALL_PATH}/conf/opsany-saas/rbac/rbac-prod.py
    sed -i "s/REDIS_SERVER_USER/${REDIS_SERVER_USER}/g" ${INSTALL_PATH}/conf/opsany-saas/rbac/rbac-prod.py
    sed -i "s/REDIS_SERVER_PASSWORD/${REDIS_SERVER_PASSWORD}/g" ${INSTALL_PATH}/conf/opsany-saas/rbac/rbac-prod.py

    # rbac ESB
    sed -i "s/DOMAIN_NAME/$DOMAIN_NAME/g" ${INSTALL_PATH}/esb/apis/rbac/toolkit/configs.py
    sed -i "s#/t/rbac#/o/rbac#g" ${INSTALL_PATH}/esb/apis/rbac/toolkit/configs.py

    # Starter container
    docker pull ${PAAS_DOCKER_REG}/opsany-saas-ce-rbac:${SAAS_VERSION}
    docker run -d --restart=always --name opsany-saas-ce-rbac \
       -p 7001:80 \
       -v ${INSTALL_PATH}/conf/opsany-saas/rbac/rbac-supervisor.ini:/etc/supervisord.d/rbac.ini \
       -v ${INSTALL_PATH}/conf/opsany-saas/rbac/rbac-uwsgi.ini:/opt/opsany/uwsgi/rbac.ini \
       -v ${INSTALL_PATH}/conf/opsany-saas/rbac/rbac-init.py:/opt/opsany/rbac/config/__init__.py \
       -v ${INSTALL_PATH}/conf/opsany-saas/rbac/rbac-prod.py:/opt/opsany/rbac/config/prod.py \
       -v ${INSTALL_PATH}/conf/opsany-saas/rbac/rbac-nginx.conf:/etc/nginx/http.d/default.conf \
       -v ${INSTALL_PATH}/logs/rbac:/opt/opsany/logs/rbac \
       -v ${INSTALL_PATH}/uploads:/opt/opsany/uploads \
       -v /etc/localtime:/etc/localtime:ro \
       ${PAAS_DOCKER_REG}/opsany-saas-ce-rbac:${SAAS_VERSION}
    
    # Django migrate
    docker exec -e BK_ENV="production" opsany-saas-ce-rbac /bin/sh -c \
    "python /opt/opsany/rbac/manage.py migrate --noinput && python /opt/opsany/rbac/manage.py createcachetable django_cache > /dev/null" >> ${SHELL_LOG}
}

saas_workbench_deploy(){
    shell_log "======Workbench: Start workbench======"
    cd ${CDIR}
    #workbench
    export MYSQL_PWD=${MYSQL_ROOT_PASSWORD}
    mysql -h "${MYSQL_SERVER_IP}" -P ${MYSQL_SERVER_PORT} -u root -e "create database workbench DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;"
    mysql -h "${MYSQL_SERVER_IP}" -P ${MYSQL_SERVER_PORT} -u root -e "CREATE USER 'workbench'@'%' IDENTIFIED BY "\"${MYSQL_OPSANY_WORKBENCH_PASSWORD}\"";"
    mysql -h "${MYSQL_SERVER_IP}" -P ${MYSQL_SERVER_PORT} -u root -e "grant all on workbench.* to workbench@'%';"

    # Register workbench
    if [ -f ${INSTALL_PATH}/conf/.workbench_secret_key ];then
        WORKBENCH_SECRET_KEY=$(cat ${INSTALL_PATH}/conf/.workbench_secret_key)
    else
        WORKBENCH_SECRET_KEY=$(uuid -v4)
        echo $WORKBENCH_SECRET_KEY > ${INSTALL_PATH}/conf/.workbench_secret_key
    fi
    docker exec opsany-paas-websocket /bin/sh -c "python3 /opt/opsany/saas/register_online_saas.py --paas_domain https://${DOMAIN_NAME} --username admin --password ${ADMIN_PASSWORD} --saas_app_code workbench --saas_app_name 工作台 --saas_app_version ${SAAS_VERSION} --saas_app_secret_key ${WORKBENCH_SECRET_KEY}"

    # Modify configuration
    WORKBENCH_SECRET_KEY=$(cat ${INSTALL_PATH}/conf/.workbench_secret_key)
    sed -i "s/DOMAIN_NAME/${DOMAIN_NAME}/g" ${INSTALL_PATH}/conf/opsany-saas/workbench/workbench-init.py
    sed -i "s/WORKBENCH_SECRET_KEY/${WORKBENCH_SECRET_KEY}/g" ${INSTALL_PATH}/conf/opsany-saas/workbench/workbench-init.py
    sed -i "s/MYSQL_SERVER_IP/${MYSQL_SERVER_IP}/g" ${INSTALL_PATH}/conf/opsany-saas/workbench/workbench-prod.py
    sed -i "s/MYSQL_SERVER_PORT/${MYSQL_SERVER_PORT}/g" ${INSTALL_PATH}/conf/opsany-saas/workbench/workbench-prod.py
    sed -i "s/MYSQL_OPSANY_WORKBENCH_PASSWORD/${MYSQL_OPSANY_WORKBENCH_PASSWORD}/g" ${INSTALL_PATH}/conf/opsany-saas/workbench/workbench-prod.py
    sed -i "s/MONGO_SERVER_IP/${MONGO_SERVER_IP}/g" ${INSTALL_PATH}/conf/opsany-saas/workbench/workbench-prod.py
    sed -i "s/MONGO_SERVER_PORT/${MONGO_SERVER_PORT}/g" ${INSTALL_PATH}/conf/opsany-saas/workbench/workbench-prod.py
    sed -i "s/MONGO_WORKBENCH_PASSWORD/${MONGO_WORKBENCH_PASSWORD}/g" ${INSTALL_PATH}/conf/opsany-saas/workbench/workbench-prod.py
    sed -i "s/REDIS_SERVER_IP/${REDIS_SERVER_IP}/g" ${INSTALL_PATH}/conf/opsany-saas/workbench/workbench-prod.py
    sed -i "s/REDIS_SERVER_PORT/${REDIS_SERVER_PORT}/g" ${INSTALL_PATH}/conf/opsany-saas/workbench/workbench-prod.py
    sed -i "s/REDIS_SERVER_USER/${REDIS_SERVER_USER}/g" ${INSTALL_PATH}/conf/opsany-saas/workbench/workbench-prod.py
    sed -i "s/REDIS_SERVER_PASSWORD/${REDIS_SERVER_PASSWORD}/g" ${INSTALL_PATH}/conf/opsany-saas/workbench/workbench-prod.py

    #workbench
    sed -i "s/DOMAIN_NAME/$DOMAIN_NAME/g" ${INSTALL_PATH}/esb/apis/workbench/toolkit/configs.py
    sed -i "s#/t/workbench#/o/workbench#g" ${INSTALL_PATH}/esb/apis/workbench/toolkit/tools.py

    # Starter container
    docker pull ${PAAS_DOCKER_REG}/opsany-saas-ce-workbench:${SAAS_VERSION}
    docker run -d --restart=always --name opsany-saas-ce-workbench \
       -p 7002:80 \
       -v ${INSTALL_PATH}/conf/opsany-saas/workbench/workbench-supervisor.ini:/etc/supervisord.d/workbench.ini \
       -v ${INSTALL_PATH}/conf/opsany-saas/workbench/workbench-uwsgi.ini:/opt/opsany/uwsgi/workbench.ini \
       -v ${INSTALL_PATH}/conf/opsany-saas/workbench/workbench-init.py:/opt/opsany/workbench/config/__init__.py \
       -v ${INSTALL_PATH}/conf/opsany-saas/workbench/workbench-prod.py:/opt/opsany/workbench/config/prod.py \
       -v ${INSTALL_PATH}/conf/opsany-saas/workbench/workbench-nginx.conf:/etc/nginx/http.d/default.conf \
       -v ${INSTALL_PATH}/logs/workbench:/opt/opsany/logs/workbench \
       -v ${INSTALL_PATH}/uploads:/opt/opsany/uploads \
       -v /etc/localtime:/etc/localtime:ro \
       ${PAAS_DOCKER_REG}/opsany-saas-ce-workbench:${SAAS_VERSION}
    # Django migrate
    docker exec -e BK_ENV="production" opsany-saas-ce-workbench /bin/sh -c \
    "python /opt/opsany/workbench/manage.py migrate --noinput && python /opt/opsany/workbench/manage.py createcachetable django_cache > /dev/null" >> ${SHELL_LOG}
}

saas_cmdb_deploy(){
    shell_log "======CMDB: Start cmdb======"
    cd ${CDIR}
    #cmdb
    export MYSQL_PWD=${MYSQL_ROOT_PASSWORD}
    mysql -h "${MYSQL_SERVER_IP}" -P ${MYSQL_SERVER_PORT} -u root -e "create database cmdb DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;"
    mysql -h "${MYSQL_SERVER_IP}" -P ${MYSQL_SERVER_PORT} -u root -e "CREATE USER 'cmdb'@'%' IDENTIFIED BY "\"${MYSQL_OPSANY_CMDB_PASSWORD}\"";"
    mysql -h "${MYSQL_SERVER_IP}" -P ${MYSQL_SERVER_PORT} -u root -e "grant all on cmdb.* to cmdb@'%';"

    # Register cmdb
    if [ -f ${INSTALL_PATH}/conf/.cmdb_secret_key ];then
        CMDB_SECRET_KEY=$(cat ${INSTALL_PATH}/conf/.cmdb_secret_key)
    else
        CMDB_SECRET_KEY=$(uuid -v4)
        echo $CMDB_SECRET_KEY > ${INSTALL_PATH}/conf/.cmdb_secret_key
    fi
    docker exec opsany-paas-websocket /bin/sh -c "python3 /opt/opsany/saas/register_online_saas.py --paas_domain https://${DOMAIN_NAME} --username admin --password ${ADMIN_PASSWORD} --saas_app_code cmdb --saas_app_name 资源平台 --saas_app_version ${SAAS_VERSION} --saas_app_secret_key ${CMDB_SECRET_KEY}"

    # Modify configuration
    CMDB_SECRET_KEY=$(cat ${INSTALL_PATH}/conf/.cmdb_secret_key)
    sed -i "s/DOMAIN_NAME/${DOMAIN_NAME}/g" ${INSTALL_PATH}/conf/opsany-saas/cmdb/cmdb-init.py
    sed -i "s/CMDB_SECRET_KEY/${CMDB_SECRET_KEY}/g" ${INSTALL_PATH}/conf/opsany-saas/cmdb/cmdb-init.py
    sed -i "s/MYSQL_SERVER_IP/${MYSQL_SERVER_IP}/g" ${INSTALL_PATH}/conf/opsany-saas/cmdb/cmdb-prod.py
    sed -i "s/MYSQL_SERVER_PORT/${MYSQL_SERVER_PORT}/g" ${INSTALL_PATH}/conf/opsany-saas/cmdb/cmdb-prod.py
    sed -i "s/MYSQL_OPSANY_CMDB_PASSWORD/${MYSQL_OPSANY_CMDB_PASSWORD}/g" ${INSTALL_PATH}/conf/opsany-saas/cmdb/cmdb-prod.py
    sed -i "s/MONGO_SERVER_IP/${MONGO_SERVER_IP}/g" ${INSTALL_PATH}/conf/opsany-saas/cmdb/cmdb-prod.py
    sed -i "s/MONGO_SERVER_PORT/${MONGO_SERVER_PORT}/g" ${INSTALL_PATH}/conf/opsany-saas/cmdb/cmdb-prod.py
    sed -i "s/MONGO_CMDB_PASSWORD/${MONGO_CMDB_PASSWORD}/g" ${INSTALL_PATH}/conf/opsany-saas/cmdb/cmdb-prod.py
    sed -i "s/REDIS_SERVER_IP/${REDIS_SERVER_IP}/g" ${INSTALL_PATH}/conf/opsany-saas/cmdb/cmdb-prod.py
    sed -i "s/REDIS_SERVER_PORT/${REDIS_SERVER_PORT}/g" ${INSTALL_PATH}/conf/opsany-saas/cmdb/cmdb-prod.py
    sed -i "s/REDIS_SERVER_USER/${REDIS_SERVER_USER}/g" ${INSTALL_PATH}/conf/opsany-saas/cmdb/cmdb-prod.py
    sed -i "s/REDIS_SERVER_PASSWORD/${REDIS_SERVER_PASSWORD}/g" ${INSTALL_PATH}/conf/opsany-saas/cmdb/cmdb-prod.py
    
    
    #cmdb
    sed -i "s/DOMAIN_NAME/$DOMAIN_NAME/g" ${INSTALL_PATH}/esb/apis/cmdb/toolkit/configs.py
    sed -i "s#/t/cmdb#/o/cmdb#g" ${INSTALL_PATH}/esb/apis/cmdb/toolkit/tools.py

    # Starter container
    docker pull ${PAAS_DOCKER_REG}/opsany-saas-ce-cmdb:${SAAS_VERSION}
    docker run -d --restart=always --name opsany-saas-ce-cmdb \
       -p 7003:80 \
       -v ${INSTALL_PATH}/conf/opsany-saas/cmdb/cmdb-supervisor.ini:/etc/supervisord.d/cmdb.ini \
       -v ${INSTALL_PATH}/conf/opsany-saas/cmdb/cmdb-uwsgi.ini:/opt/opsany/uwsgi/cmdb.ini \
       -v ${INSTALL_PATH}/conf/opsany-saas/cmdb/cmdb-init.py:/opt/opsany/cmdb/config/__init__.py \
       -v ${INSTALL_PATH}/conf/opsany-saas/cmdb/cmdb-prod.py:/opt/opsany/cmdb/config/prod.py \
       -v ${INSTALL_PATH}/conf/opsany-saas/cmdb/cmdb-nginx.conf:/etc/nginx/http.d/default.conf \
       -v ${INSTALL_PATH}/logs/cmdb:/opt/opsany/logs/cmdb \
       -v ${INSTALL_PATH}/uploads:/opt/opsany/uploads \
       -v /etc/localtime:/etc/localtime:ro \
       ${PAAS_DOCKER_REG}/opsany-saas-ce-cmdb:${SAAS_VERSION}
    
    # Django migrate
    docker exec -e BK_ENV="production" opsany-saas-ce-cmdb /bin/sh -c \
    "python /opt/opsany/cmdb/manage.py migrate --noinput && python /opt/opsany/cmdb/manage.py createcachetable django_cache > /dev/null" >> ${SHELL_LOG}
}

saas_control_deploy(){
    shell_log "======Control: Start control======"
    cd ${CDIR}
    #control
    export MYSQL_PWD=${MYSQL_ROOT_PASSWORD}
    mysql -h "${MYSQL_SERVER_IP}" -P ${MYSQL_SERVER_PORT} -u root -e "create database control DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;"
    mysql -h "${MYSQL_SERVER_IP}" -P ${MYSQL_SERVER_PORT} -u root -e "CREATE USER 'control'@'%' identified by "\"${MYSQL_OPSANY_CONTROL_PASSWORD}\"";"
    mysql -h "${MYSQL_SERVER_IP}" -P ${MYSQL_SERVER_PORT} -u root -e "grant all on control.* to control@'%';"
    
    # Register control
    if [ -f ${INSTALL_PATH}/conf/.control_secret_key ];then
        CONTROL_SECRET_KEY=$(cat ${INSTALL_PATH}/conf/.control_secret_key)
    else
        CONTROL_SECRET_KEY=$(uuid -v4)
        echo $CONTROL_SECRET_KEY > ${INSTALL_PATH}/conf/.control_secret_key
    fi 
    docker exec opsany-paas-websocket /bin/sh -c "python3 /opt/opsany/saas/register_online_saas.py --paas_domain https://${DOMAIN_NAME} --username admin --password ${ADMIN_PASSWORD} --saas_app_code control --saas_app_name 管控平台 --saas_app_version ${SAAS_VERSION} --saas_app_secret_key ${CONTROL_SECRET_KEY}"

    # Modify configuration
    CONTROL_SECRET_KEY=$(cat ${INSTALL_PATH}/conf/.control_secret_key)
    sed -i "s/DOMAIN_NAME/${DOMAIN_NAME}/g" ${INSTALL_PATH}/conf/opsany-saas/control/control-init.py
    sed -i "s/CONTROL_SECRET_KEY/${CONTROL_SECRET_KEY}/g" ${INSTALL_PATH}/conf/opsany-saas/control/control-init.py
    sed -i "s/MYSQL_SERVER_IP/${MYSQL_SERVER_IP}/g" ${INSTALL_PATH}/conf/opsany-saas/control/control-prod.py
    sed -i "s/MYSQL_SERVER_PORT/${MYSQL_SERVER_PORT}/g" ${INSTALL_PATH}/conf/opsany-saas/control/control-prod.py
    sed -i "s/MYSQL_OPSANY_CONTROL_PASSWORD/${MYSQL_OPSANY_CONTROL_PASSWORD}/g" ${INSTALL_PATH}/conf/opsany-saas/control/control-prod.py
    sed -i "s/REDIS_SERVER_IP/${REDIS_SERVER_IP}/g" ${INSTALL_PATH}/conf/opsany-saas/control/control-prod.py
    sed -i "s/REDIS_SERVER_PORT/${REDIS_SERVER_PORT}/g" ${INSTALL_PATH}/conf/opsany-saas/control/control-prod.py
    sed -i "s/REDIS_SERVER_USER/${REDIS_SERVER_USER}/g" ${INSTALL_PATH}/conf/opsany-saas/control/control-prod.py
    sed -i "s/REDIS_SERVER_PASSWORD/${REDIS_SERVER_PASSWORD}/g" ${INSTALL_PATH}/conf/opsany-saas/control/control-prod.py

    #control
    sed -i "s/DOMAIN_NAME/$DOMAIN_NAME/g" ${INSTALL_PATH}/esb/apis/control/toolkit/configs.py
    sed -i "s#/t/control#/o/control#g" ${INSTALL_PATH}/esb/apis/control/toolkit/tools.py

    # Starter container
    docker pull ${PAAS_DOCKER_REG}/opsany-saas-ce-control:${SAAS_VERSION}
    docker run -d --restart=always --name opsany-saas-ce-control \
       -p 7004:80 \
       -v ${INSTALL_PATH}/conf/opsany-saas/control/control-supervisor.ini:/etc/supervisord.d/control.ini \
       -v ${INSTALL_PATH}/conf/opsany-saas/control/control-uwsgi.ini:/opt/opsany/uwsgi/control.ini \
       -v ${INSTALL_PATH}/conf/opsany-saas/control/control-init.py:/opt/opsany/control/config/__init__.py \
       -v ${INSTALL_PATH}/conf/opsany-saas/control/control-prod.py:/opt/opsany/control/config/prod.py \
       -v ${INSTALL_PATH}/conf/opsany-saas/control/control-nginx.conf:/etc/nginx/http.d/default.conf \
       -v ${INSTALL_PATH}/logs:/opt/opsany/logs \
       -v ${INSTALL_PATH}/uploads:/opt/opsany/uploads \
       -v /etc/localtime:/etc/localtime:ro \
       ${PAAS_DOCKER_REG}/opsany-saas-ce-control:${SAAS_VERSION}
    
    # Django migrate
    docker exec -e BK_ENV="production" opsany-saas-ce-control /bin/sh -c \
    "python /opt/opsany/control/manage.py migrate --noinput && python /opt/opsany/control/manage.py createcachetable django_cache > /dev/null" >> ${SHELL_LOG}
}

saas_job_deploy(){
    shell_log "======Job: Start job======"
    cd ${CDIR}
    #job
    export MYSQL_PWD=${MYSQL_ROOT_PASSWORD}
    mysql -h "${MYSQL_SERVER_IP}" -P ${MYSQL_SERVER_PORT} -u root -e "create database job DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;"
    mysql -h "${MYSQL_SERVER_IP}" -P ${MYSQL_SERVER_PORT} -u root -e "CREATE USER 'job'@'%' identified by "\"${MYSQL_OPSANY_JOB_PASSWORD}\"";"
    mysql -h "${MYSQL_SERVER_IP}" -P ${MYSQL_SERVER_PORT} -u root -e "grant all on job.* to job@'%';"

    # Register job
    if [ -f ${INSTALL_PATH}/conf/.job_secret_key ];then
        JOB_SECRET_KEY=$(cat ${INSTALL_PATH}/conf/.job_secret_key)
    else
        JOB_SECRET_KEY=$(uuid -v4)
        echo $JOB_SECRET_KEY > ${INSTALL_PATH}/conf/.job_secret_key
    fi 
    docker exec opsany-paas-websocket /bin/sh -c "python3 /opt/opsany/saas/register_online_saas.py --paas_domain https://${DOMAIN_NAME} --username admin --password ${ADMIN_PASSWORD} --saas_app_code job --saas_app_name 作业平台 --saas_app_version ${SAAS_VERSION} --saas_app_secret_key ${JOB_SECRET_KEY}"

    # Modify configuration
    JOB_SECRET_KEY=$(cat ${INSTALL_PATH}/conf/.job_secret_key)
    sed -i "s/DOMAIN_NAME/${DOMAIN_NAME}/g" ${INSTALL_PATH}/conf/opsany-saas/job/job-init.py
    sed -i "s/JOB_SECRET_KEY/${JOB_SECRET_KEY}/g" ${INSTALL_PATH}/conf/opsany-saas/job/job-init.py
    sed -i "s/MYSQL_SERVER_IP/${MYSQL_SERVER_IP}/g" ${INSTALL_PATH}/conf/opsany-saas/job/job-prod.py
    sed -i "s/MYSQL_SERVER_PORT/${MYSQL_SERVER_PORT}/g" ${INSTALL_PATH}/conf/opsany-saas/job/job-prod.py
    sed -i "s/MYSQL_OPSANY_JOB_PASSWORD/${MYSQL_OPSANY_JOB_PASSWORD}/g" ${INSTALL_PATH}/conf/opsany-saas/job/job-prod.py
    sed -i "s/MONGO_SERVER_IP/${MONGO_SERVER_IP}/g" ${INSTALL_PATH}/conf/opsany-saas/job/job-prod.py
    sed -i "s/MONGO_SERVER_PORT/${MONGO_SERVER_PORT}/g" ${INSTALL_PATH}/conf/opsany-saas/job/job-prod.py
    sed -i "s/MONGO_JOB_PASSWORD/${MONGO_JOB_PASSWORD}/g" ${INSTALL_PATH}/conf/opsany-saas/job/job-prod.py
    sed -i "s/REDIS_SERVER_IP/${REDIS_SERVER_IP}/g" ${INSTALL_PATH}/conf/opsany-saas/job/job-prod.py
    sed -i "s/REDIS_SERVER_PORT/${REDIS_SERVER_PORT}/g" ${INSTALL_PATH}/conf/opsany-saas/job/job-prod.py
    sed -i "s/REDIS_SERVER_USER/${REDIS_SERVER_USER}/g" ${INSTALL_PATH}/conf/opsany-saas/job/job-prod.py
    sed -i "s/REDIS_SERVER_PASSWORD/${REDIS_SERVER_PASSWORD}/g" ${INSTALL_PATH}/conf/opsany-saas/job/job-prod.py
    
    #job
    sed -i "s/DOMAIN_NAME/$DOMAIN_NAME/g" ${INSTALL_PATH}/esb/apis/task/toolkit/configs.py
    sed -i "s#/t/job#/o/job#g" ${INSTALL_PATH}/esb/apis/task/toolkit/tools.py
    sed -i "s/DOMAIN_NAME/$DOMAIN_NAME/g" ${INSTALL_PATH}/esb/apis/job/toolkit/configs.py
    sed -i "s#/t/job#/o/job#g" ${INSTALL_PATH}/esb/apis/job/toolkit/tools.py

    # Starter container
    docker pull ${PAAS_DOCKER_REG}/opsany-saas-ce-job:${SAAS_VERSION}
    docker run -d --restart=always --name opsany-saas-ce-job \
       -p 7005:80 \
       -v ${INSTALL_PATH}/conf/opsany-saas/job/job-supervisor.ini:/etc/supervisord.d/job.ini \
       -v ${INSTALL_PATH}/conf/opsany-saas/job/job-uwsgi.ini:/opt/opsany/uwsgi/job.ini \
       -v ${INSTALL_PATH}/conf/opsany-saas/job/job-init.py:/opt/opsany/job/config/__init__.py \
       -v ${INSTALL_PATH}/conf/opsany-saas/job/job-prod.py:/opt/opsany/job/config/prod.py \
       -v ${INSTALL_PATH}/conf/opsany-saas/job/job-nginx.conf:/etc/nginx/http.d/default.conf \
       -v ${INSTALL_PATH}/logs/job:/opt/opsany/logs/job \
       -v ${INSTALL_PATH}/uploads:/opt/opsany/uploads \
       -v /etc/localtime:/etc/localtime:ro \
       ${PAAS_DOCKER_REG}/opsany-saas-ce-job:${SAAS_VERSION}
    
    # Django migrate
    docker exec -e BK_ENV="production" opsany-saas-ce-job /bin/sh -c \
    "python /opt/opsany/job/manage.py migrate --noinput && python /opt/opsany/job/manage.py createcachetable django_cache > /dev/null" >> ${SHELL_LOG}
}

saas_monitor_deploy(){
    cd ${CDIR}
    # Grafana
    shell_log "======Grafana: Start Grafana======"
    docker run -d --restart=always --name opsany-base-grafana --user root \
    -v ${INSTALL_PATH}/conf/grafana/grafana.ini:/etc/grafana/grafana.ini \
    -v ${INSTALL_PATH}/conf/grafana/grafana.key:/etc/grafana/grafana.key \
    -v ${INSTALL_PATH}/conf/grafana/grafana.pem:/etc/grafana/grafana.pem \
    -v /etc/localtime:/etc/localtime:ro \
    -v ${INSTALL_PATH}/grafana-volume/data:/var/lib/grafana \
    -p 8007:3000 \
    ${PAAS_DOCKER_REG}/opsany-grafana:9.0.3

    shell_log "======Monitor: Start monitor======"
    #monitor
    export MYSQL_PWD=${MYSQL_ROOT_PASSWORD}
    mysql -h "${MYSQL_SERVER_IP}" -P ${MYSQL_SERVER_PORT} -u root -e "create database monitor DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;"
    mysql -h "${MYSQL_SERVER_IP}" -P ${MYSQL_SERVER_PORT} -u root -e "CREATE USER 'monitor'@'%' identified by "\"${MYSQL_OPSANY_MONITOR_PASSWORD}\"";"
    mysql -h "${MYSQL_SERVER_IP}" -P ${MYSQL_SERVER_PORT} -u root -e "grant all on monitor.* to monitor@'%';" 

    #monitor
    sed -i "s/DOMAIN_NAME/$DOMAIN_NAME/g" ${INSTALL_PATH}/esb/apis/monitor/toolkit/configs.py
    sed -i "s#/t/monitor#/o/monitor#g" ${INSTALL_PATH}/esb/apis/monitor/toolkit/tools.py
 
    # Register monitor
    if [ -f ${INSTALL_PATH}/conf/.passwd_env ];then
        source ${INSTALL_PATH}/conf/.passwd_env
    fi
    
    if [ -f ${INSTALL_PATH}/conf/.monitor_secret_key ];then
        MONITOR_SECRET_KEY=$(cat ${INSTALL_PATH}/conf/.monitor_secret_key)
    else
        MONITOR_SECRET_KEY=$(uuid -v4)
        echo $MONITOR_SECRET_KEY > ${INSTALL_PATH}/conf/.monitor_secret_key
    fi 

    # Modify configuration
    MONITOR_SECRET_KEY=$(cat ${INSTALL_PATH}/conf/.monitor_secret_key)
    sed -i "s/DOMAIN_NAME/${DOMAIN_NAME}/g" ${INSTALL_PATH}/conf/opsany-saas/monitor/monitor-init.py
    sed -i "s/MONITOR_SECRET_KEY/${MONITOR_SECRET_KEY}/g" ${INSTALL_PATH}/conf/opsany-saas/monitor/monitor-init.py
    sed -i "s/MYSQL_SERVER_IP/${MYSQL_SERVER_IP}/g" ${INSTALL_PATH}/conf/opsany-saas/monitor/monitor-prod.py
    sed -i "s/MYSQL_SERVER_PORT/${MYSQL_SERVER_PORT}/g" ${INSTALL_PATH}/conf/opsany-saas/monitor/monitor-prod.py
    sed -i "s/MYSQL_OPSANY_MONITOR_PASSWORD/${MYSQL_OPSANY_MONITOR_PASSWORD}/g" ${INSTALL_PATH}/conf/opsany-saas/monitor/monitor-prod.py
    sed -i "s/MONGO_SERVER_IP/${MONGO_SERVER_IP}/g" ${INSTALL_PATH}/conf/opsany-saas/monitor/monitor-prod.py
    sed -i "s/MONGO_SERVER_PORT/${MONGO_SERVER_PORT}/g" ${INSTALL_PATH}/conf/opsany-saas/monitor/monitor-prod.py
    sed -i "s/MONGO_MONITOR_PASSWORD/${MONGO_MONITOR_PASSWORD}/g" ${INSTALL_PATH}/conf/opsany-saas/monitor/monitor-prod.py
    sed -i "s/REDIS_SERVER_IP/${REDIS_SERVER_IP}/g" ${INSTALL_PATH}/conf/opsany-saas/monitor/monitor-prod.py
    sed -i "s/REDIS_SERVER_PORT/${REDIS_SERVER_PORT}/g" ${INSTALL_PATH}/conf/opsany-saas/monitor/monitor-prod.py
    sed -i "s/REDIS_SERVER_USER/${REDIS_SERVER_USER}/g" ${INSTALL_PATH}/conf/opsany-saas/monitor/monitor-prod.py
    sed -i "s/REDIS_SERVER_PASSWORD/${REDIS_SERVER_PASSWORD}/g" ${INSTALL_PATH}/conf/opsany-saas/monitor/monitor-prod.py
    
    # Starter container
    docker pull ${PAAS_DOCKER_REG}/opsany-saas-ce-monitor:${SAAS_VERSION}
    docker run -d --restart=always --name opsany-saas-ce-monitor \
       -p 7006:80 \
       -v ${INSTALL_PATH}/conf/opsany-saas/monitor/monitor-supervisor.ini:/etc/supervisord.d/monitor.ini \
       -v ${INSTALL_PATH}/conf/opsany-saas/monitor/monitor-uwsgi.ini:/opt/opsany/uwsgi/monitor.ini \
       -v ${INSTALL_PATH}/conf/opsany-saas/monitor/monitor-init.py:/opt/opsany/monitor/config/__init__.py \
       -v ${INSTALL_PATH}/conf/opsany-saas/monitor/monitor-prod.py:/opt/opsany/monitor/config/prod.py \
       -v ${INSTALL_PATH}/conf/opsany-saas/monitor/monitor-nginx.conf:/etc/nginx/http.d/default.conf \
       -v ${INSTALL_PATH}/logs/monitor:/opt/opsany/logs/monitor \
       -v ${INSTALL_PATH}/uploads:/opt/opsany/uploads \
       -v /etc/localtime:/etc/localtime:ro \
       ${PAAS_DOCKER_REG}/opsany-saas-ce-monitor:${SAAS_VERSION}
    
    # Django migrate
    docker exec -e BK_ENV="production" opsany-saas-ce-monitor /bin/sh -c \
    "python /opt/opsany/monitor/manage.py migrate --noinput && python /opt/opsany/monitor/manage.py createcachetable django_cache > /dev/null" >> ${SHELL_LOG}
    sleep 5
    docker exec opsany-paas-websocket /bin/sh -c "python3 /opt/opsany/saas/register_online_saas.py --paas_domain https://${DOMAIN_NAME} --username admin --password ${ADMIN_PASSWORD} --saas_app_code monitor --saas_app_name 基础监控 --saas_app_version ${SAAS_VERSION} --saas_app_secret_key ${MONITOR_SECRET_KEY}"
    docker exec opsany-paas-websocket /bin/sh -c "python3 /opt/opsany/saas/sync-user-script.py --domain https://${DOMAIN_NAME} --paas_username admin --paas_password ${ADMIN_PASSWORD} --app_code monitor"
    docker exec opsany-paas-websocket /bin/sh -c "python3 /opt/opsany/saas/init-ce-monitor.py --domain $DOMAIN_NAME --private_ip $LOCAL_IP --paas_username admin --paas_password ${ADMIN_PASSWORD} --grafana_password admin --grafana_change_password $GRAFANA_ADMIN_PASSWORD"

    # Install Grafana Zabbix Plugin
    ZABBIX_GRAFANE_PLUGIN_NAME="alexanderzobnin-zabbix-app-4.3.1.zip"
    if [ -f "${ZABBIX_GRAFANE_PLUGIN_NAME}" ]; then
        cd /tmp && unzip -q ${ZABBIX_GRAFANE_PLUGIN_NAME}
        docker cp /tmp/alexanderzobnin-zabbix-app opsany-base-grafana:/var/lib/grafana/plugins/
        docker restart opsany-base-grafana
    else
        cd /tmp && wget https://opsany.oss-cn-beijing.aliyuncs.com/${ZABBIX_GRAFANE_PLUGIN_NAME}
        unzip -q ${ZABBIX_GRAFANE_PLUGIN_NAME}
        docker cp /tmp/alexanderzobnin-zabbix-app opsany-base-grafana:/var/lib/grafana/plugins/
        docker restart opsany-base-grafana
    fi
}

saas_cmp_deploy(){
    shell_log "======CMP: Start cmp======"
    cd ${CDIR}
    #cmp
    export MYSQL_PWD=${MYSQL_ROOT_PASSWORD}
    mysql -h "${MYSQL_SERVER_IP}" -P ${MYSQL_SERVER_PORT} -u root -e "create database cmp DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;"
    mysql -h "${MYSQL_SERVER_IP}" -P ${MYSQL_SERVER_PORT} -u root -e "CREATE USER 'cmp'@'%' identified by "\"${MYSQL_OPSANY_CMP_PASSWORD}\"";"
    mysql -h "${MYSQL_SERVER_IP}" -P ${MYSQL_SERVER_PORT} -u root -e "grant all on cmp.* to cmp@'%';" 
    
    #cmp
    sed -i "s/DOMAIN_NAME/$DOMAIN_NAME/g" ${INSTALL_PATH}/esb/apis/cmp/toolkit/configs.py
    sed -i "s#/t/cmp#/o/cmp#g" ${INSTALL_PATH}/esb/apis/cmp/toolkit/tools.py

    # Register cmp
    if [ -f ${INSTALL_PATH}/conf/.cmp_secret_key ];then
        CMP_SECRET_KEY=$(cat ${INSTALL_PATH}/conf/.cmp_secret_key)
    else
        CMP_SECRET_KEY=$(uuid -v4)
        echo $CMP_SECRET_KEY > ${INSTALL_PATH}/conf/.cmp_secret_key
    fi 
    docker exec opsany-paas-websocket /bin/sh -c "python3 /opt/opsany/saas/register_online_saas.py --paas_domain https://${DOMAIN_NAME} --username admin --password ${ADMIN_PASSWORD} --saas_app_code cmp --saas_app_name 云管平台 --saas_app_version ${SAAS_VERSION} --saas_app_secret_key ${CMP_SECRET_KEY}"

    #CMP Configure
    CMP_SECRET_KEY=$(cat ${INSTALL_PATH}/conf/.cmp_secret_key)
    sed -i "s/DOMAIN_NAME/${DOMAIN_NAME}/g" ${INSTALL_PATH}/conf/opsany-saas/cmp/cmp-init.py
    sed -i "s/CMP_SECRET_KEY/${CMP_SECRET_KEY}/g" ${INSTALL_PATH}/conf/opsany-saas/cmp/cmp-init.py
    sed -i "s/MYSQL_SERVER_IP/${MYSQL_SERVER_IP}/g" ${INSTALL_PATH}/conf/opsany-saas/cmp/cmp-prod.py
    sed -i "s/MYSQL_SERVER_PORT/${MYSQL_SERVER_PORT}/g" ${INSTALL_PATH}/conf/opsany-saas/cmp/cmp-prod.py
    sed -i "s/MYSQL_OPSANY_CMP_PASSWORD/${MYSQL_OPSANY_CMP_PASSWORD}/g" ${INSTALL_PATH}/conf/opsany-saas/cmp/cmp-prod.py
    sed -i "s/MONGO_SERVER_IP/${MONGO_SERVER_IP}/g" ${INSTALL_PATH}/conf/opsany-saas/cmp/cmp-prod.py
    sed -i "s/MONGO_SERVER_PORT/${MONGO_SERVER_PORT}/g" ${INSTALL_PATH}/conf/opsany-saas/cmp/cmp-prod.py
    sed -i "s/MONGO_CMP_PASSWORD/${MONGO_CMP_PASSWORD}/g" ${INSTALL_PATH}/conf/opsany-saas/cmp/cmp-prod.py
    sed -i "s/REDIS_SERVER_IP/${REDIS_SERVER_IP}/g" ${INSTALL_PATH}/conf/opsany-saas/cmp/cmp-prod.py
    sed -i "s/REDIS_SERVER_PORT/${REDIS_SERVER_PORT}/g" ${INSTALL_PATH}/conf/opsany-saas/cmp/cmp-prod.py
    sed -i "s/REDIS_SERVER_USER/${REDIS_SERVER_USER}/g" ${INSTALL_PATH}/conf/opsany-saas/cmp/cmp-prod.py
    sed -i "s/REDIS_SERVER_PASSWORD/${REDIS_SERVER_PASSWORD}/g" ${INSTALL_PATH}/conf/opsany-saas/cmp/cmp-prod.py
    
    # Starter container
    docker pull ${PAAS_DOCKER_REG}/opsany-saas-ce-cmp:${SAAS_VERSION}
    docker run -d --restart=always --name opsany-saas-ce-cmp \
       -p 7007:80 \
       -v ${INSTALL_PATH}/conf/opsany-saas/cmp/cmp-supervisor.ini:/etc/supervisord.d/cmp.ini \
       -v ${INSTALL_PATH}/conf/opsany-saas/cmp/cmp-uwsgi.ini:/opt/opsany/uwsgi/cmp.ini \
       -v ${INSTALL_PATH}/conf/opsany-saas/cmp/cmp-init.py:/opt/opsany/cmp/config/__init__.py \
       -v ${INSTALL_PATH}/conf/opsany-saas/cmp/cmp-prod.py:/opt/opsany/cmp/config/prod.py \
       -v ${INSTALL_PATH}/conf/opsany-saas/cmp/cmp-nginx.conf:/etc/nginx/http.d/default.conf \
       -v ${INSTALL_PATH}/logs/cmp:/opt/opsany/logs/cmp \
       -v ${INSTALL_PATH}/uploads:/opt/opsany/uploads \
       -v /etc/localtime:/etc/localtime:ro \
       ${PAAS_DOCKER_REG}/opsany-saas-ce-cmp:${SAAS_VERSION}
    
    # Django migrate
    docker exec -e BK_ENV="production" opsany-saas-ce-cmp /bin/sh -c \
    "python /opt/opsany/cmp/manage.py migrate --noinput && python /opt/opsany/cmp/manage.py createcachetable django_cache > /dev/null" >> ${SHELL_LOG}
}

saas_bastion_deploy(){
    shell_log "======Bastion: Start bastion======"
    cd ${CDIR}
    #bastion
    export MYSQL_PWD=${MYSQL_ROOT_PASSWORD}
    mysql -h "${MYSQL_SERVER_IP}" -P ${MYSQL_SERVER_PORT} -u root -e "create database bastion DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;"
    mysql -h "${MYSQL_SERVER_IP}" -P ${MYSQL_SERVER_PORT} -u root -e "CREATE USER 'bastion'@'%' identified by "\"${MYSQL_OPSANY_BASTION_PASSWORD}\"";"
    mysql -h "${MYSQL_SERVER_IP}" -P ${MYSQL_SERVER_PORT} -u root -e "grant all on bastion.* to bastion@'%';" 

    #bastion
    sed -i "s/DOMAIN_NAME/$DOMAIN_NAME/g" ${INSTALL_PATH}/esb/apis/bastion/toolkit/configs.py
    sed -i "s#/t/bastion#/o/bastion#g" ${INSTALL_PATH}/esb/apis/bastion/toolkit/configs.py

    # Register bastion
    if [ -f ${INSTALL_PATH}/conf/.bastion_secret_key ];then
        BASTION_SECRET_KEY=$(cat ${INSTALL_PATH}/conf/.bastion_secret_key)
    else
        BASTION_SECRET_KEY=$(uuid -v4)
        echo $BASTION_SECRET_KEY > ${INSTALL_PATH}/conf/.bastion_secret_key
    fi 
    docker exec opsany-paas-websocket /bin/sh -c "python3 /opt/opsany/saas/register_online_saas.py --paas_domain https://${DOMAIN_NAME} --username admin --password ${ADMIN_PASSWORD} --saas_app_code bastion --saas_app_name 堡垒机 --saas_app_version ${SAAS_VERSION} --saas_app_secret_key ${BASTION_SECRET_KEY}"

    # Bastion Configure
    sed -i "s/DOMAIN_NAME/${DOMAIN_NAME}/g" ${INSTALL_PATH}/conf/opsany-saas/bastion/bastion-init.py
    sed -i "s/BASTION_SECRET_KEY/${BASTION_SECRET_KEY}/g" ${INSTALL_PATH}/conf/opsany-saas/bastion/bastion-init.py
    sed -i "s/MYSQL_SERVER_IP/${MYSQL_SERVER_IP}/g" ${INSTALL_PATH}/conf/opsany-saas/bastion/bastion-prod.py
    sed -i "s/MYSQL_SERVER_PORT/${MYSQL_SERVER_PORT}/g" ${INSTALL_PATH}/conf/opsany-saas/bastion/bastion-prod.py
    sed -i "s/MYSQL_OPSANY_BASTION_PASSWORD/${MYSQL_OPSANY_BASTION_PASSWORD}/g" ${INSTALL_PATH}/conf/opsany-saas/bastion/bastion-prod.py
    sed -i "s/REDIS_SERVER_IP/${REDIS_SERVER_IP}/g" ${INSTALL_PATH}/conf/opsany-saas/bastion/bastion-prod.py
    sed -i "s/REDIS_SERVER_PORT/${REDIS_SERVER_PORT}/g" ${INSTALL_PATH}/conf/opsany-saas/bastion/bastion-prod.py
    sed -i "s/REDIS_SERVER_USER/${REDIS_SERVER_USER}/g" ${INSTALL_PATH}/conf/opsany-saas/bastion/bastion-prod.py
    sed -i "s/REDIS_SERVER_PASSWORD/${REDIS_SERVER_PASSWORD}/g" ${INSTALL_PATH}/conf/opsany-saas/bastion/bastion-prod.py
    
    # Starter container
    docker pull ${PAAS_DOCKER_REG}/opsany-saas-ce-bastion:${SAAS_VERSION}
    docker run -d --restart=always --name opsany-saas-ce-bastion \
       -p 7008:80 \
       -v ${INSTALL_PATH}/conf/opsany-saas/bastion/bastion-supervisor.ini:/etc/supervisord.d/bastion.ini \
       -v ${INSTALL_PATH}/conf/opsany-saas/bastion/bastion-uwsgi.ini:/opt/opsany/uwsgi/bastion.ini \
       -v ${INSTALL_PATH}/conf/opsany-saas/bastion/bastion-init.py:/opt/opsany/bastion/config/__init__.py \
       -v ${INSTALL_PATH}/conf/opsany-saas/bastion/bastion-prod.py:/opt/opsany/bastion/config/prod.py \
       -v ${INSTALL_PATH}/conf/opsany-saas/bastion/bastion-nginx.conf:/etc/nginx/http.d/default.conf \
       -v ${INSTALL_PATH}/logs:/opt/opsany/logs \
       -v ${INSTALL_PATH}/uploads:/opt/opsany/uploads \
       -v /etc/localtime:/etc/localtime:ro \
       ${PAAS_DOCKER_REG}/opsany-saas-ce-bastion:${SAAS_VERSION}
    
    # Django migrate
    docker exec -e BK_ENV="production" opsany-saas-ce-bastion /bin/sh -c \
    "python /opt/opsany/bastion/manage.py migrate --noinput && python /opt/opsany/bastion/manage.py createcachetable django_cache > /dev/null" >> ${SHELL_LOG}
}

saas_devops_deploy(){
    shell_log "======DevOps: Start devops======"
    cd ${CDIR}
    #DevOps MySQL
    export MYSQL_PWD=${MYSQL_ROOT_PASSWORD}
    mysql -h "${MYSQL_SERVER_IP}" -P ${MYSQL_SERVER_PORT} -u root -e "create database devops DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;"
    mysql -h "${MYSQL_SERVER_IP}" -P ${MYSQL_SERVER_PORT} -u root -e "CREATE USER 'devops'@'%' identified by "\"${MYSQL_OPSANY_DEVOPS_PASSWORD}\"";"
    mysql -h "${MYSQL_SERVER_IP}" -P ${MYSQL_SERVER_PORT} -u root -e "grant all on devops.* to devops@'%';" 
    
    #devops
    sed -i "s/DOMAIN_NAME/$DOMAIN_NAME/g" ${INSTALL_PATH}/esb/apis/devops/toolkit/configs.py
    sed -i "s#/t/devops#/o/devops#g" ${INSTALL_PATH}/esb/apis/devops/toolkit/tools.py

    # Register devops
    if [ -f ${INSTALL_PATH}/conf/.passwd_env ];then
        source ${INSTALL_PATH}/conf/.passwd_env
    fi
    if [ -f ${INSTALL_PATH}/conf/.devops_secret_key ];then
        DEVOPS_SECRET_KEY=$(cat ${INSTALL_PATH}/conf/.devops_secret_key)
    else
        DEVOPS_SECRET_KEY=$(uuid -v4)
        echo $DEVOPS_SECRET_KEY > ${INSTALL_PATH}/conf/.devops_secret_key
    fi
    docker exec opsany-paas-websocket /bin/sh -c "python3 /opt/opsany/saas/register_online_saas.py --paas_domain https://${DOMAIN_NAME} --username admin --password ${ADMIN_PASSWORD} --saas_app_code devops --saas_app_name 应用平台 --saas_app_version ${SAAS_VERSION} --saas_app_secret_key ${DEVOPS_SECRET_KEY}"

    # DevOps Configure
    DEVOPS_SECRET_KEY=$(cat ${INSTALL_PATH}/conf/.devops_secret_key)
    /bin/cp conf/opsany-saas/devops/* ${INSTALL_PATH}/conf/opsany-saas/devops/
    sed -i "s/DOMAIN_NAME/${DOMAIN_NAME}/g" ${INSTALL_PATH}/conf/opsany-saas/devops/devops-init.py
    sed -i "s/DEVOPS_SECRET_KEY/${DEVOPS_SECRET_KEY}/g" ${INSTALL_PATH}/conf/opsany-saas/devops/devops-init.py
    sed -i "s/MYSQL_SERVER_IP/${MYSQL_SERVER_IP}/g" ${INSTALL_PATH}/conf/opsany-saas/devops/devops-prod.py
    sed -i "s/MYSQL_SERVER_PORT/${MYSQL_SERVER_PORT}/g" ${INSTALL_PATH}/conf/opsany-saas/devops/devops-prod.py
    sed -i "s/MYSQL_OPSANY_DEVOPS_PASSWORD/${MYSQL_OPSANY_DEVOPS_PASSWORD}/g" ${INSTALL_PATH}/conf/opsany-saas/devops/devops-prod.py
    sed -i "s/MONGO_SERVER_IP/${MONGO_SERVER_IP}/g" ${INSTALL_PATH}/conf/opsany-saas/devops/devops-prod.py
    sed -i "s/MONGO_SERVER_PORT/${MONGO_SERVER_PORT}/g" ${INSTALL_PATH}/conf/opsany-saas/devops/devops-prod.py
    sed -i "s/MONGO_DEVOPS_PASSWORD/${MONGO_DEVOPS_PASSWORD}/g" ${INSTALL_PATH}/conf/opsany-saas/devops/devops-prod.py
    sed -i "s/REDIS_SERVER_IP/${REDIS_SERVER_IP}/g" ${INSTALL_PATH}/conf/opsany-saas/devops/devops-prod.py
    sed -i "s/REDIS_SERVER_PORT/${REDIS_SERVER_PORT}/g" ${INSTALL_PATH}/conf/opsany-saas/devops/devops-prod.py
    sed -i "s/REDIS_SERVER_USER/${REDIS_SERVER_USER}/g" ${INSTALL_PATH}/conf/opsany-saas/devops/devops-prod.py
    sed -i "s/REDIS_SERVER_PASSWORD/${REDIS_SERVER_PASSWORD}/g" ${INSTALL_PATH}/conf/opsany-saas/devops/devops-prod.py
    
    # Starter container   
    docker pull ${PAAS_DOCKER_REG}/opsany-saas-ce-devops:${SAAS_VERSION}
    docker run -d --restart=always --name opsany-saas-ce-devops \
       -p 7009:80 \
       -v ${INSTALL_PATH}/conf/opsany-saas/devops/devops-supervisor.ini:/etc/supervisord.d/devops.ini \
       -v ${INSTALL_PATH}/conf/opsany-saas/devops/devops-uwsgi.ini:/opt/opsany/uwsgi/devops.ini \
       -v ${INSTALL_PATH}/conf/opsany-saas/devops/devops-init.py:/opt/opsany/devops/config/__init__.py \
       -v ${INSTALL_PATH}/conf/opsany-saas/devops/devops-prod.py:/opt/opsany/devops/config/prod.py \
       -v ${INSTALL_PATH}/conf/opsany-saas/devops/devops-nginx.conf:/etc/nginx/http.d/default.conf \
       -v ${INSTALL_PATH}/logs:/opt/opsany/logs \
       -v ${INSTALL_PATH}/uploads:/opt/opsany/uploads \
       -v /etc/localtime:/etc/localtime:ro \
       ${PAAS_DOCKER_REG}/opsany-saas-ce-devops:${SAAS_VERSION}
    
    docker exec opsany-paas-websocket /bin/sh -c "python3 /opt/opsany/saas/sync-user-script.py --domain https://${DOMAIN_NAME} --paas_username admin --paas_password ${ADMIN_PASSWORD} --app_code cmdb"
        # Django migrate
    docker exec -e BK_ENV="production" opsany-saas-ce-devops /bin/sh -c \
    "python /opt/opsany/devops/manage.py migrate --noinput && python /opt/opsany/devops/manage.py createcachetable django_cache > /dev/null" >> ${SHELL_LOG}
    sleep 5
    docker exec opsany-paas-websocket /bin/sh -c "python3 /opt/opsany/saas/sync-user-script.py --domain https://${DOMAIN_NAME} --paas_username admin --paas_password ${ADMIN_PASSWORD} --app_code devops"
    docker exec opsany-paas-websocket /bin/sh -c "python3 /opt/opsany/saas/init-ce-devops.py --domain https://${DOMAIN_NAME} --username admin  --password $ADMIN_PASSWORD"
    docker exec opsany-paas-websocket /bin/sh -c "python3 /opt/opsany/saas/init_cmdb_app_to_devops.py --domain https://${DOMAIN_NAME} --paas_username admin --paas_password ${ADMIN_PASSWORD}"
}

saas_repo_deploy(){
    shell_log "======REPO: Start repo======"
    cd ${CDIR}
    #repo mysql
    export MYSQL_PWD=${MYSQL_ROOT_PASSWORD}
    mysql -h "${MYSQL_SERVER_IP}" -P ${MYSQL_SERVER_PORT} -u root -e "create database repo DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;"
    mysql -h "${MYSQL_SERVER_IP}" -P ${MYSQL_SERVER_PORT} -u root -e "CREATE USER 'repo'@'%' identified by "\"${MYSQL_OPSANY_REPO_PASSWORD}\"";"
    mysql -h "${MYSQL_SERVER_IP}" -P ${MYSQL_SERVER_PORT} -u root -e "grant all on repo.* to repo@'%';" 

    #repo esb
    sed -i "s/DOMAIN_NAME/$DOMAIN_NAME/g" ${INSTALL_PATH}/esb/apis/repo/toolkit/configs.py
    sed -i "s#/t/repo#/o/repo#g" ${INSTALL_PATH}/esb/apis/repo/toolkit/configs.py

    # Register repo
    if [ -f ${INSTALL_PATH}/conf/.repo_secret_key ];then
        REPO_SECRET_KEY=$(cat ${INSTALL_PATH}/conf/.repo_secret_key)
    else
        REPO_SECRET_KEY=$(uuid -v4)
        echo $REPO_SECRET_KEY > ${INSTALL_PATH}/conf/.repo_secret_key
    fi

    if [ -f  ${INSTALL_PATH}/conf/.passwd_env ];then
        source ${INSTALL_PATH}/conf/.passwd_env
    fi
    docker exec opsany-paas-websocket /bin/sh -c "python3 /opt/opsany/saas/register_online_saas.py --paas_domain https://${DOMAIN_NAME} --username admin --password ${ADMIN_PASSWORD} --saas_app_code repo --saas_app_name 制品仓库 --saas_app_version ${SAAS_VERSION} --saas_app_secret_key ${REPO_SECRET_KEY}"

    # repo Configure
    if [ -d ${INSTALL_PATH}/conf/opsany-saas/repo ];then
        /bin/cp -r ./conf/opsany-saas/repo/* ${INSTALL_PATH}/conf/opsany-saas/repo/
    else
        /bin/cp -r ./conf/opsany-saas/repo ${INSTALL_PATH}/conf/opsany-saas/
    fi
    sed -i "s/DOMAIN_NAME/${DOMAIN_NAME}/g" ${INSTALL_PATH}/conf/opsany-saas/repo/repo-init.py
    sed -i "s/REPO_SECRET_KEY/${REPO_SECRET_KEY}/g" ${INSTALL_PATH}/conf/opsany-saas/repo/repo-init.py
    sed -i "s/MYSQL_SERVER_IP/${MYSQL_SERVER_IP}/g" ${INSTALL_PATH}/conf/opsany-saas/repo/repo-prod.py
    sed -i "s/MYSQL_SERVER_PORT/${MYSQL_SERVER_PORT}/g" ${INSTALL_PATH}/conf/opsany-saas/repo/repo-prod.py
    sed -i "s/MYSQL_OPSANY_REPO_PASSWORD/${MYSQL_OPSANY_REPO_PASSWORD}/g" ${INSTALL_PATH}/conf/opsany-saas/repo/repo-prod.py
    sed -i "s/MONGO_SERVER_IP/${MONGO_SERVER_IP}/g" ${INSTALL_PATH}/conf/opsany-saas/repo/repo-prod.py
    sed -i "s/MONGO_SERVER_PORT/${MONGO_SERVER_PORT}/g" ${INSTALL_PATH}/conf/opsany-saas/repo/repo-prod.py
    sed -i "s/MONGO_DEVOPS_PASSWORD/${MONGO_DEVOPS_PASSWORD}/g" ${INSTALL_PATH}/conf/opsany-saas/repo/repo-prod.py
    sed -i "s/REDIS_SERVER_IP/${REDIS_SERVER_IP}/g" ${INSTALL_PATH}/conf/opsany-saas/repo/repo-prod.py
    sed -i "s/REDIS_SERVER_PORT/${REDIS_SERVER_PORT}/g" ${INSTALL_PATH}/conf/opsany-saas/repo/repo-prod.py
    sed -i "s/REDIS_SERVER_USER/${REDIS_SERVER_USER}/g" ${INSTALL_PATH}/conf/opsany-saas/repo/repo-prod.py
    sed -i "s/REDIS_SERVER_PASSWORD/${REDIS_SERVER_PASSWORD}/g" ${INSTALL_PATH}/conf/opsany-saas/repo/repo-prod.py
    
    # Starter container
    docker pull ${PAAS_DOCKER_REG}/opsany-saas-ce-repo:${SAAS_VERSION}
    docker run -d --restart=always --name opsany-saas-ce-repo \
       -p 7020:80 \
       -v ${INSTALL_PATH}/conf/opsany-saas/repo/repo-supervisor.ini:/etc/supervisord.d/repo.ini \
       -v ${INSTALL_PATH}/conf/opsany-saas/repo/repo-uwsgi.ini:/opt/opsany/uwsgi/repo.ini \
       -v ${INSTALL_PATH}/conf/opsany-saas/repo/repo-init.py:/opt/opsany/repo/config/__init__.py \
       -v ${INSTALL_PATH}/conf/opsany-saas/repo/repo-prod.py:/opt/opsany/repo/config/prod.py \
       -v ${INSTALL_PATH}/conf/opsany-saas/repo/repo-nginx.conf:/etc/nginx/http.d/default.conf \
       -v ${INSTALL_PATH}/logs:/opt/opsany/logs \
       -v ${INSTALL_PATH}/uploads:/opt/opsany/uploads \
       -v /etc/localtime:/etc/localtime:ro \
       ${PAAS_DOCKER_REG}/opsany-saas-ce-repo:${SAAS_VERSION}
    
    # Django migrate
    docker exec -e BK_ENV="production" opsany-saas-ce-repo /bin/sh -c \
    "python /opt/opsany/repo/manage.py migrate --noinput && python /opt/opsany/repo/manage.py createcachetable django_cache > /dev/null" >> ${SHELL_LOG}
}

saas_pipeline_deploy(){
    shell_log "======Pipeline: Start pipeline======"
    cd ${CDIR}
    #pipeline mysql
    export MYSQL_PWD=${MYSQL_ROOT_PASSWORD}
    mysql -h "${MYSQL_SERVER_IP}" -P ${MYSQL_SERVER_PORT} -u root -e "create database pipeline DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;"
    mysql -h "${MYSQL_SERVER_IP}" -P ${MYSQL_SERVER_PORT} -u root -e "CREATE USER 'pipeline'@'%' identified by "\"${MYSQL_OPSANY_PIPELINE_PASSWORD}\"";"
    mysql -h "${MYSQL_SERVER_IP}" -P ${MYSQL_SERVER_PORT} -u root -e "grant all on pipeline.* to pipeline@'%';" 

    # Register pipeline
    if [ -f ${INSTALL_PATH}/conf/.pipeline_secret_key ];then
        PIPELINE_SECRET_KEY=$(cat ${INSTALL_PATH}/conf/.pipeline_secret_key)
    else
        PIPELINE_SECRET_KEY=$(uuid -v4)
        echo $PIPELINE_SECRET_KEY > ${INSTALL_PATH}/conf/.pipeline_secret_key
    fi

    if [ -f  ${INSTALL_PATH}/conf/.passwd_env ];then
        source ${INSTALL_PATH}/conf/.passwd_env
    fi
    docker exec opsany-paas-websocket /bin/sh -c "python3 /opt/opsany/saas/register_online_saas.py --paas_domain https://${DOMAIN_NAME} --username admin --password ${ADMIN_PASSWORD} --saas_app_code pipeline --saas_app_name 流水线 --saas_app_version ${SAAS_VERSION} --saas_app_secret_key ${PIPELINE_SECRET_KEY}"

    # Modify configuration
    if [ -d ${INSTALL_PATH}/conf/opsany-saas/pipeline ];then
        /bin/cp -r ./conf/opsany-saas/pipeline/* ${INSTALL_PATH}/conf/opsany-saas/pipeline/
    else
        /bin/cp -r ./conf/opsany-saas/pipeline ${INSTALL_PATH}/conf/opsany-saas/
    fi
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
    docker pull ${PAAS_DOCKER_REG}/opsany-saas-ce-pipeline:${SAAS_VERSION}
    docker run -d --restart=always --name opsany-saas-ce-pipeline \
       -p 7017:80 \
       -v ${INSTALL_PATH}/conf/opsany-saas/pipeline/pipeline-supervisor.ini:/etc/supervisord.d/pipeline.ini \
       -v ${INSTALL_PATH}/conf/opsany-saas/pipeline/pipeline-uwsgi.ini:/opt/opsany/uwsgi/pipeline.ini \
       -v ${INSTALL_PATH}/conf/opsany-saas/pipeline/pipeline-init.py:/opt/opsany/pipeline/config/__init__.py \
       -v ${INSTALL_PATH}/conf/opsany-saas/pipeline/pipeline-prod.py:/opt/opsany/pipeline/config/prod.py \
       -v ${INSTALL_PATH}/conf/opsany-saas/pipeline/pipeline-nginx.conf:/etc/nginx/http.d/default.conf \
       -v ${INSTALL_PATH}/logs/pipeline:/opt/opsany/logs/pipeline \
       -v ${INSTALL_PATH}/uploads:/opt/opsany/uploads \
       -v /etc/localtime:/etc/localtime:ro \
       ${PAAS_DOCKER_REG}/opsany-saas-ce-pipeline:${SAAS_VERSION}
    
    # Django migrate
    docker exec -e BK_ENV="production" opsany-saas-ce-pipeline /bin/sh -c \
    "python /opt/opsany/pipeline/manage.py migrate --noinput && python /opt/opsany/pipeline/manage.py createcachetable django_cache > /dev/null" >> ${SHELL_LOG}
}

saas_deploy_deploy(){
    shell_log "======Deploy: Start deploy======"
    cd ${CDIR}
    #deploy
    export MYSQL_PWD=${MYSQL_ROOT_PASSWORD}
    mysql -h "${MYSQL_SERVER_IP}" -P ${MYSQL_SERVER_PORT} -u root -e "create database deploy DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;"
    mysql -h "${MYSQL_SERVER_IP}" -P ${MYSQL_SERVER_PORT} -u root -e "CREATE USER 'deploy'@'%' identified by "\"${MYSQL_OPSANY_DEPLOY_PASSWORD}\"";"
    mysql -h "${MYSQL_SERVER_IP}" -P ${MYSQL_SERVER_PORT} -u root -e "grant all on deploy.* to deploy@'%';" 

    # Register deploy
    if [ -f ${INSTALL_PATH}/conf/.deploy_secret_key ];then
        DEPLOY_SECRET_KEY=$(cat ${INSTALL_PATH}/conf/.deploy_secret_key)
    else
        DEPLOY_SECRET_KEY=$(uuid -v4)
        echo $DEPLOY_SECRET_KEY > ${INSTALL_PATH}/conf/.deploy_secret_key
    fi

    if [ -f  ${INSTALL_PATH}/conf/.passwd_env ];then
        source ${INSTALL_PATH}/conf/.passwd_env
    fi
    docker exec opsany-paas-websocket /bin/sh -c "python3 /opt/opsany/saas/register_online_saas.py --paas_domain https://${DOMAIN_NAME} --username admin --password ${ADMIN_PASSWORD} --saas_app_code deploy --saas_app_name 持续部署 --saas_app_version ${SAAS_VERSION} --saas_app_secret_key ${DEPLOY_SECRET_KEY}"

    # Modify configuration
    if [ -d ${INSTALL_PATH}/conf/opsany-saas/deploy ];then
        /bin/cp -r ./conf/opsany-saas/deploy/* ${INSTALL_PATH}/conf/opsany-saas/deploy/
    else
        /bin/cp -r ./conf/opsany-saas/deploy ${INSTALL_PATH}/conf/opsany-saas/
    fi
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
    docker pull ${PAAS_DOCKER_REG}/opsany-saas-ce-deploy:${SAAS_VERSION}
    docker run -d --restart=always --name opsany-saas-ce-deploy \
       -p 7018:80 \
       -v ${INSTALL_PATH}/conf/opsany-saas/deploy/deploy-supervisor.ini:/etc/supervisord.d/deploy.ini \
       -v ${INSTALL_PATH}/conf/opsany-saas/deploy/deploy-uwsgi.ini:/opt/opsany/uwsgi/deploy.ini \
       -v ${INSTALL_PATH}/conf/opsany-saas/deploy/deploy-init.py:/opt/opsany/deploy/config/__init__.py \
       -v ${INSTALL_PATH}/conf/opsany-saas/deploy/deploy-prod.py:/opt/opsany/deploy/config/prod.py \
       -v ${INSTALL_PATH}/conf/opsany-saas/deploy/deploy-nginx.conf:/etc/nginx/http.d/default.conf \
       -v ${INSTALL_PATH}/logs/deploy:/opt/opsany/logs/deploy \
       -v ${INSTALL_PATH}/uploads:/opt/opsany/uploads \
       -v /etc/localtime:/etc/localtime:ro \
       ${PAAS_DOCKER_REG}/opsany-saas-ce-deploy:${SAAS_VERSION}
    
    # Django migrate
    docker exec -e BK_ENV="production" opsany-saas-ce-deploy /bin/sh -c \
    "python /opt/opsany/deploy/manage.py migrate --noinput && python /opt/opsany/deploy/manage.py createcachetable django_cache > /dev/null" >> ${SHELL_LOG}
}

saas_code_deploy(){
    shell_log "======Code: Start Code======"
    cd ${CDIR}
    #Code
    export MYSQL_PWD=${MYSQL_ROOT_PASSWORD}
    mysql -h "${MYSQL_SERVER_IP}" -P ${MYSQL_SERVER_PORT} -u root -e "create database code DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;"
    mysql -h "${MYSQL_SERVER_IP}" -P ${MYSQL_SERVER_PORT} -u root -e "CREATE USER 'code'@'%' identified by "\"${MYSQL_OPSANY_CODE_PASSWORD}\"";"
    mysql -h "${MYSQL_SERVER_IP}" -P ${MYSQL_SERVER_PORT} -u root -e "grant all on code.* to code@'%';" 

     #Code
    sed -i "s/DOMAIN_NAME/$DOMAIN_NAME/g" ${INSTALL_PATH}/esb/apis/code/toolkit/configs.py
    sed -i "s#/t/code#/o/code#g" ${INSTALL_PATH}/esb/apis/code/toolkit/tools.py

    # Register Code
    if [ -f ${INSTALL_PATH}/conf/.passwd_env ];then
        source ${INSTALL_PATH}/conf/.passwd_env
    fi

    if [ -f ${INSTALL_PATH}/conf/.code_secret_key ];then
        CODE_SECRET_KEY=$(cat ${INSTALL_PATH}/conf/.code_secret_key)
    else
        CODE_SECRET_KEY=$(uuid -v4)
        echo $CODE_SECRET_KEY > ${INSTALL_PATH}/conf/.code_secret_key
    fi
    docker exec opsany-paas-websocket /bin/sh -c "python3 /opt/opsany/saas/register_online_saas.py --paas_domain https://${DOMAIN_NAME} --username admin --password ${ADMIN_PASSWORD} --saas_app_code code --saas_app_name 代码仓库 --saas_app_version ${SAAS_VERSION} --saas_app_secret_key ${CODE_SECRET_KEY}"

    # Code Configure
    CODE_SECRET_KEY=$(cat ${INSTALL_PATH}/conf/.code_secret_key)
    sed -i "s/DOMAIN_NAME/${DOMAIN_NAME}/g" ${INSTALL_PATH}/conf/opsany-saas/code/code-init.py
    sed -i "s/CODE_SECRET_KEY/${CODE_SECRET_KEY}/g" ${INSTALL_PATH}/conf/opsany-saas/code/code-init.py
    sed -i "s/MYSQL_SERVER_IP/${MYSQL_SERVER_IP}/g" ${INSTALL_PATH}/conf/opsany-saas/code/code-prod.py
    sed -i "s/MYSQL_SERVER_PORT/${MYSQL_SERVER_PORT}/g" ${INSTALL_PATH}/conf/opsany-saas/code/code-prod.py
    sed -i "s/MYSQL_OPSANY_CODE_PASSWORD/${MYSQL_OPSANY_CODE_PASSWORD}/g" ${INSTALL_PATH}/conf/opsany-saas/code/code-prod.py

    # Starter container
    docker pull ${PAAS_DOCKER_REG}/opsany-saas-ce-code:${SAAS_VERSION}
    docker run -d --restart=always --name opsany-saas-ce-code \
       -p 7010:80 \
       -v ${INSTALL_PATH}/conf/opsany-saas/code/code-supervisor.ini:/etc/supervisord.d/code.ini \
       -v ${INSTALL_PATH}/conf/opsany-saas/code/code-uwsgi.ini:/opt/opsany/uwsgi/code.ini \
       -v ${INSTALL_PATH}/conf/opsany-saas/code/code-init.py:/opt/opsany/code/config/__init__.py \
       -v ${INSTALL_PATH}/conf/opsany-saas/code/code-prod.py:/opt/opsany/code/config/prod.py \
       -v ${INSTALL_PATH}/conf/opsany-saas/code/code-nginx.conf:/etc/nginx/http.d/default.conf \
       -v ${INSTALL_PATH}/logs:/opt/opsany/logs \
       -v ${INSTALL_PATH}/uploads:/opt/opsany/uploads \
       -v /etc/localtime:/etc/localtime:ro \
       ${PAAS_DOCKER_REG}/opsany-saas-ce-code:${SAAS_VERSION}

    # Django migrate
    docker exec -e BK_ENV="production" opsany-saas-ce-code /bin/sh -c \
    "python /opt/opsany/code/manage.py migrate --noinput && python /opt/opsany/code/manage.py createcachetable django_cache > /dev/null" >> ${SHELL_LOG}
    
}

zabbix_install(){
   shell_log "=====Start Zabbix Server 7.0 LTS======"
   mkdir -p ${INSTALL_PATH}/{zabbix-volume/alertscripts,zabbix-volume/externalscripts,zabbix-volume/snmptraps}
   docker run --restart=always --name opsany-zabbix-server-7.0.3 -t \
     -e DB_SERVER_HOST="${MYSQL_SERVER_IP}" \
     -e DB_SERVER_PORT="3306" \
     -e MYSQL_DATABASE="${ZABBIX_DB_NAME}" \
     -e MYSQL_USER="${ZABBIX_DB_USER}" \
     -e MYSQL_PASSWORD="${ZABBIX_DB_PASSWORD}" \
     -e MYSQL_ROOT_PASSWORD="${MYSQL_ROOT_PASSWORD}" \
     -p 10051:10051 \
     -v ${INSTALL_PATH}/zabbix-volume/alertscripts:/usr/lib/zabbix/alertscripts \
     -v ${INSTALL_PATH}/zabbix-volume/externalscripts:/usr/lib/zabbix/externalscripts \
     -v ${INSTALL_PATH}/zabbix-volume/snmptraps:/var/lib/zabbix/snmptraps \
     -v /etc/localtime:/etc/localtime:ro \
     -d ${PAAS_DOCKER_REG}/zabbix-server-mysql:7.0.3-ubuntu

   sleep 15
   shell_log "=====Start Zabbix Web 7.0 LTS======"
   docker run --restart=always --name opsany-zabbix-web-7.0.3 -t \
     -e ZBX_SERVER_HOST="${MYSQL_SERVER_IP}" \
     -e DB_SERVER_HOST="${MYSQL_SERVER_IP}" \
     -e DB_SERVER_PORT="3306" \
     -e MYSQL_DATABASE="${ZABBIX_DB_NAME}" \
     -e MYSQL_USER="${ZABBIX_DB_USER}" \
     -e MYSQL_PASSWORD="${ZABBIX_DB_PASSWORD}" \
     -e MYSQL_ROOT_PASSWORD="${MYSQL_ROOT_PASSWORD}" \
     -e PHP_TZ="Asia/Shanghai" \
     -e ZBX_SERVER_NAME="opsany-server" \
     -v /etc/localtime:/etc/localtime:ro \
     -p 8006:8080 \
     -d ${PAAS_DOCKER_REG}/zabbix-web-nginx-mysql:7.0.3-ubuntu

    shell_log "=====Start Zabbix Agent2 7.0 LTS======"
    docker run --restart=always --name opsany-zabbix-agent2 -t \
     -e ZBX_HOSTNAME="opsany-server" \
     -e ZBX_SERVER_HOST="${LOCAL_IP}" \
     -e ZBX_ACTIVE_ALLOW=true \
     -e ZBX_PASSIVE_ALLOW=false \
     -v /etc/localtime:/etc/localtime:ro \
     -d ${PAAS_DOCKER_REG}/zabbix-agent2:7.0.3-ubuntu
}

saas_base_init(){
    shell_log "======Init: OpsAny User Initialize======"
    cd ${CDIR}
    # Sync User
    docker exec opsany-paas-websocket /bin/sh -c "python3 /opt/opsany/saas/sync-user-script.py --domain https://${DOMAIN_NAME} --paas_username admin --paas_password ${ADMIN_PASSWORD} --app_code workbench cmdb control job cmp bastion"

    shell_log "======Init: OpsAny Workbench Initialize======"
    # Create Service
    docker exec opsany-paas-websocket /bin/sh -c "python3 /opt/opsany/saas/init_work_order.py --domain https://$DOMAIN_NAME --paas_username admin --paas_password ${ADMIN_PASSWORD}"

    shell_log "======Init: OpsAny Proxy Initialize======"
    # Create Proxy Token
    PROXY_TOKEN=$(docker exec -e OPS_ANY_ENV=production \
            opsany-paas-proxy /bin/sh -c " /usr/local/bin/python3 /opt/opsany-proxy/manage.py create_access" | grep 'Access' | awk -F ': ' '{print $2}' | awk -F '.' '{print $1}')  >> ${SHELL_LOG} 2>&1
    docker exec opsany-paas-websocket /bin/sh -c "python3 /opt/opsany/saas/init-ce-base.py --domain $DOMAIN_NAME --private_ip $LOCAL_IP --paas_username admin --paas_password ${ADMIN_PASSWORD} --proxy_url https://${PROXY_LOCAL_IP}:8011 --proxy_public_url https://${PROXY_PUBLIC_IP}:8011 --proxy_token $PROXY_TOKEN >> ${SHELL_LOG} 2>&1"

    shell_log "======Init: OpsAny Job Initialize======"
    # Init Script Job
    cd $CDIR/init/
    docker exec opsany-paas-websocket /bin/sh -c "cd /opt/opsany/init/ && python3 import_script.py --domain https://${DOMAIN_NAME} --paas_username admin --paas_password ${ADMIN_PASSWORD} --target_type script --target_path ./job-script >> ${SHELL_LOG} 2>&1"
    docker exec opsany-paas-websocket /bin/sh -c "cd /opt/opsany/init/ && python3 import_script.py --domain https://$DOMAIN_NAME --paas_username admin --paas_password ${ADMIN_PASSWORD} --target_type task --target_path ./job-task >> ${SHELL_LOG} 2>&1"

    shell_log "======Init: OpsAny Dashboard Initialize======"
    # Init Script Job
    cd $CDIR/init/
    docker exec opsany-paas-websocket /bin/sh -c "cd /opt/opsany/init/ && python3 init_dashboard.py --grafana_url https://${DOMAIN_NAME}/grafana/ --grafana_username admin --grafana_password $GRAFANA_ADMIN_PASSWORD"

    shell_log "======Init: Download Agent+Docs Package======"
    cd $INSTALL_PATH/uploads/
    wget https://opsany.oss-cn-beijing.aliyuncs.com/opsany-agent-2.2.3.tar.gz
    tar zxf opsany-agent-2.2.3.tar.gz
    wget https://opsany.oss-cn-beijing.aliyuncs.com/opsany-docs-2.2.3.tar.gz
    tar zxf opsany-docs-2.2.3.tar.gz

    shell_log "=====Zabbix Automatic Integration======"
    cd ${CDIR}
    if [ -z "$ADMIN_PASSWORD" ];then
        source ${INSTALL_PATH}/conf/.passwd_env
    fi
    docker exec opsany-paas-websocket /bin/sh -c "python3 /opt/opsany/saas/init-ce-monitor-zabbix.py --domain $DOMAIN_NAME --private_ip $LOCAL_IP --paas_username admin --paas_password $ADMIN_PASSWORD --zabbix_ip $LOCAL_IP --zabbix_password zabbix --grafana_ip $LOCAL_IP --grafana_password $GRAFANA_ADMIN_PASSWORD --zabbix_api_password ${ZABBIX_API_PASSWORD}  --modify_zabbix_password ${ZABBIX_ADMIN_PASSWORD} --zabbix_version 7.0"
}

admin_password_init(){
    shell_warning_log "======OpsAny: Make Ops Perfect======" 
    PRESTR='Ops'
    STR=`head /dev/urandom | tr -dc A-Za-z0-9 | head -c 5`
    NUM=`echo $RANDOM`
    ADMIN_NEW_PASSWORD=$PRESTR$STR$NUM
    echo "ADMIN_PASSWORD=$ADMIN_NEW_PASSWORD" > ${INSTALL_PATH}/conf/.passwd_env
    docker exec opsany-paas-websocket /bin/sh -c "python3 /opt/opsany/saas/password-init.py --paas_domain https://$DOMAIN_NAME --username admin --password ${ADMIN_PASSWORD} --new_password $ADMIN_NEW_PASSWORD"
    shell_error_log "Web: https://$DOMAIN_NAME Username: admin Password: $ADMIN_NEW_PASSWORD"
}

# Main
main(){
    case "$1" in
    base)
        install_init
        mongodb_init
        proxy_install
        saas_rbac_deploy
        saas_workbench_deploy
        saas_cmdb_deploy
        saas_control_deploy
        saas_job_deploy
        saas_cmp_deploy
        saas_bastion_deploy
        saas_monitor_deploy
        saas_base_init
        admin_password_init
        ;;
    ops)
        install_init
        mongodb_init
        proxy_install
        saas_rbac_deploy
        saas_workbench_deploy
        saas_cmdb_deploy
        saas_control_deploy
        saas_monitor_deploy
        zabbix_install
        saas_job_deploy
	    saas_cmp_deploy
	    saas_bastion_deploy
        saas_base_init
        admin_password_init
        ;;
    monitor)
        saas_monitor_deploy
        ;;
    repo)
        saas_repo_deploy
        ;;
    code)
        saas_code_deploy
        ;;
    pipeline)
        saas_pipeline_deploy
        ;;
    deploy)
        saas_deploy_deploy
        ;;
    devops)
	    saas_devops_deploy
        saas_pipeline_deploy
        saas_deploy_deploy
        saas_repo_deploy
        #saas_code_deploy
	    ;;
    dev)
	    saas_devops_deploy
        saas_pipeline_deploy
        saas_deploy_deploy
        saas_repo_deploy
        #saas_code_deploy
        ;;
    all)
        install_init
        mongodb_init
        proxy_install
        saas_rbac_deploy
        saas_workbench_deploy
        saas_cmdb_deploy
        saas_control_deploy
        saas_monitor_deploy
        zabbix_install
        saas_job_deploy
        saas_cmp_deploy
        saas_bastion_deploy
        saas_base_init
        #saas_code_deploy
        saas_devops_deploy
        saas_pipeline_deploy
        saas_deploy_deploy
        saas_repo_deploy
        admin_password_init
        ;;
    help|*)
	    echo $"Usage: $0 {ops|dev|devops|base|all|help}"
	    ;;
    esac
}

main $1 
