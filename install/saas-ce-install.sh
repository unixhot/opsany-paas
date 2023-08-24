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
fi

# Install initialization
install_init(){
    #SaaS Log Directory
    mkdir -p ${INSTALL_PATH}/logs/{rbac,workbench,cmdb,control,job,monitor,cmp,bastion,dashboard,devops}
}

# Start Proxy
proxy_install(){
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
    sed -i "s/RABBIT_SERVER_IP/${RABBIT_SERVER_IP}/g" ${INSTALL_PATH}/conf/proxy/settings_production.py.proxy
    sed -i "s/RABBITMQ_DEFAULT_USER/${RABBITMQ_DEFAULT_USER}/g" ${INSTALL_PATH}/conf/proxy/settings_production.py.proxy
    sed -i "s/RABBITMQ_DEFAULT_PASS/${RABBITMQ_DEFAULT_PASS}/g" ${INSTALL_PATH}/conf/proxy/settings_production.py.proxy
    sed -i "s/CONTROL_SECRET_KEY_PROXY/${CONTROL_SECRET_KEY_PROXY}/g" ${INSTALL_PATH}/conf/proxy/settings_production.py.proxy

    # For Ansible
    
    cp ../saas/invscript_proxy.py ${INSTALL_PATH}/conf/proxy/
    sed -i "s/LOCALHOST/${MYSQL_SERVER_IP}/g" ${INSTALL_PATH}/conf/proxy/invscript_proxy.py
    sed -i "s/PROXY_PASSWORD/${MYSQL_OPSANY_PASSWORD}/g" ${INSTALL_PATH}/conf/proxy/invscript_proxy.py
    sed -i "s/CONTROL_SECRET_KEY/${CONTROL_SECRET_KEY}/g" ${INSTALL_PATH}/conf/proxy/invscript_proxy.py
    chmod +x ${INSTALL_PATH}/conf/proxy/invscript_proxy.py

    shell_log "======Start Proxy======"
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
        opsany-paas-proxy /bin/sh -c "/usr/local/bin/python3 /opt/opsany-proxy/manage.py migrate --noinput" >> ${SHELL_LOG}
}

# MonogDB Initialize
mongodb_init(){
    shell_log "======MongoDB Initialize======"
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
                opsany-base-mongodb /bin/bash -c "/usr/bin/mongo -u $MONGO_INITDB_ROOT_USERNAME -p $MONGO_INITDB_ROOT_PASSWORD /opt/mongodb_init.js" >> ${SHELL_LOG}

    docker cp -a init/cmdb-init opsany-base-mongodb:/opt/
    docker exec -e MONGO_CMDB_PASSWORD=${MONGO_CMDB_PASSWORD} \
                opsany-base-mongodb /bin/bash -c "mongoimport -u cmdb -p ${MONGO_CMDB_PASSWORD} --db cmdb --drop --collection field_group < /opt/cmdb-init/field_group.json" >> ${SHELL_LOG}
    docker exec -e MONGO_CMDB_PASSWORD=${MONGO_CMDB_PASSWORD} \
                opsany-base-mongodb /bin/bash -c "mongoimport -u cmdb -p ${MONGO_CMDB_PASSWORD} --db cmdb --drop --collection icon_model < /opt/cmdb-init/icon_model.json" >> ${SHELL_LOG}
    docker exec -e MONGO_CMDB_PASSWORD=${MONGO_CMDB_PASSWORD} \
                opsany-base-mongodb /bin/bash -c "mongoimport -u cmdb -p ${MONGO_CMDB_PASSWORD} --db cmdb --drop --collection link_relationship_model < /opt/cmdb-init/link_relationship_model.json"
        docker exec -e MONGO_CMDB_PASSWORD=${MONGO_CMDB_PASSWORD} \
                opsany-base-mongodb /bin/bash -c "mongoimport -u cmdb -p ${MONGO_CMDB_PASSWORD} --db cmdb --drop --collection model_group < /opt/cmdb-init/model_group.json" >> ${SHELL_LOG}
    docker exec -e MONGO_CMDB_PASSWORD=${MONGO_CMDB_PASSWORD} \
                opsany-base-mongodb /bin/bash -c "mongoimport -u cmdb -p ${MONGO_CMDB_PASSWORD} --db cmdb --drop --collection model_field < /opt/cmdb-init/model_field.json" >> ${SHELL_LOG}
    docker exec -e MONGO_CMDB_PASSWORD=${MONGO_CMDB_PASSWORD} \
                opsany-base-mongodb /bin/bash -c "mongoimport -u cmdb -p ${MONGO_CMDB_PASSWORD} --db cmdb --drop --collection model_info < /opt/cmdb-init/model_info.json" >> ${SHELL_LOG}

    shell_log "======MongoDB Initialize End======"
}

