#!/bin/bash
#******************************************
# Author:       Jason Zhao
# Email:        zhaoshundong@opsany.com
# Organization: OpsAny https://www.opsany.com/
# Description:  OpsAny Community Edition Update Script
#******************************************

# Data/Time Variables
CTIME=$(date "+%Y-%m-%d-%H-%M")

# Shell Envionment Variables
CDIR=$(pwd)
SHELL_NAME="opsany-ce-update.sh"
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
    grep '^[A-Z]' install.config > install.env
    source ./install.env && rm -f install.env
    if [ -z "$ADMIN_PASSWORD" ];then
        source ${INSTALL_PATH}/conf/.passwd_env
    fi
fi

# PaaS Service Update
paas_update(){
    #paas
    shell_log "======Update paas Service======"
    # PaaS Config
    UPDATE_VERSION=$1
    /bin/cp conf/settings_production.py.paas ${INSTALL_PATH}/conf/settings_production.py.paas
    sed -i "s/PAAS_LOGIN_IP/${PAAS_LOGIN_IP}/g" ${INSTALL_PATH}/conf/settings_production.py.paas
    sed -i "s/PAAS_APPENGINE_IP/${PAAS_APPENGINE_IP}/g" ${INSTALL_PATH}/conf/settings_production.py.paas
    sed -i "s/DOMAIN_NAME/${DOMAIN_NAME}/g" ${INSTALL_PATH}/conf/settings_production.py.paas
    sed -i "s/LOCAL_IP/${LOCAL_IP}/g" ${INSTALL_PATH}/conf/settings_production.py.paas
    sed -i "s/MYSQL_SERVER_IP/${MYSQL_SERVER_IP}/g" ${INSTALL_PATH}/conf/settings_production.py.paas
    sed -i "s/MYSQL_OPSANY_PASSWORD/${MYSQL_OPSANY_PASSWORD}/g" ${INSTALL_PATH}/conf/settings_production.py.paas

    docker stop opsany-paas-paas && docker rm opsany-paas-paas 
    docker pull ${PAAS_DOCKER_REG}/opsany-paas-paas:${UPDATE_VERSION}
    docker run -d --restart=always --name opsany-paas-paas \
    -p 8001:8001 -v ${INSTALL_PATH}/logs:/opt/opsany/logs \
    -v ${INSTALL_PATH}/conf/settings_production.py.paas:/opt/opsany/paas/paas/conf/settings_production.py \
    -v /etc/localtime:/etc/localtime:ro \
    ${PAAS_DOCKER_REG}/opsany-paas-paas:${UPDATE_VERSION}
}

login_update(){
 #login
    shell_log "Start login Service"
    #Login Config
    UPDATE_VERSION=$1
    RBAC_SECRET_KEY=$(cat ${INSTALL_PATH}/conf/.rbac_secret_key)
    /bin/cp conf/settings_production.py.login ${INSTALL_PATH}/conf/settings_production.py.login
    sed -i "s/RBAC_SECRET_KEY/${RBAC_SECRET_KEY}/g" ${INSTALL_PATH}/conf/settings_production.py.login
    sed -i "s/DOMAIN_NAME/${DOMAIN_NAME}/g" ${INSTALL_PATH}/conf/settings_production.py.login
    sed -i "s/LOCAL_IP/${LOCAL_IP}/g" ${INSTALL_PATH}/conf/settings_production.py.login
    sed -i "s/MYSQL_SERVER_IP/${MYSQL_SERVER_IP}/g" ${INSTALL_PATH}/conf/settings_production.py.login
    sed -i "s/MYSQL_OPSANY_PASSWORD/${MYSQL_OPSANY_PASSWORD}/g" ${INSTALL_PATH}/conf/settings_production.py.login

    docker stop opsany-paas-login && docker rm opsany-paas-login 
    docker pull ${PAAS_DOCKER_REG}/opsany-paas-login:${UPDATE_VERSION}
    docker run -d --restart=always --name opsany-paas-login \
    -p 8003:8003 -v ${INSTALL_PATH}/logs:/opt/opsany/logs \
    -v ${INSTALL_PATH}/conf/settings_production.py.login:/opt/opsany/paas/login/conf/settings_production.py \
    -v /etc/localtime:/etc/localtime:ro \
    ${PAAS_DOCKER_REG}/opsany-paas-login:${UPDATE_VERSION}
}

