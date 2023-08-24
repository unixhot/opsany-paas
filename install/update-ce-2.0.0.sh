#!/bin/bash
#******************************************
# Author:       Jason Zhao
# Email:        zhaoshundong@opsany.com
# Organization: OpsAny https://www.opsany.com/
# Description:  OpsAny SAAS Community Edition 2.0.0 Update Script
#******************************************

# Data/Time Variables
CTIME=$(date "+%Y-%m-%d-%H-%M")

# Shell Envionment Variables
CDIR=$(pwd)
SHELL_NAME="update-2.0.0.sh"
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
    echo 'MYSQL_SERVER_PORT="3306"' >> install.config
    echo 'MONGO_SERVER_PORT="27017"' >> install.config
    echo 'REDIS_SERVER_PORT="6379"' >> install.config
    grep '^[A-Z]' install.config > install.env
    source ./install.env && rm -f install.env
    if [ -z "$ADMIN_PASSWORD" ];then
        source ${INSTALL_PATH}/conf/.passwd_env
    fi
fi

# Install initialization
update_init(){
    shell_log "======Update init======"
    #SaaS Log Directory
    mkdir -p ${INSTALL_PATH}/logs/{rbac,workbench,cmdb,control,job,monitor,cmp,bastion,dashboard,devops}
    /bin/cp -r conf/opsany-saas/ ${INSTALL_PATH}/conf/
    echo 'a5168d38-fc09-11ea-a87d-00163e105ceb' > ${INSTALL_PATH}/conf/.rbac_secret_key
    echo 'cc6e99fc-fc09-11ea-b63c-00163e105ceb' > ${INSTALL_PATH}/conf/.workbench_secret_key
    echo 'eee5b34e-fc09-11ea-9e6a-00163e105ceb' > ${INSTALL_PATH}/conf/.cmdb_secret_key
    echo '099f6e6f-9ad8-43d7-b487-7f655519598d' > ${INSTALL_PATH}/conf/.control_secret_key
    echo '66f8cd80-fc0a-11ea-90e5-00163e105ceb' > ${INSTALL_PATH}/conf/.job_secret_key
    echo '5e003cfa-1b44-11eb-876c-00163e105ceb' > ${INSTALL_PATH}/conf/.monitor_secret_key
    echo '64046956-5171-11eb-a042-00163e105ceb' > ${INSTALL_PATH}/conf/.cmp_secret_key
    echo '73a828d2-0cc1-11ec-bea7-00163e105ceb' > ${INSTALL_PATH}/conf/.bastion_secret_key
    echo 'f64f3fae-b335-11eb-a88b-00163e105ceb' > ${INSTALL_PATH}/conf/.devops_secret_key
    echo '9efb7e72-f2e3-11ec-90d5-00163e105ceb' > ${INSTALL_PATH}/conf/.dashboard_secret_key
}

saas_login_update(){
    shell_log "======Update Login======"
    /bin/cp conf/settings_production.py.login ${INSTALL_PATH}/conf/
    RBAC_SECRET_KEY=$(cat ${INSTALL_PATH}/conf/.rbac_secret_key)
    sed -i "s/RBAC_SECRET_KEY/${RBAC_SECRET_KEY}/g" ${INSTALL_PATH}/conf/settings_production.py.login
    sed -i "s/DOMAIN_NAME/${DOMAIN_NAME}/g" ${INSTALL_PATH}/conf/settings_production.py.login
    sed -i "s/LOCAL_IP/${LOCAL_IP}/g" ${INSTALL_PATH}/conf/settings_production.py.login
    sed -i "s/MYSQL_SERVER_IP/${MYSQL_SERVER_IP}/g" ${INSTALL_PATH}/conf/settings_production.py.login
    sed -i "s/MYSQL_OPSANY_PASSWORD/${MYSQL_OPSANY_PASSWORD}/g" ${INSTALL_PATH}/conf/settings_production.py.login

    docker stop opsany-paas-login && docker rm opsany-paas-login
    docker run -d --restart=always --name opsany-paas-login \
    -p 8003:8003 -v ${INSTALL_PATH}/logs:/opt/opsany/logs \
    -v ${INSTALL_PATH}/conf/settings_production.py.login:/opt/opsany/paas/login/conf/settings_production.py \
    -v /etc/localtime:/etc/localtime:ro \
    ${PAAS_DOCKER_REG}/opsany-paas-login:v3.2.22
}