# SaaS Deploy

saas_rbac_deploy(){
    shell_log "======Start RBAC======"
    # Database 
    mysql -h "${MYSQL_SERVER_IP}" -u root -p"${MYSQL_ROOT_PASSWORD}" -e "create database rbac DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;"
    mysql -h "${MYSQL_SERVER_IP}" -u root -p"${MYSQL_ROOT_PASSWORD}" -e "grant all on rbac.* to rbac@'%' identified by "\"${MYSQL_OPSANY_RBAC_PASSWORD}\"";"
    mysql -h "${MYSQL_SERVER_IP}" -u root -p"${MYSQL_ROOT_PASSWORD}" -e "grant all on rbac.* to opsany@'%' identified by "\"${MYSQL_OPSANY_PASSWORD}\"";"

    # Register rbac
    RBAC_SECRET_KEY=$(cat ${INSTALL_PATH}/conf/.rbac_secret_key)
    python3 ../saas/register_online_saas.py --paas_domain https://${DOMAIN_NAME} --username admin --password ${ADMIN_PASSWORD} --saas_app_code rbac --saas_app_name 统一权限 --saas_app_version 2.0.0 --saas_app_secret_key ${RBAC_SECRET_KEY}

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
    docker pull ${PAAS_DOCKER_REG}/opsany-saas-ce-rbac:2.0.0
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
    "python /opt/opsany/rbac/manage.py migrate --noinput && python /opt/opsany/rbac/manage.py createcachetable django_cache > /dev/null" >> ${SHELL_LOG}
}

saas_workbench_deploy(){
    shell_log "======Start workbench======"
    #workbench
    mysql -h "${MYSQL_SERVER_IP}" -u root -p"${MYSQL_ROOT_PASSWORD}" -e "create database workbench DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;"
    mysql -h "${MYSQL_SERVER_IP}" -u root -p"${MYSQL_ROOT_PASSWORD}" -e "grant all on workbench.* to workbench@'%' identified by "\"${MYSQL_OPSANY_WORKBENCH_PASSWORD}\"";"
    mysql -h "${MYSQL_SERVER_IP}" -u root -p"${MYSQL_ROOT_PASSWORD}" -e "grant all on workbench.* to opsany@'%' identified by "\"${MYSQL_OPSANY_PASSWORD}\"";"

    # Register workbench
    WORKBENCH_SECRET_KEY=$(uuid -v4)
    echo $WORKBENCH_SECRET_KEY > ${INSTALL_PATH}/conf/.workbench_secret_key
    python3 ../saas/register_online_saas.py --paas_domain https://${DOMAIN_NAME} --username admin --password ${ADMIN_PASSWORD} --saas_app_code workbench --saas_app_name 工作台 --saas_app_version 2.0.0 --saas_app_secret_key ${WORKBENCH_SECRET_KEY}

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
    docker pull ${PAAS_DOCKER_REG}/opsany-saas-ce-workbench:2.0.0
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
    "python /opt/opsany/workbench/manage.py migrate --noinput && python /opt/opsany/workbench/manage.py createcachetable django_cache > /dev/null" >> ${SHELL_LOG}
}