esb_update(){
#esb
    shell_log "Start esb Service"
    # ESB Config
    UPDATE_VERSION=$1
    /bin/cp conf/settings_production.py.esb ${INSTALL_PATH}/conf/settings_production.py.esb
    sed -i "s/PAAS_LOGIN_IP/${PAAS_LOGIN_IP}/g" ${INSTALL_PATH}/conf/settings_production.py.esb
    sed -i "s/PAAS_PAAS_IP/${PAAS_PAAS_IP}/g" ${INSTALL_PATH}/conf/settings_production.py.esb
    sed -i "s/REDIS_SERVER_IP/${REDIS_SERVER_IP}/g" ${INSTALL_PATH}/conf/settings_production.py.esb
    sed -i "s/REDIS_SERVER_PASSWORD/${REDIS_SERVER_PASSWORD}/g" ${INSTALL_PATH}/conf/settings_production.py.esb
    sed -i "s/MYSQL_SERVER_IP/${MYSQL_SERVER_IP}/g" ${INSTALL_PATH}/conf/settings_production.py.esb
    sed -i "s/MYSQL_OPSANY_PASSWORD/${MYSQL_OPSANY_PASSWORD}/g" ${INSTALL_PATH}/conf/settings_production.py.esb

    docker stop opsany-paas-esb && docker rm opsany-paas-esb 
    docker pull ${PAAS_DOCKER_REG}/opsany-paas-esb:${UPDATE_VERSION}
    docker run -d --restart=always --name opsany-paas-esb \
    -p 8002:8002 -v ${INSTALL_PATH}/logs:/opt/opsany/logs \
    -v ${INSTALL_PATH}/esb/apis:/opt/opsany/paas/esb/components/generic/apis \
    -v ${INSTALL_PATH}/conf/settings_production.py.esb:/opt/opsany/paas/esb/configs/default.py \
    -v /etc/localtime:/etc/localtime:ro \
    ${PAAS_DOCKER_REG}/opsany-paas-esb:${UPDATE_VERSION}
}  

appengine_update(){
 #appengine
    # App Engine Config
    UPDATE_VERSION=$1
    /bin/cp conf/settings_production.py.appengine ${INSTALL_PATH}/conf/settings_production.py.appengine
    sed -i "s/MYSQL_SERVER_IP/${MYSQL_SERVER_IP}/g" ${INSTALL_PATH}/conf/settings_production.py.appengine
    sed -i "s/MYSQL_OPSANY_PASSWORD/${MYSQL_OPSANY_PASSWORD}/g" ${INSTALL_PATH}/conf/settings_production.py.appengine
    shell_log "Start appengine Service"

    docker stop opsany-paas-appengine && docker rm opsany-paas-appengine 
    docker pull ${PAAS_DOCKER_REG}/opsany-paas-appengine:${UPDATE_VERSION}
    docker run -d --restart=always --name opsany-paas-appengine \
    -p 8000:8000 -v ${INSTALL_PATH}/logs:/opt/opsany/logs \
    -v ${INSTALL_PATH}/conf/settings_production.py.appengine:/opt/opsany/paas/appengine/controller/settings.py \
    -v /etc/localtime:/etc/localtime:ro \
    ${PAAS_DOCKER_REG}/opsany-paas-appengine:${UPDATE_VERSION}
}  