saas_esb_update(){
    shell_log "======Update ESB======"
    docker stop opsany-paas-esb && docker rm opsany-paas-esb
    docker run -d --restart=always --name opsany-paas-esb \
    -p 8002:8002 -v ${INSTALL_PATH}/logs:/opt/opsany/logs \
    -v ${INSTALL_PATH}/esb/apis:/opt/opsany/paas/esb/components/generic/apis \
    -v ${INSTALL_PATH}/conf/settings_production.py.esb:/opt/opsany/paas/esb/configs/default.py \
    -v /etc/localtime:/etc/localtime:ro \
    ${PAAS_DOCKER_REG}/opsany-paas-esb:v3.2.7
}

saas_websocket_update(){
    shell_log "======Update Websocket======"
    BASTION_SECRET_KEY=$(cat ${INSTALL_PATH}/conf/.bastion_secret_key)
    /bin/cp conf/settings_production.py.websocket ${INSTALL_PATH}/conf/
    /bin/cp conf/settings_production.py.websocket.init ${INSTALL_PATH}/conf/
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
    ${PAAS_DOCKER_REG}/opsany-paas-websocket:2.0.0
}

openresty_update(){
    shell_log "======Update Openresty======"
    /bin/cp conf/nginx-conf.d/opsany_paas.conf ${INSTALL_PATH}/conf/nginx-conf.d/
    /bin/cp conf/nginx-conf.d/opsany_proxy.conf ${INSTALL_PATH}/conf/nginx-conf.d/
    sed -i "s/DOMAIN_NAME/${DOMAIN_NAME}/g" ${INSTALL_PATH}/conf/nginx-conf.d/opsany_paas.conf
    sed -i "s/LOCAL_IP/${LOCAL_IP}/g" ${INSTALL_PATH}/conf/nginx-conf.d/opsany_paas.conf
    sed -i "s/DOMAIN_NAME/${DOMAIN_NAME}/g" ${INSTALL_PATH}/conf/nginx-conf.d/opsany_proxy.conf
    sed -i "s/LOCAL_IP/${LOCAL_IP}/g" ${INSTALL_PATH}/conf/nginx-conf.d/opsany_proxy.conf
    mv ${INSTALL_PATH}/conf/nginx-conf.d/nginx_paas.conf /tmp/
    mv ${INSTALL_PATH}/conf/nginx-conf.d/nginx_proxy.conf /tmp/
    docker restart opsany-openresty
}
    

# Start Proxy
proxy_update(){
    shell_log "======Update Proxy======"
    # Proxy config
    CONTROL_SECRET_KEY=$(cat ${INSTALL_PATH}/conf/.control_secret_key)
    /bin/cp conf/proxy/settings_production.py.proxy ${INSTALL_PATH}/conf/proxy/
    /bin/cp conf/proxy/nginx-conf.d/nginx_proxy.conf ${INSTALL_PATH}/conf/proxy/nginx-conf.d/
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
    sed -i "s/CONTROL_SECRET_KEY_PROXY/${CONTROL_SECRET_KEY_PROXY}/g" ${INSTALL_PATH}/conf/proxy/settings_production.py.proxy
    /bin/cp ../saas/invscript_proxy.py ${INSTALL_PATH}/conf/proxy/
    sed -i "s/LOCALHOST/${MYSQL_SERVER_IP}/g" ${INSTALL_PATH}/conf/proxy/invscript_proxy.py
    sed -i "s/PROXY_PASSWORD/${MYSQL_OPSANY_PASSWORD}/g" ${INSTALL_PATH}/conf/proxy/invscript_proxy.py
    sed -i "s/CONTROL_SECRET_KEY/${CONTROL_SECRET_KEY}/g" ${INSTALL_PATH}/conf/proxy/invscript_proxy.py
    chmod +x ${INSTALL_PATH}/conf/proxy/invscript_proxy.py

    shell_log "======Start Proxy======"
    docker stop opsany-proxy && docker rm opsany-proxy
    #docker stop opsany-paas-proxy && docker rm opsany-paas-proxy
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
        ${PAAS_DOCKER_REG}/opsany-paas-proxy:2.0.0

    shell_log "======OpsAny Proxy Initialize======"
    # OpsAny Database Init
    docker exec -e OPS_ANY_ENV=production \
        opsany-paas-proxy /bin/sh -c "/usr/local/bin/python3 /opt/opsany-proxy/manage.py migrate >> ${SHELL_LOG}"
}