saas_cmdb_deploy(){
    shell_log "======Start cmdb======"
    #cmdb
    mysql -h "${MYSQL_SERVER_IP}" -u root -p"${MYSQL_ROOT_PASSWORD}" -e "create database cmdb DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;"
    mysql -h "${MYSQL_SERVER_IP}" -u root -p"${MYSQL_ROOT_PASSWORD}" -e "grant all on cmdb.* to cmdb@'%' identified by "\"${MYSQL_OPSANY_CMDB_PASSWORD}\"";"
    mysql -h "${MYSQL_SERVER_IP}" -u root -p"${MYSQL_ROOT_PASSWORD}" -e "grant all on cmdb.* to opsany@'%' identified by "\"${MYSQL_OPSANY_PASSWORD}\"";"

    # Register cmdb
    CMDB_SECRET_KEY=$(uuid -v4)
    echo $CMDB_SECRET_KEY > ${INSTALL_PATH}/conf/.cmdb_secret_key
    python3 ../saas/register_online_saas.py --paas_domain https://${DOMAIN_NAME} --username admin --password ${ADMIN_PASSWORD} --saas_app_code cmdb --saas_app_name 资源平台 --saas_app_version 2.0.0 --saas_app_secret_key ${CMDB_SECRET_KEY}

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
    docker pull ${PAAS_DOCKER_REG}/opsany-saas-ce-cmdb:2.0.0
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
    "python /opt/opsany/cmdb/manage.py migrate --noinput && python /opt/opsany/cmdb/manage.py createcachetable django_cache > /dev/null" >> ${SHELL_LOG}
}

saas_control_deploy(){
    shell_log "======Start control======"
    #control
    mysql -h "${MYSQL_SERVER_IP}" -u root -p"${MYSQL_ROOT_PASSWORD}" -e "create database control DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;"
    mysql -h "${MYSQL_SERVER_IP}" -u root -p"${MYSQL_ROOT_PASSWORD}" -e "grant all on control.* to control@'%' identified by "\"${MYSQL_OPSANY_CONTROL_PASSWORD}\"";"
    mysql -h "${MYSQL_SERVER_IP}" -u root -p"${MYSQL_ROOT_PASSWORD}" -e "grant all on control.* to opsany@'%' identified by "\"${MYSQL_OPSANY_PASSWORD}\"";"

    # Register control 
    python3 ../saas/register_online_saas.py --paas_domain https://${DOMAIN_NAME} --username admin --password ${ADMIN_PASSWORD} --saas_app_code control --saas_app_name 管控平台 --saas_app_version 2.0.0 --saas_app_secret_key ${CONTROL_SECRET_KEY}

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
    docker pull ${PAAS_DOCKER_REG}/opsany-saas-ce-control:2.0.0
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
    "python /opt/opsany/control/manage.py migrate --noinput && python /opt/opsany/control/manage.py createcachetable django_cache > /dev/null" >> ${SHELL_LOG}
}

saas_job_deploy(){
    shell_log "======Start job======"
    #job
    mysql -h "${MYSQL_SERVER_IP}" -u root -p"${MYSQL_ROOT_PASSWORD}" -e "create database job DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;"
    mysql -h "${MYSQL_SERVER_IP}" -u root -p"${MYSQL_ROOT_PASSWORD}" -e "grant all on job.* to job@'%' identified by "\"${MYSQL_OPSANY_JOB_PASSWORD}\"";"
    mysql -h "${MYSQL_SERVER_IP}" -u root -p"${MYSQL_ROOT_PASSWORD}" -e "grant all on job.* to opsany@'%' identified by "\"${MYSQL_OPSANY_PASSWORD}\"";"

    # Register job
    JOB_SECRET_KEY=$(uuid -v4)
    echo $JOB_SECRET_KEY > ${INSTALL_PATH}/conf/.job_secret_key
    python3 ../saas/register_online_saas.py --paas_domain https://${DOMAIN_NAME} --username admin --password ${ADMIN_PASSWORD} --saas_app_code job --saas_app_name 作业平台 --saas_app_version 2.0.0 --saas_app_secret_key ${JOB_SECRET_KEY}

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

    # Starter container
    docker pull ${PAAS_DOCKER_REG}/opsany-saas-ce-job:2.0.0
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
    "python /opt/opsany/job/manage.py migrate --noinput && python /opt/opsany/job/manage.py createcachetable django_cache > /dev/null" >> ${SHELL_LOG}
}