# Update Proxy
proxy_update(){
    shell_log "======Update Proxy======"
    UPDATE_VERSION=$1
    # Proxy config
    CONTROL_SECRET_KEY=$(cat ${INSTALL_PATH}/conf/.control_secret_key)
    /bin/cp conf/proxy/settings_production.py.proxy ${INSTALL_PATH}/conf/proxy/
    sed -i "s/REDIS_SERVER_IP/${REDIS_SERVER_IP}/g" ${INSTALL_PATH}/conf/proxy/settings_production.py.proxy
    sed -i "s/REDIS_SERVER_PASSWORD/${REDIS_SERVER_PASSWORD}/g" ${INSTALL_PATH}/conf/proxy/settings_production.py.proxy
    sed -i "s/MYSQL_SERVER_IP/${MYSQL_SERVER_IP}/g" ${INSTALL_PATH}/conf/proxy/settings_production.py.proxy
    sed -i "s/MYSQL_OPSANY_PASSWORD/${MYSQL_OPSANY_PASSWORD}/g" ${INSTALL_PATH}/conf/proxy/settings_production.py.proxy
    sed -i "s/local-proxy.opsany.com/${PROXY_LOCAL_IP}/g" ${INSTALL_PATH}/conf/proxy/settings_production.py.proxy
    sed -i "s/public-proxy.opsany.com/${PROXY_PUBLIC_IP}/g" ${INSTALL_PATH}/conf/proxy/settings_production.py.proxy
    sed -i "s/LOCAL_IP/${PROXY_PUBLIC_IP} ${PROXY_LOCAL_IP}/g" ${INSTALL_PATH}/conf/proxy/nginx-conf.d/nginx_proxy.conf
    sed -i "s/DOMAIN_NAME/${PROXY_PUBLIC_IP} ${PROXY_LOCAL_IP}/g" ${INSTALL_PATH}/conf/proxy/nginx-conf.d/nginx_proxy.conf
    sed -i "s/RABBIT_SERVER_IP/${RABBIT_SERVER_IP}/g" ${INSTALL_PATH}/conf/proxy/settings_production.py.proxy
    sed -i "s/RABBITMQ_DEFAULT_USER/${RABBITMQ_DEFAULT_USER}/g" ${INSTALL_PATH}/conf/proxy/settings_production.py.proxy
    sed -i "s/RABBITMQ_DEFAULT_PASS/${RABBITMQ_DEFAULT_PASS}/g" ${INSTALL_PATH}/conf/proxy/settings_production.py.proxy
    sed -i "s/CONTROL_SECRET_KEY_PROXY/${CONTROL_SECRET_KEY}/g" ${INSTALL_PATH}/conf/proxy/settings_production.py.proxy
    cp ../saas/invscript_proxy.py ${INSTALL_PATH}/conf/proxy/
    sed -i "s/LOCALHOST/${MYSQL_SERVER_IP}/g" ${INSTALL_PATH}/conf/proxy/invscript_proxy.py
    sed -i "s/PROXY_PASSWORD/${MYSQL_OPSANY_PASSWORD}/g" ${INSTALL_PATH}/conf/proxy/invscript_proxy.py
    sed -i "s/CONTROL_SECRET_KEY/${CONTROL_SECRET_KEY}/g" ${INSTALL_PATH}/conf/proxy/invscript_proxy.py
    chmod +x ${INSTALL_PATH}/conf/proxy/invscript_proxy.py

    # Starter container
    docker stop opsany-paas-proxy && docker rm opsany-paas-proxy 
    docker pull ${PAAS_DOCKER_REG}/opsany-paas-proxy:${UPDATE_VERSION}
    docker run --restart=always --name opsany-paas-proxy -d \
        -p 4505:4505 -p 4506:4506 -p 8010:8010 \
        -v ${INSTALL_PATH}/logs:${INSTALL_PATH}/logs \
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
        -v /etc/localtime:/etc/localtime:ro \
        ${PAAS_DOCKER_REG}/opsany-paas-proxy:${UPDATE_VERSION}

    # OpsAny Database Init
    docker exec -e OPS_ANY_ENV=production \
        opsany-paas-proxy /bin/sh -c "/usr/local/bin/python3 /opt/opsany-proxy/manage.py migrate >> ${SHELL_LOG}"
}