# SaaS Deploy

saas_rbac_deploy(){
    shell_log "======Start RBAC======"

    # Modify configuration
    RBAC_SECRET_KEY=$(cat ${INSTALL_PATH}/conf/.rbac_secret_key)
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
    docker pull ${PAAS_DOCKER_REG}/opsany-saas-ce-rbac:2.0.0
    #docker stop opsany-saas-ce-rbac && docker rm opsany-saas-ce-rbac
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
       ${PAAS_DOCKER_REG}/opsany-saas-ce-rbac:2.0.0
    
    # Django migrate
    docker exec -e BK_ENV="production" opsany-saas-ce-rbac /bin/sh -c \
    "python /opt/opsany/rbac/manage.py migrate --noinput >> ${SHELL_LOG} && python /opt/opsany/rbac/manage.py createcachetable django_cache > /dev/null"
}

saas_workbench_deploy(){
    shell_log "======Start workbench======"

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

    # Starter container
    docker pull ${PAAS_DOCKER_REG}/opsany-saas-ce-workbench:2.0.0
    #docker stop opsany-saas-ce-workbench && docker rm opsany-saas-ce-workbench
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
       ${PAAS_DOCKER_REG}/opsany-saas-ce-workbench:2.0.0
    # Django migrate
    docker exec -e BK_ENV="production" opsany-saas-ce-workbench /bin/sh -c \
    "python /opt/opsany/workbench/manage.py migrate --noinput >> ${SHELL_LOG} >> ${SHELL_LOG} && python /opt/opsany/workbench/manage.py createcachetable django_cache > /dev/null"
}

saas_cmdb_deploy(){
    shell_log "======Start cmdb======"

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

    # Starter container
    docker pull ${PAAS_DOCKER_REG}/opsany-saas-ce-cmdb:2.0.0
    #docker stop opsany-saas-ce-cmdb && docker rm opsany-saas-ce-cmdb
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
       ${PAAS_DOCKER_REG}/opsany-saas-ce-cmdb:2.0.0
    
    # Django migrate
    docker exec -e BK_ENV="production" opsany-saas-ce-cmdb /bin/sh -c \
    "python /opt/opsany/cmdb/manage.py migrate --noinput >> ${SHELL_LOG} && python /opt/opsany/cmdb/manage.py createcachetable django_cache > /dev/null"
}

saas_control_deploy(){
    shell_log "======Start control======"
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

    # Starter container
    docker pull ${PAAS_DOCKER_REG}/opsany-saas-ce-control:2.0.0
    #docker stop opsany-saas-ce-control && docker rm opsany-saas-ce-control
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
       ${PAAS_DOCKER_REG}/opsany-saas-ce-control:2.0.0
    
    # Django migrate
    docker exec -e BK_ENV="production" opsany-saas-ce-control /bin/sh -c \
    "python /opt/opsany/control/manage.py migrate --noinput >> ${SHELL_LOG} && python /opt/opsany/control/manage.py createcachetable django_cache > /dev/null"
}