saas_monitor_deploy(){
    # Grafana
    shell_log "======Start Grafana======"
    docker run -d --restart=always --name opsany-base-grafana --user root \
    -v ${INSTALL_PATH}/conf/grafana/grafana.ini:/etc/grafana/grafana.ini \
    -v ${INSTALL_PATH}/conf/grafana/grafana.key:/etc/grafana/grafana.key \
    -v ${INSTALL_PATH}/conf/grafana/grafana.pem:/etc/grafana/grafana.pem \
    -v /etc/localtime:/etc/localtime:ro \
    -v ${INSTALL_PATH}/grafana-volume/data:/var/lib/grafana \
    -p 8007:3000 \
    ${PAAS_DOCKER_REG}/opsany-grafana:9.0.2

    shell_log "======Start monitor======"
    #monitor
    mysql -h "${MYSQL_SERVER_IP}" -u root -p"${MYSQL_ROOT_PASSWORD}" -e "create database monitor DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;"
    mysql -h "${MYSQL_SERVER_IP}" -u root -p"${MYSQL_ROOT_PASSWORD}" -e "grant all on monitor.* to monitor@'%' identified by "\"${MYSQL_OPSANY_MONITOR_PASSWORD}\"";"
    mysql -h "${MYSQL_SERVER_IP}" -u root -p"${MYSQL_ROOT_PASSWORD}" -e "grant all on monitor.* to opsany@'%' identified by "\"${MYSQL_OPSANY_PASSWORD}\"";" 

    #monitor
    sed -i "s/DOMAIN_NAME/$DOMAIN_NAME/g" ${INSTALL_PATH}/esb/apis/monitor/toolkit/configs.py
    sed -i "s#/t/monitor#/o/monitor#g" ${INSTALL_PATH}/esb/apis/monitor/toolkit/tools.py
 
    # Register monitor
    if [ -f ${INSTALL_PATH}/conf/.passwd_env ];then
        source ${INSTALL_PATH}/conf/.passwd_env
    fi
    MONITOR_SECRET_KEY=$(uuid -v4)
    echo $MONITOR_SECRET_KEY > ${INSTALL_PATH}/conf/.monitor_secret_key

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
    "python /opt/opsany/monitor/manage.py migrate --noinput && python /opt/opsany/monitor/manage.py createcachetable django_cache > /dev/null" >> ${SHELL_LOG}
    sleep 5
    python3 ../saas/register_online_saas.py --paas_domain https://${DOMAIN_NAME} --username admin --password ${ADMIN_PASSWORD} --saas_app_code monitor --saas_app_name 基础监控 --saas_app_version 2.0.0 --saas_app_secret_key ${MONITOR_SECRET_KEY}
}