websocket_update(){
# Websocket
    UPDATE_VERSION=$1
    BASTION_SECRET_KEY=$(cat ${INSTALL_PATH}/conf/.bastion_secret_key)
    /bin/cp conf/settings_production.py.websocket ${INSTALL_PATH}/conf/settings_production.py.websocket
    /bin/cp conf/settings_production.py.websocket.init ${INSTALL_PATH}/conf/settings_production.py.websocket.init
    sed -i "s/BASTION_SECRET_KEY/${BASTION_SECRET_KEY}/g" ${INSTALL_PATH}/conf/settings_production.py.websocket.init
    sed -i "s/WEBSOCKET_GUACD_HOST/${WEBSOCKET_GUACD_HOST}/g" ${INSTALL_PATH}/conf/settings_production.py.websocket
    sed -i "s/REDIS_SERVER_IP/${REDIS_SERVER_IP}/g" ${INSTALL_PATH}/conf/settings_production.py.websocket
    sed -i "s/REDIS_SERVER_USER/${REDIS_SERVER_USER}/g" ${INSTALL_PATH}/conf/settings_production.py.websocket
    sed -i "s/REDIS_SERVER_PORT/${REDIS_SERVER_PORT}/g" ${INSTALL_PATH}/conf/settings_production.py.websocket
    sed -i "s/REDIS_SERVER_PASSWORD/${REDIS_SERVER_PASSWORD}/g" ${INSTALL_PATH}/conf/settings_production.py.websocket
    sed -i "s/MYSQL_SERVER_IP/${MYSQL_SERVER_IP}/g" ${INSTALL_PATH}/conf/settings_production.py.websocket
    sed -i "s/MYSQL_SERVER_PORT/${MYSQL_SERVER_PORT}/g" ${INSTALL_PATH}/conf/settings_production.py.websocket
    sed -i "s/MYSQL_OPSANY_PASSWORD/${MYSQL_OPSANY_PASSWORD}/g" ${INSTALL_PATH}/conf/settings_production.py.websocket
    sed -i "s/PAAS_PAAS_IP/${PAAS_PAAS_IP}/g" ${INSTALL_PATH}/conf/settings_production.py.websocket.init
    docker stop opsany-paas-websocket && docker rm opsany-paas-websocket
    docker run -d --restart=always --name opsany-paas-websocket \
    -p 8004:8004 -v ${INSTALL_PATH}/logs:/opt/opsany/logs \
    -v ${INSTALL_PATH}/uploads:/opt/opsany/uploads \
    -v ${INSTALL_PATH}/conf/settings_production.py.websocket:/opt/opsany/websocket/config/prod.py \
    -v ${INSTALL_PATH}/conf/settings_production.py.websocket.init:/opt/opsany/websocket/config/__init__.py \
    -v /usr/share/zoneinfo:/usr/share/zoneinfo \
    -v /etc/localtime:/etc/localtime:ro \
    ${PAAS_DOCKER_REG}/opsany-paas-websocket:${UPDATE_VERSION}
}