saas_job_deploy(){
    shell_log "======Start job======"

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

    # Starter container
    docker pull ${PAAS_DOCKER_REG}/opsany-saas-ce-job:2.0.0
    #docker stop opsany-saas-ce-job && docker rm opsany-saas-ce-job
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
       ${PAAS_DOCKER_REG}/opsany-saas-ce-job:2.0.0
    
    # Django migrate
    docker exec -e BK_ENV="production" opsany-saas-ce-job /bin/sh -c \
    "python /opt/opsany/job/manage.py migrate --noinput >> ${SHELL_LOG} && python /opt/opsany/job/manage.py createcachetable django_cache > /dev/null"
}

saas_monitor_deploy(){
    shell_log "======Start monitor======"

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
    docker pull ${PAAS_DOCKER_REG}/opsany-saas-ce-monitor:2.0.0
    #docker stop opsany-saas-ce-monitor && docker rm opsany-saas-ce-monitor
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
       ${PAAS_DOCKER_REG}/opsany-saas-ce-monitor:2.0.0
    
    # Django migrate
    docker exec -e BK_ENV="production" opsany-saas-ce-monitor /bin/sh -c \
    "python /opt/opsany/monitor/manage.py migrate --noinput >> ${SHELL_LOG} && python /opt/opsany/monitor/manage.py createcachetable django_cache > /dev/null"
}

saas_cmp_deploy(){
    shell_log "======Start cmp======"

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
    docker pull ${PAAS_DOCKER_REG}/opsany-saas-ce-cmp:2.0.0
    #docker stop opsany-saas-ce-cmp && docker rm opsany-saas-ce-cmp
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
       ${PAAS_DOCKER_REG}/opsany-saas-ce-cmp:2.0.0
    
    # Django migrate
    docker exec -e BK_ENV="production" opsany-saas-ce-cmp /bin/sh -c \
    "python /opt/opsany/cmp/manage.py migrate --noinput >> ${SHELL_LOG} && python /opt/opsany/cmp/manage.py createcachetable django_cache > /dev/null"
}

saas_bastion_deploy(){
    shell_log "======Start bastion======"

    # Bastion Configure
    BASTION_SECRET_KEY=$(cat ${INSTALL_PATH}/conf/.bastion_secret_key)
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
    docker pull ${PAAS_DOCKER_REG}/opsany-saas-ce-bastion:2.0.0
    #docker stop opsany-saas-ce-bastion && docker rm opsany-saas-ce-bastion
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
       ${PAAS_DOCKER_REG}/opsany-saas-ce-bastion:2.0.0
    
    # Django migrate
    docker exec -e BK_ENV="production" opsany-saas-ce-bastion /bin/sh -c \
    "python /opt/opsany/bastion/manage.py migrate --noinput >> ${SHELL_LOG} && python /opt/opsany/bastion/manage.py createcachetable django_cache > /dev/null"
}

saas_devops_deploy(){
    shell_log "======Start devops======"

    # DevOps Configure
    DEVOPS_SECRET_KEY=$(cat ${INSTALL_PATH}/conf/.devops_secret_key)
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
    docker pull ${PAAS_DOCKER_REG}/opsany-saas-ce-devops:2.0.0
    #docker stop opsany-saas-ce-devops && docker rm opsany-saas-ce-devops
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
       ${PAAS_DOCKER_REG}/opsany-saas-ce-devops:2.0.0
        # Django migrate
    docker exec -e BK_ENV="production" opsany-saas-ce-devops /bin/sh -c \
    "python /opt/opsany/devops/manage.py migrate --noinput >> ${SHELL_LOG} && python /opt/opsany/devops/manage.py createcachetable django_cache > /dev/null"
}