saas_cmp_deploy(){
    shell_log "======Start cmp======"
    #cmp
    mysql -h "${MYSQL_SERVER_IP}" -u root -p"${MYSQL_ROOT_PASSWORD}" -e "create database cmp DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;"
    mysql -h "${MYSQL_SERVER_IP}" -u root -p"${MYSQL_ROOT_PASSWORD}" -e "grant all on cmp.* to cmp@'%' identified by "\"${MYSQL_OPSANY_CMP_PASSWORD}\"";"
    mysql -h "${MYSQL_SERVER_IP}" -u root -p"${MYSQL_ROOT_PASSWORD}" -e "grant all on cmp.* to opsany@'%' identified by "\"${MYSQL_OPSANY_PASSWORD}\"";" 

    #cmp
    sed -i "s/DOMAIN_NAME/$DOMAIN_NAME/g" ${INSTALL_PATH}/esb/apis/cmp/toolkit/configs.py
    sed -i "s#/t/cmp#/o/cmp#g" ${INSTALL_PATH}/esb/apis/cmp/toolkit/tools.py

    # Register cmp
    CMP_SECRET_KEY=$(uuid -v4)
    echo $CMP_SECRET_KEY > ${INSTALL_PATH}/conf/.cmp_secret_key
    python3 ../saas/register_online_saas.py --paas_domain https://${DOMAIN_NAME} --username admin --password ${ADMIN_PASSWORD} --saas_app_code cmp --saas_app_name 云管平台 --saas_app_version 2.0.0 --saas_app_secret_key ${CMP_SECRET_KEY}

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
    "python /opt/opsany/cmp/manage.py migrate --noinput && python /opt/opsany/cmp/manage.py createcachetable django_cache > /dev/null" >> ${SHELL_LOG}
}

saas_bastion_deploy(){
    shell_log "======Start bastion======"
    #bastion
    mysql -h "${MYSQL_SERVER_IP}" -u root -p"${MYSQL_ROOT_PASSWORD}" -e "create database bastion DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;"
    mysql -h "${MYSQL_SERVER_IP}" -u root -p"${MYSQL_ROOT_PASSWORD}" -e "grant all on bastion.* to bastion@'%' identified by "\"${MYSQL_OPSANY_BASTION_PASSWORD}\"";"
    mysql -h "${MYSQL_SERVER_IP}" -u root -p"${MYSQL_ROOT_PASSWORD}" -e "grant all on bastion.* to opsany@'%' identified by "\"${MYSQL_OPSANY_PASSWORD}\"";" 

    #bastion
    sed -i "s/DOMAIN_NAME/$DOMAIN_NAME/g" ${INSTALL_PATH}/esb/apis/bastion/toolkit/configs.py
    sed -i "s#/t/bastion#/o/bastion#g" ${INSTALL_PATH}/esb/apis/bastion/toolkit/configs.py

    # Register bastion
    BASTION_SECRET_KEY=$(cat ${INSTALL_PATH}/conf/.bastion_secret_key)
    python3 ../saas/register_online_saas.py --paas_domain https://${DOMAIN_NAME} --username admin --password ${ADMIN_PASSWORD} --saas_app_code bastion --saas_app_name 堡垒机 --saas_app_version 2.0.0 --saas_app_secret_key ${BASTION_SECRET_KEY}

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
    docker pull ${PAAS_DOCKER_REG}/opsany-saas-ce-bastion:2.0.0
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
    "python /opt/opsany/bastion/manage.py migrate --noinput && python /opt/opsany/bastion/manage.py createcachetable django_cache > /dev/null" >> ${SHELL_LOG}
}