saas_rbac_update(){
    shell_log "======Update RBAC======"
    # Modify configuration
    UPDATE_VERSION=$1
    RBAC_SECRET_KEY=$(cat ${INSTALL_PATH}/conf/.rbac_secret_key)
    /bin/cp conf/opsany-saas/rbac/* ${INSTALL_PATH}/conf/opsany-saas/rbac/
    sed -i "s/DOMAIN_NAME/${DOMAIN_NAME}/g" ${INSTALL_PATH}/conf/opsany-saas/rbac/rbac-init.py
    sed -i "s/RBAC_SECRET_KEY/${RBAC_SECRET_KEY}/g" ${INSTALL_PATH}/conf/opsany-saas/rbac/rbac-init.py
    sed -i "s/MYSQL_SERVER_IP/${MYSQL_SERVER_IP}/g" ${INSTALL_PATH}/conf/opsany-saas/rbac/rbac-prod.py
    sed -i "s/MYSQL_SERVER_PORT/${MYSQL_SERVER_PORT}/g" ${INSTALL_PATH}/conf/opsany-saas/rbac/rbac-prod.py
    sed -i "s/MYSQL_OPSANY_RBAC_PASSWORD/${MYSQL_OPSANY_RBAC_PASSWORD}/g" ${INSTALL_PATH}/conf/opsany-saas/rbac/rbac-prod.py
    sed -i "s/REDIS_SERVER_IP/${REDIS_SERVER_IP}/g" ${INSTALL_PATH}/conf/opsany-saas/rbac/rbac-prod.py
    sed -i "s/REDIS_SERVER_PORT/${REDIS_SERVER_PORT}/g" ${INSTALL_PATH}/conf/opsany-saas/rbac/rbac-prod.py
    sed -i "s/REDIS_SERVER_USER/${REDIS_SERVER_USER}/g" ${INSTALL_PATH}/conf/opsany-saas/rbac/rbac-prod.py
    sed -i "s/REDIS_SERVER_PASSWORD/${REDIS_SERVER_PASSWORD}/g" ${INSTALL_PATH}/conf/opsany-saas/rbac/rbac-prod.py

    # Starter container
    docker stop opsany-saas-ce-rbac && docker rm opsany-saas-ce-rbac
    docker pull ${PAAS_DOCKER_REG}/opsany-saas-ce-rbac:${UPDATE_VERSION}
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
       ${PAAS_DOCKER_REG}/opsany-saas-ce-rbac:${UPDATE_VERSION}
    
    # Django migrate
    docker exec -e BK_ENV="production" opsany-saas-ce-rbac /bin/sh -c \
    "python /opt/opsany/rbac/manage.py migrate --noinput >> ${SHELL_LOG} && python /opt/opsany/rbac/manage.py createcachetable django_cache > /dev/null"
}

saas_workbench_update(){
    shell_log "======Update workbench======"
    # Modify configuration
    UPDATE_VERSION=$1
    WORKBENCH_SECRET_KEY=$(cat ${INSTALL_PATH}/conf/.workbench_secret_key)
    /bin/cp conf/opsany-saas/workbench/* ${INSTALL_PATH}/conf/opsany-saas/workbench/
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
    docker pull ${PAAS_DOCKER_REG}/opsany-saas-ce-workbench:${UPDATE_VERSION}
    docker stop opsany-saas-ce-workbench && docker rm opsany-saas-ce-workbench
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
       ${PAAS_DOCKER_REG}/opsany-saas-ce-workbench:${UPDATE_VERSION}
    # Django migrate
    docker exec -e BK_ENV="production" opsany-saas-ce-workbench /bin/sh -c \
    "python /opt/opsany/workbench/manage.py migrate --noinput >> ${SHELL_LOG} >> ${SHELL_LOG} && python /opt/opsany/workbench/manage.py createcachetable django_cache > /dev/null"
}

saas_cmdb_update(){
    shell_log "======Update cmdb======"
    # Modify configuration
    UPDATE_VERSION=$1
    CMDB_SECRET_KEY=$(cat ${INSTALL_PATH}/conf/.cmdb_secret_key)
    /bin/cp conf/opsany-saas/cmdb/* ${INSTALL_PATH}/conf/opsany-saas/cmdb/
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
    docker pull ${PAAS_DOCKER_REG}/opsany-saas-ce-cmdb:${UPDATE_VERSION}
    docker stop opsany-saas-ce-cmdb && docker rm opsany-saas-ce-cmdb
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
       ${PAAS_DOCKER_REG}/opsany-saas-ce-cmdb:${UPDATE_VERSION}
    
    # Django migrate
    docker exec -e BK_ENV="production" opsany-saas-ce-cmdb /bin/sh -c \
    "python /opt/opsany/cmdb/manage.py migrate --noinput >> ${SHELL_LOG} && python /opt/opsany/cmdb/manage.py createcachetable django_cache > /dev/null"
}

saas_control_update(){
    shell_log "======Update control======"
    # Modify configuration
    UPDATE_VERSION=$1
    CONTROL_SECRET_KEY=$(cat ${INSTALL_PATH}/conf/.control_secret_key)
    /bin/cp conf/opsany-saas/control/* ${INSTALL_PATH}/conf/opsany-saas/control/
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
    docker pull ${PAAS_DOCKER_REG}/opsany-saas-ce-control:${UPDATE_VERSION}
    docker stop opsany-saas-ce-control && docker rm opsany-saas-ce-control
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
       ${PAAS_DOCKER_REG}/opsany-saas-ce-control:${UPDATE_VERSION}
    
    # Django migrate
    docker exec -e BK_ENV="production" opsany-saas-ce-control /bin/sh -c \
    "python /opt/opsany/control/manage.py migrate --noinput >> ${SHELL_LOG} && python /opt/opsany/control/manage.py createcachetable django_cache > /dev/null"
}

saas_job_update(){
    shell_log "======Update job======"
    # Modify configuration
    UPDATE_VERSION=$1
    JOB_SECRET_KEY=$(cat ${INSTALL_PATH}/conf/.job_secret_key)
    /bin/cp conf/opsany-saas/job/* ${INSTALL_PATH}/conf/opsany-saas/job/
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

    # Starter container
    docker pull ${PAAS_DOCKER_REG}/opsany-saas-ce-job:${UPDATE_VERSION}
    docker stop opsany-saas-ce-job && docker rm opsany-saas-ce-job
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
       ${PAAS_DOCKER_REG}/opsany-saas-ce-job:${UPDATE_VERSION}
    
    # Django migrate
    docker exec -e BK_ENV="production" opsany-saas-ce-job /bin/sh -c \
    "python /opt/opsany/job/manage.py migrate --noinput >> ${SHELL_LOG} && python /opt/opsany/job/manage.py createcachetable django_cache > /dev/null"
}

saas_monitor_update(){
    shell_log "======Update monitor======"

    # Modify configuration
    UPDATE_VERSION=$1
    MONITOR_SECRET_KEY=$(cat ${INSTALL_PATH}/conf/.monitor_secret_key)
    /bin/cp conf/opsany-saas/monitor/* ${INSTALL_PATH}/conf/opsany-saas/monitor/
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
    docker pull ${PAAS_DOCKER_REG}/opsany-saas-ce-monitor:${UPDATE_VERSION}
    docker stop opsany-saas-ce-monitor && docker rm opsany-saas-ce-monitor
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
       ${PAAS_DOCKER_REG}/opsany-saas-ce-monitor:${UPDATE_VERSION}
    
    # Django migrate
    docker exec -e BK_ENV="production" opsany-saas-ce-monitor /bin/sh -c \
    "python /opt/opsany/monitor/manage.py migrate --noinput >> ${SHELL_LOG} && python /opt/opsany/monitor/manage.py createcachetable django_cache > /dev/null"
}

saas_cmp_update(){
    shell_log "======Update cmp======"

    #CMP Configure
    UPDATE_VERSION=$1
    CMP_SECRET_KEY=$(cat ${INSTALL_PATH}/conf/.cmp_secret_key)
    /bin/cp conf/opsany-saas/cmp/* ${INSTALL_PATH}/conf/opsany-saas/cmp/
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
    docker pull ${PAAS_DOCKER_REG}/opsany-saas-ce-cmp:${UPDATE_VERSION}
    docker stop opsany-saas-ce-cmp && docker rm opsany-saas-ce-cmp
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
       ${PAAS_DOCKER_REG}/opsany-saas-ce-cmp:${UPDATE_VERSION}
    
    # Django migrate
    docker exec -e BK_ENV="production" opsany-saas-ce-cmp /bin/sh -c \
    "python /opt/opsany/cmp/manage.py migrate --noinput >> ${SHELL_LOG} && python /opt/opsany/cmp/manage.py createcachetable django_cache > /dev/null"
}

saas_bastion_update(){
    shell_log "======Update bastion======"

    # Bastion Configure
    UPDATE_VERSION=$1
    BASTION_SECRET_KEY=$(cat ${INSTALL_PATH}/conf/.bastion_secret_key)
    /bin/cp conf/opsany-saas/bastion/* ${INSTALL_PATH}/conf/opsany-saas/bastion/
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
    docker pull ${PAAS_DOCKER_REG}/opsany-saas-ce-bastion:${UPDATE_VERSION}
    docker stop opsany-saas-ce-bastion && docker rm opsany-saas-ce-bastion
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
       ${PAAS_DOCKER_REG}/opsany-saas-ce-bastion:${UPDATE_VERSION}
    
    # Django migrate
    docker exec -e BK_ENV="production" opsany-saas-ce-bastion /bin/sh -c \
    "python /opt/opsany/bastion/manage.py migrate --noinput >> ${SHELL_LOG} && python /opt/opsany/bastion/manage.py createcachetable django_cache > /dev/null"
}

saas_devops_update(){
    shell_log "======Update devops======"

    # DevOps Configure
    UPDATE_VERSION=$1
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
    docker pull ${PAAS_DOCKER_REG}/opsany-saas-ce-devops:${UPDATE_VERSION}
    docker stop opsany-saas-ce-devops && docker rm opsany-saas-ce-devops
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
       ${PAAS_DOCKER_REG}/opsany-saas-ce-devops:${UPDATE_VERSION}
        # Django migrate
    docker exec -e BK_ENV="production" opsany-saas-ce-devops /bin/sh -c \
    "python /opt/opsany/devops/manage.py migrate --noinput >> ${SHELL_LOG} && python /opt/opsany/devops/manage.py createcachetable django_cache > /dev/null"
}

saas_pipeline_update(){
    shell_log "======Update pipeline======"
    # Modify configuration
    /bin/cp -r ./conf/opsany-saas/pipeline/* ${INSTALL_PATH}/conf/opsany-saas/pipeline/
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
    docker pull ${PAAS_DOCKER_REG}/opsany-saas-ce-pipeline:${UPDATE_VERSION}
    docker stop opsany-saas-ce-pipeline && docker rm opsany-saas-ce-pipeline
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
       ${PAAS_DOCKER_REG}/opsany-saas-ce-pipeline:${UPDATE_VERSION}
    
    # Django migrate
    docker exec -e BK_ENV="production" opsany-saas-ce-pipeline /bin/sh -c \
    "python /opt/opsany/pipeline/manage.py migrate --noinput >> ${SHELL_LOG} && python /opt/opsany/pipeline/manage.py createcachetable django_cache > /dev/null"
}

saas_deploy_update(){
    shell_log "======Update deploy======"
    # Modify configuration
    /bin/cp -r ./conf/opsany-saas/deploy/* ${INSTALL_PATH}/conf/opsany-saas/deploy/
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
    docker pull ${PAAS_DOCKER_REG}/opsany-saas-ce-deploy:${UPDATE_VERSION}
    docker stop opsany-saas-ce-deploy && docker rm opsany-saas-ce-deploy
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
       ${PAAS_DOCKER_REG}/opsany-saas-ce-deploy:${UPDATE_VERSION}
    
    # Django migrate
    docker exec -e BK_ENV="production" opsany-saas-ce-deploy /bin/sh -c \
    "python /opt/opsany/deploy/manage.py migrate --noinput >> ${SHELL_LOG} && python /opt/opsany/deploy/manage.py createcachetable django_cache > /dev/null"
}

saas_repo_update(){
    shell_log "======Update repo======"
    # Modify configuration
    /bin/cp -r ./conf/opsany-saas/repo/* ${INSTALL_PATH}/conf/opsany-saas/repo/
    REPO_SECRET_KEY=$(cat ${INSTALL_PATH}/conf/.repo_secret_key)
    # repo Configure
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
    docker pull ${PAAS_DOCKER_REG}/opsany-saas-ce-repo:2.1.3
    docker stop opsany-saas-ce-repo && docker rm opsany-saas-ce-repo
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
       ${PAAS_DOCKER_REG}/opsany-saas-ce-repo:2.1.3
    
    # Django migrate
    docker exec -e BK_ENV="production" opsany-saas-ce-repo /bin/sh -c \
    "python /opt/opsany/repo/manage.py migrate --noinput && python /opt/opsany/repo/manage.py createcachetable django_cache > /dev/null" >> ${SHELL_LOG}
}


saas_dashboard_update(){
    shell_log "======Update dashboard======"

    # Dashboard Configure
    UPDATE_VERSION=$1
    DASHBOARD_SECRET_KEY=$(cat ${INSTALL_PATH}/conf/.dashboard_secret_key)
    /bin/cp conf/opsany-saas/dashboard/* ${INSTALL_PATH}/conf/opsany-saas/dashboard/
    sed -i "s/DOMAIN_NAME/${DOMAIN_NAME}/g" ${INSTALL_PATH}/conf/opsany-saas/dashboard/dashboard-init.py
    sed -i "s/DASHBOARD_SECRET_KEY/${DASHBOARD_SECRET_KEY}/g" ${INSTALL_PATH}/conf/opsany-saas/dashboard/dashboard-init.py
    sed -i "s/MYSQL_SERVER_IP/${MYSQL_SERVER_IP}/g" ${INSTALL_PATH}/conf/opsany-saas/dashboard/dashboard-prod.py
    sed -i "s/MYSQL_SERVER_PORT/${MYSQL_SERVER_PORT}/g" ${INSTALL_PATH}/conf/opsany-saas/dashboard/dashboard-prod.py
    sed -i "s/MYSQL_OPSANY_DASHBOARD_PASSWORD/${MYSQL_OPSANY_DASHBOARD_PASSWORD}/g" ${INSTALL_PATH}/conf/opsany-saas/dashboard/dashboard-prod.py

    # Starter container
    docker pull ${PAAS_DOCKER_REG}/opsany-saas-ce-dashboard:${UPDATE_VERSION}
    docker stop opsany-saas-ce-dashboard && docker rm opsany-saas-ce-dashboard
    docker run -d --restart=always --name opsany-saas-ce-dashboard \
       -p 7010:80 \
       -v ${INSTALL_PATH}/conf/opsany-saas/dashboard/dashboard-supervisor.ini:/etc/supervisord.d/dashboard.ini \
       -v ${INSTALL_PATH}/conf/opsany-saas/dashboard/dashboard-uwsgi.ini:/opt/opsany/uwsgi/dashboard.ini \
       -v ${INSTALL_PATH}/conf/opsany-saas/dashboard/dashboard-init.py:/opt/opsany/dashboard/config/__init__.py \
       -v ${INSTALL_PATH}/conf/opsany-saas/dashboard/dashboard-prod.py:/opt/opsany/dashboard/config/prod.py \
       -v ${INSTALL_PATH}/conf/opsany-saas/dashboard/dashboard-nginx.conf:/etc/nginx/http.d/default.conf \
       -v ${INSTALL_PATH}/logs:/opt/opsany/logs \
       -v ${INSTALL_PATH}/uploads:/opt/opsany/uploads \
       -v /etc/localtime:/etc/localtime:ro \
       ${PAAS_DOCKER_REG}/opsany-saas-ce-dashboard:${UPDATE_VERSION}

    # Django migrate
    docker exec -e BK_ENV="production" opsany-saas-ce-dashboard /bin/sh -c \
    "python /opt/opsany/dashboard/manage.py migrate --noinput >> ${SHELL_LOG} && python /opt/opsany/dashboard/manage.py createcachetable django_cache > /dev/null"
}

# Main
main(){
    UPDATE_VERSION=$2
    case "$1" in
	base)
	    saas_rbac_update $2
	    saas_workbench_update $2
	    saas_cmdb_update $2
	    saas_control_update $2
	    saas_job_update $2
	    saas_cmp_update $2
	    saas_bastion_update $2
		;;
    paas)
        paas_update $2
        ;;
    login)
        login_update $2
        ;;
    esb)
        esb_update $2
        ;;
    websocket)
        websocket_update $2
        ;;
    appengine)
        appengine_update $2
        ;;
    proxy)
        proxy_update $2
        ;;
    rbac)
        saas_rbac_update $2
	    ;;
    workbench)
        saas_workbench_update $2
	    ;;
    cmdb)
        saas_cmdb_update $2
	    ;;
    control)
        saas_control_update $2
	    ;;
    job)
        saas_job_update $2
	    ;;
	monitor)
	    saas_monitor_update $2
	    ;;
    dashboard)
	    saas_dashboard_update $2
	    ;;
	devops)
	    saas_devops_update $2
	    ;;
    pipeline)
	    saas_pipeline_update $2
	    ;;
	deploy)
	    saas_deploy_update $2
	    ;;
	repo)
	    saas_repo_update $2
	    ;;
    cmp)
        saas_cmp_update $2
	    ;;
    bastion)
        saas_bastion_update $2
	    ;;
    websocket)
        websocket_update $2
        ;;
    all)
	    saas_rbac_update $2
	    saas_workbench_update $2
	    saas_cmdb_update $2
	    saas_control_update $2
	    saas_job_update $2
	    saas_cmp_update $2
	    saas_bastion_update $2
	    saas_dashboard_update $2
        saas_monitor_update $2
        saas_devops_update $2
        saas_pipeline_update $2
        saas_deploy_update $2
        saas_repo_update $2
        ;;
	help|*)
	    echo $"Usage: $0 {(paas|login|esb|appengine|proxy|websocket|rbac|workbench|cmdb|control|job|cmp|bastion|base|monitor|dashboard|devops|all|help) version}"
	    ;;
    esac
}

main $1 $2