saas_dashboard_deploy(){
    shell_log "======Start dashboard======"
    
    # Dashboard Configure
    DASHBOARD_SECRET_KEY=$(cat ${INSTALL_PATH}/conf/.dashboard_secret_key)
    sed -i "s/DOMAIN_NAME/${DOMAIN_NAME}/g" ${INSTALL_PATH}/conf/opsany-saas/dashboard/dashboard-init.py
    sed -i "s/DASHBOARD_SECRET_KEY/${DASHBOARD_SECRET_KEY}/g" ${INSTALL_PATH}/conf/opsany-saas/dashboard/dashboard-init.py
    sed -i "s/MYSQL_SERVER_IP/${MYSQL_SERVER_IP}/g" ${INSTALL_PATH}/conf/opsany-saas/dashboard/dashboard-prod.py
    sed -i "s/MYSQL_SERVER_PORT/${MYSQL_SERVER_PORT}/g" ${INSTALL_PATH}/conf/opsany-saas/dashboard/dashboard-prod.py
    sed -i "s/MYSQL_OPSANY_DASHBOARD_PASSWORD/${MYSQL_OPSANY_DASHBOARD_PASSWORD}/g" ${INSTALL_PATH}/conf/opsany-saas/dashboard/dashboard-prod.py

    # Starter container
    docker pull ${PAAS_DOCKER_REG}/opsany-saas-ce-dashboard:2.0.0
    #docker stop opsany-saas-ce-dashboard && docker rm opsany-saas-ce-dashboard
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
       ${PAAS_DOCKER_REG}/opsany-saas-ce-dashboard:2.0.0

    # Django migrate
    docker exec -e BK_ENV="production" opsany-saas-ce-dashboard /bin/sh -c \
    "python /opt/opsany/dashboard/manage.py migrate --noinput >> ${SHELL_LOG} && python /opt/opsany/dashboard/manage.py createcachetable django_cache > /dev/null"
}

saas_base_init(){
    shell_log "======OpsAny User Initialize======"
    sleep 3
    python3 ../saas/sync-user-script.py --domain https://${DOMAIN_NAME} --paas_username admin --paas_password ${ADMIN_PASSWORD} --app_code workbench cmdb control job cmp bastion
    shell_warning_log "======OpsAny: Make Ops Perfect======" 
}

saas_monitor_init(){
    python3 ../saas/sync-user-script.py --domain https://${DOMAIN_NAME} --paas_username admin --paas_password ${ADMIN_PASSWORD} --app_code monitor dashboard
}

saas_devops_init(){
    python3 ../saas/sync-user-script.py --domain https://${DOMAIN_NAME} --paas_username admin --paas_password ${ADMIN_PASSWORD} --app_code monitor devops
}

# Main
main(){
    case "$1" in
    login)
        saas_login_update
        ;;
    esb)
        saas_esb_update
        ;;
    websocket)
        saas_websocket_update
        ;;
	base)
        update_init
        saas_login_update
        saas_esb_update
        saas_websocket_update
        openresty_update
        proxy_update
	    saas_rbac_deploy
	    saas_workbench_deploy
	    saas_cmdb_deploy
	    saas_control_deploy
	    saas_job_deploy
	    saas_cmp_deploy
	    saas_bastion_deploy
        saas_base_init
		;;
	monitor)
        saas_dashboard_deploy
	    saas_monitor_deploy
        saas_monitor_init
	    ;;
	devops)
	    saas_devops_deploy
        saas_devops_init
	    ;;
    all)
        update_init
        saas_login_update
        saas_esb_update
        saas_websocket_update
        openresty_update
        proxy_update
	    saas_rbac_deploy
	    saas_workbench_deploy
	    saas_cmdb_deploy
	    saas_control_deploy
	    saas_job_deploy
	    saas_cmp_deploy
	    saas_bastion_deploy
	    saas_dashboard_deploy
        saas_monitor_deploy
        saas_devops_deploy
        saas_base_init
        saas_monitor_init
        saas_devops_init
        ;;
	help|*)
	    echo $"Usage: $0 {base|monitor|devops|all|help}"
	    ;;
    esac
}

main $1 