saas_devops_deploy(){
    shell_log "======Start devops======"
    #DevOps MySQL
    mysql -h "${MYSQL_SERVER_IP}" -u root -p"${MYSQL_ROOT_PASSWORD}" -e "create database devops DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;"
    mysql -h "${MYSQL_SERVER_IP}" -u root -p"${MYSQL_ROOT_PASSWORD}" -e "grant all on devops.* to devops@'%' identified by "\"${MYSQL_OPSANY_BASTION_PASSWORD}\"";"
    mysql -h "${MYSQL_SERVER_IP}" -u root -p"${MYSQL_ROOT_PASSWORD}" -e "grant all on devops.* to opsany@'%' identified by "\"${MYSQL_OPSANY_PASSWORD}\"";" 

    #devops
    sed -i "s/DOMAIN_NAME/$DOMAIN_NAME/g" ${INSTALL_PATH}/esb/apis/devops/toolkit/configs.py
    sed -i "s#/t/devops#/o/devops#g" ${INSTALL_PATH}/esb/apis/devops/toolkit/tools.py

    # Register devops
    if [ -f ${INSTALL_PATH}/conf/.passwd_env ];then
        source ${INSTALL_PATH}/conf/.passwd_env
    fi
    DEVOPS_SECRET_KEY=$(uuid -v4)
    echo $DEVOPS_SECRET_KEY > ${INSTALL_PATH}/conf/.devops_secret_key
    python3 ../saas/register_online_saas.py --paas_domain https://${DOMAIN_NAME} --username admin --password ${ADMIN_PASSWORD} --saas_app_code devops --saas_app_name 应用平台 --saas_app_version 2.0.0 --saas_app_secret_key ${DEVOPS_SECRET_KEY}

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
    "python /opt/opsany/devops/manage.py migrate --noinput && python /opt/opsany/devops/manage.py createcachetable django_cache > /dev/null" >> ${SHELL_LOG}
    sleep 5
    python3 ../saas/sync-user-script.py --domain https://${DOMAIN_NAME} --paas_username admin --paas_password ${ADMIN_PASSWORD} --app_code devops
    python3 ../saas/init-ce-devops.py --domain https://${DOMAIN_NAME} --username admin  --password $ADMIN_PASSWORD
}

saas_dashboard_deploy(){
    shell_log "======Start dashboard======"
    #dashboard
    mysql -h "${MYSQL_SERVER_IP}" -u root -p"${MYSQL_ROOT_PASSWORD}" -e "create database dashboard DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;"
    mysql -h "${MYSQL_SERVER_IP}" -u root -p"${MYSQL_ROOT_PASSWORD}" -e "grant all on dashboard.* to dashboard@'%' identified by "\"${MYSQL_OPSANY_BASTION_PASSWORD}\"";"
    mysql -h "${MYSQL_SERVER_IP}" -u root -p"${MYSQL_ROOT_PASSWORD}" -e "grant all on dashboard.* to opsany@'%' identified by "\"${MYSQL_OPSANY_PASSWORD}\"";" 

     #dashboard
    sed -i "s/DOMAIN_NAME/$DOMAIN_NAME/g" ${INSTALL_PATH}/esb/apis/dashboard/toolkit/configs.py
    sed -i "s#/t/dashboard#/o/dashboard#g" ${INSTALL_PATH}/esb/apis/dashboard/toolkit/tools.py

    # Register dashboard
    if [ -f ${INSTALL_PATH}/conf/.passwd_env ];then
        source ${INSTALL_PATH}/conf/.passwd_env
    fi
    DASHBOARD_SECRET_KEY=$(uuid -v4)
    echo $DASHBOARD_SECRET_KEY > ${INSTALL_PATH}/conf/.dashboard_secret_key
    python3 ../saas/register_online_saas.py --paas_domain https://${DOMAIN_NAME} --username admin --password ${ADMIN_PASSWORD} --saas_app_code dashboard --saas_app_name 可视化平台 --saas_app_version 2.0.0 --saas_app_secret_key ${DASHBOARD_SECRET_KEY}

    # Dashboard Configure
    DASHBOARD_SECRET_KEY=$(cat ${INSTALL_PATH}/conf/.dashboard_secret_key)
    sed -i "s/DOMAIN_NAME/${DOMAIN_NAME}/g" ${INSTALL_PATH}/conf/opsany-saas/dashboard/dashboard-init.py
    sed -i "s/DASHBOARD_SECRET_KEY/${DASHBOARD_SECRET_KEY}/g" ${INSTALL_PATH}/conf/opsany-saas/dashboard/dashboard-init.py
    sed -i "s/MYSQL_SERVER_IP/${MYSQL_SERVER_IP}/g" ${INSTALL_PATH}/conf/opsany-saas/dashboard/dashboard-prod.py
    sed -i "s/MYSQL_SERVER_PORT/${MYSQL_SERVER_PORT}/g" ${INSTALL_PATH}/conf/opsany-saas/dashboard/dashboard-prod.py
    sed -i "s/MYSQL_OPSANY_DASHBOARD_PASSWORD/${MYSQL_OPSANY_DASHBOARD_PASSWORD}/g" ${INSTALL_PATH}/conf/opsany-saas/dashboard/dashboard-prod.py

    # Starter container
    docker pull ${PAAS_DOCKER_REG}/opsany-saas-ce-dashboard:2.0.0
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
    "python /opt/opsany/dashboard/manage.py migrate --noinput && python /opt/opsany/dashboard/manage.py createcachetable django_cache > /dev/null" >> ${SHELL_LOG}
    python3 ../saas/sync-user-script.py --domain https://${DOMAIN_NAME} --paas_username admin --paas_password ${ADMIN_PASSWORD} --app_code monitor dashboard
    python3 ../saas/init-ce-monitor.py --domain $DOMAIN_NAME --private_ip $LOCAL_IP --paas_username admin --paas_password ${ADMIN_PASSWORD} --grafana_password admin --grafana_change_password $GRAFANA_ADMIN_PASSWORD
}

saas_base_init(){
    shell_log "======OpsAny User Initialize======"
    sleep 3
    # Sync User
    python3 ../saas/sync-user-script.py --domain https://${DOMAIN_NAME} --paas_username admin --paas_password ${ADMIN_PASSWORD} --app_code workbench cmdb control job cmp bastion

    shell_log "======OpsAny Workbench Initialize======"
    # Create Service
    python3 ../saas/init_work_order.py --domain https://$DOMAIN_NAME --paas_username admin --paas_password ${ADMIN_PASSWORD}

    shell_log "======OpsAny Proxy Initialize======"
    # Create Proxy Token
    PROXY_TOKEN=$(docker exec -e OPS_ANY_ENV=production \
            opsany-paas-proxy /bin/sh -c " /usr/local/bin/python3 /opt/opsany-proxy/manage.py create_access" | grep 'Access' | awk -F ': ' '{print $2}' | awk -F '.' '{print $1}')
    python3 ../saas/init-ce-base.py --domain $DOMAIN_NAME --private_ip $LOCAL_IP --paas_username admin --paas_password ${ADMIN_PASSWORD} --proxy_url https://${PROXY_LOCAL_IP}:8011 --proxy_public_url https://${PROXY_PUBLIC_IP}:8011 --proxy_token $PROXY_TOKEN

    shell_log "======OpsAny Job Initialize======"
    # Init Script Job
    cd $CDIR/init/
    python3 import_script.py --domain https://${DOMAIN_NAME} --paas_username admin --paas_password ${ADMIN_PASSWORD} \
--target_type script --target_path ./job-script
    python3 import_script.py --domain https://$DOMAIN_NAME --paas_username admin --paas_password ${ADMIN_PASSWORD} \
--target_type task --target_path ./job-task
    shell_warning_log "======OpsAny: Make Ops Perfect======" 
}

admin_password_init(){
    PRESTR='Ops'
    STR=`head /dev/urandom | tr -dc A-Za-z0-9 | head -c 5`
    NUM=`echo $RANDOM`
    ADMIN_NEW_PASSWORD=$PRESTR$STR$NUM
    echo "ADMIN_PASSWORD=$ADMIN_NEW_PASSWORD" > ${INSTALL_PATH}/conf/.passwd_env
    cd ${CDIR}
    python3 password-init.py --paas_domain https://$DOMAIN_NAME --username admin --password ${ADMIN_PASSWORD} --new_password $ADMIN_NEW_PASSWORD
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
        saas_base_init
        admin_password_init
		;;
	monitor)
	    saas_monitor_deploy
        saas_dashboard_deploy
	    ;;
	devops)
	    saas_devops_deploy
	    ;;
    all)
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
        saas_dashboard_deploy
        saas_devops_deploy
        saas_base_init
        admin_password_init
        ;;
	help|*)
	    echo $"Usage: $0 {base|monitor|devops|all|help}"
	    ;;
    esac
}

main $1 
