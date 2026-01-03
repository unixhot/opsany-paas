#!/bin/bash
#******************************************
# Author:       Jason Zhao
# Email:        zhaoshundong@opsany.com
# Organization: OpsAny https://www.opsany.com/
# Description:  OpsAny Community Edition Update Script For kubernetes
#******************************************

# Data/Time Variables
CTIME=$(date "+%Y-%m-%d-%H-%M")

# Shell Envionment Variables
CDIR=$(pwd)
SHELL_NAME="opsany-ce-k8s-update.sh"
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
if [ ! -f ./install-k8s.config ];then
      shell_error_log "Please Change Directory to ${INSTALL_PATH}/install"
      exit
else
    grep '^[A-Z]' install-k8s.config > install.env
    source ./install.env && rm -f install.env
    if [ -z "$ADMIN_PASSWORD" ];then
        source ${INSTALL_PATH}/conf/.passwd_env
    fi
fi

# update saas version $1 rbac $2 统一权限 $3 ${RBAC_SECRET_KEY}
update_saas_version(){
      python3 ../saas/register_online_saas.py --paas_domain https://${DOMAIN_NAME} --username admin --password ${ADMIN_PASSWORD} --saas_app_code $1 --saas_app_name $2 --saas_app_version ${UPDATE_VERSION} --saas_app_secret_key $3 --is_update true
}

# PaaS Service Update
paas_update(){
    #paas
    shell_log "======Update paas Service======"
    # PaaS Config
    UPDATE_VERSION=$1
    /bin/cp conf/opsany-paas/paas/paas.ini ${INSTALL_PATH}/conf/opsany-paas/paas/paas.ini
    /bin/cp conf/opsany-paas/paas/settings_production.py.paas ${INSTALL_PATH}/conf/opsany-paas/paas/settings_production.py.paas
    sed -i "s/PAAS_LOGIN_IP/${PAAS_LOGIN_IP}/g" ${INSTALL_PATH}/conf/opsany-paas/paas/settings_production.py.paas
    sed -i "s/PAAS_APPENGINE_IP/${PAAS_APPENGINE_IP}/g" ${INSTALL_PATH}/conf/opsany-paas/paas/settings_production.py.paas
    sed -i "s/DOMAIN_NAME/${DOMAIN_NAME}/g" ${INSTALL_PATH}/conf/opsany-paas/paas/settings_production.py.paas
    sed -i "s/LOCAL_IP/${LOCAL_IP}/g" ${INSTALL_PATH}/conf/opsany-paas/paas/settings_production.py.paas
    sed -i "s/MYSQL_SERVER_IP/${MYSQL_SERVER_IP}/g" ${INSTALL_PATH}/conf/opsany-paas/paas/settings_production.py.paas
    sed -i "s/MYSQL_OPSANY_PASSWORD/${MYSQL_OPSANY_PASSWORD}/g" ${INSTALL_PATH}/conf/opsany-paas/paas/settings_production.py.paas
    /bin/cp ${INSTALL_PATH}/conf/opsany-paas/paas/settings_production.py.paas ${INSTALL_PATH}/kubernetes/helm/opsany-paas/opsany-paas-paas/
    /bin/cp ${INSTALL_PATH}/conf/opsany-paas/paas/paas.ini ${INSTALL_PATH}/kubernetes/helm/opsany-paas/opsany-paas-paas/
    /bin/cp -r ../kubernetes/helm/opsany-paas/opsany-paas-paas/* ${INSTALL_PATH}/kubernetes/helm/opsany-paas/opsany-paas-paas/
    helm upgrade opsany-paas-paas ${INSTALL_PATH}/kubernetes/helm/opsany-paas/opsany-paas-paas/ -n opsany
}

login_update(){
 #login
    shell_log "Start login Service"
    #Login Config
    UPDATE_VERSION=$1
    RBAC_SECRET_KEY=$(cat ${INSTALL_PATH}/conf/.rbac_secret_key)
    /bin/cp conf/opsany-paas/login/login.ini ${INSTALL_PATH}/conf/opsany-paas/login/login.ini
    /bin/cp conf/opsany-paas/login/settings_production.py.login ${INSTALL_PATH}/conf/opsany-paas/login/settings_production.py.login
    sed -i "s/RBAC_SECRET_KEY/${RBAC_SECRET_KEY}/g" ${INSTALL_PATH}/conf/opsany-paas/login/settings_production.py.login
    sed -i "s/DOMAIN_NAME/${DOMAIN_NAME}/g" ${INSTALL_PATH}/conf/opsany-paas/login/settings_production.py.login
    sed -i "s/LOCAL_IP/${LOCAL_IP}/g" ${INSTALL_PATH}/conf/opsany-paas/login/settings_production.py.login
    sed -i "s/MYSQL_SERVER_IP/${MYSQL_SERVER_IP}/g" ${INSTALL_PATH}/conf/opsany-paas/login/settings_production.py.login
    sed -i "s/MYSQL_OPSANY_PASSWORD/${MYSQL_OPSANY_PASSWORD}/g" ${INSTALL_PATH}/conf/opsany-paas/login/settings_production.py.login
    /bin/cp ${INSTALL_PATH}/conf/opsany-paas/login/settings_production.py.login ${INSTALL_PATH}/kubernetes/helm/opsany-paas/opsany-paas-login/
    /bin/cp ${INSTALL_PATH}/conf/opsany-paas/login/login.ini ${INSTALL_PATH}/kubernetes/helm/opsany-paas/opsany-paas-login/
    /bin/cp -r ../kubernetes/helm/opsany-paas/opsany-paas-login/* ${INSTALL_PATH}/kubernetes/helm/opsany-paas/opsany-paas-login/
    helm upgrade opsany-paas-login ${INSTALL_PATH}/kubernetes/helm/opsany-paas/opsany-paas-login/ -n opsany
}

esb_update(){
#esb
    shell_log "Start esb Service"

# ESB Components Update
    shell_log "======ESB Update======"
    /bin/cp -r ../paas-ce/paas/esb/components/generic/apis/* ${INSTALL_PATH}/esb/apis/
    # Copy to NFS
    /bin/cp -r ${INSTALL_PATH}/esb/apis/* /data/k8s-nfs/opsany-esb-code/

    # update esb sql
    MYSQL_SERVER_IP=$(kubectl get svc opsany-base-mysql -n opsany | awk -F ' ' '{print $3}' | tail -1)
    export MYSQL_PWD=${MYSQL_ROOT_PASSWORD}
    /bin/cp ./init/esb-init/* ${INSTALL_PATH}/init/esb-init/
    kubectl cp ${INSTALL_PATH}/init/esb-init opsany-base-mysql-0:/opt/ -n opsany
    kubectl -n opsany exec opsany-base-mysql-0 -- sh -c "
        mysql -h \"${MYSQL_SERVER_IP}\" -P ${MYSQL_SERVER_PORT} -u root -p\"${MYSQL_ROOT_PASSWORD}\" opsany_paas < /opt/esb-init/esb_api_doc.sql
        mysql -h \"${MYSQL_SERVER_IP}\" -P ${MYSQL_SERVER_PORT} -u root -p\"${MYSQL_ROOT_PASSWORD}\" opsany_paas < /opt/esb-init/esb_channel.sql
        mysql -h \"${MYSQL_SERVER_IP}\" -P ${MYSQL_SERVER_PORT} -u root -p\"${MYSQL_ROOT_PASSWORD}\" opsany_paas < /opt/esb-init/esb_component_system.sql
        mysql -h \"${MYSQL_SERVER_IP}\" -P ${MYSQL_SERVER_PORT} -u root -p\"${MYSQL_ROOT_PASSWORD}\" opsany_paas < /opt/esb-init/esb_function_controller.sql
    "

    # ESB Config
    UPDATE_VERSION=$1
    /bin/cp conf/opsany-paas/esb/esb.ini ${INSTALL_PATH}/conf/opsany-paas/esb/esb.ini
    /bin/cp conf/opsany-paas/esb/settings_production.py.esb ${INSTALL_PATH}/conf/opsany-paas/esb/settings_production.py.esb
    sed -i "s/PAAS_LOGIN_IP/${PAAS_LOGIN_IP}/g" ${INSTALL_PATH}/conf/opsany-paas/esb/settings_production.py.esb
    sed -i "s/PAAS_PAAS_IP/${PAAS_PAAS_IP}/g" ${INSTALL_PATH}/conf/opsany-paas/esb/settings_production.py.esb
    sed -i "s/REDIS_SERVER_IP/${REDIS_SERVER_IP}/g" ${INSTALL_PATH}/conf/opsany-paas/esb/settings_production.py.esb
    sed -i "s/REDIS_SERVER_PASSWORD/${REDIS_SERVER_PASSWORD}/g" ${INSTALL_PATH}/conf/opsany-paas/esb/settings_production.py.esb
    sed -i "s/MYSQL_SERVER_IP/${MYSQL_SERVER_IP}/g" ${INSTALL_PATH}/conf/opsany-paas/esb/settings_production.py.esb
    sed -i "s/MYSQL_OPSANY_PASSWORD/${MYSQL_OPSANY_PASSWORD}/g" ${INSTALL_PATH}/conf/opsany-paas/esb/settings_production.py.esb
    /bin/cp ${INSTALL_PATH}/conf/opsany-paas/esb/settings_production.py.esb ${INSTALL_PATH}/kubernetes/helm/opsany-paas/opsany-paas-esb/
    /bin/cp ${INSTALL_PATH}/conf/opsany-paas/esb/esb.ini ${INSTALL_PATH}/kubernetes/helm/opsany-paas/opsany-paas-esb/
    /bin/cp -r ../kubernetes/helm/opsany-paas/opsany-paas-esb/* ${INSTALL_PATH}/kubernetes/helm/opsany-paas/opsany-paas-esb/
    sed -i "s/^.*appVersion:.*$/appVersion: \"${UPDATE_VERSION}\"/g" ${INSTALL_PATH}/kubernetes/helm/opsany-paas/opsany-paas-esb/Chart.yaml
    ESB_POD=$(kubectl get pod -n opsany | grep opsany-paas-esb | awk '{print $1}')
    helm upgrade opsany-paas-esb ${INSTALL_PATH}/kubernetes/helm/opsany-paas/opsany-paas-esb/ -n opsany
    kubectl delete pod ${ESB_POD} -n opsany
    sleep 10
}  

appengine_update(){
 #appengine
    shell_log "Start appengine Service"
    # App Engine Config
    UPDATE_VERSION=$1
    /bin/cp conf/opsany-paas/appengine/appengine.ini ${INSTALL_PATH}/conf/opsany-paas/appengine/appengine.ini
    /bin/cp conf/opsany-paas/appengine/settings_production.py.appengine ${INSTALL_PATH}/conf/opsany-paas/appengine/settings_production.py.appengine
    sed -i "s/MYSQL_SERVER_IP/${MYSQL_SERVER_IP}/g" ${INSTALL_PATH}/conf/opsany-paas/appengine/settings_production.py.appengine
    sed -i "s/MYSQL_OPSANY_PASSWORD/${MYSQL_OPSANY_PASSWORD}/g" ${INSTALL_PATH}/conf/opsany-paas/appengine/settings_production.py.appengine
    /bin/cp ${INSTALL_PATH}/conf/opsany-paas/appengine/settings_production.py.appengine ${INSTALL_PATH}/kubernetes/helm/opsany-paas/opsany-paas-appengine/
    /bin/cp ${INSTALL_PATH}/conf/opsany-paas/appengine/appengine.ini ${INSTALL_PATH}/kubernetes/helm/opsany-paas/opsany-paas-appengine/
    /bin/cp -r ../kubernetes/helm/opsany-paas/opsany-paas-appengine/* ${INSTALL_PATH}/kubernetes/helm/opsany-paas/opsany-paas-appengine/
    helm upgrade opsany-paas-appengine ${INSTALL_PATH}/kubernetes/helm/opsany-paas/opsany-paas-appengine/ -n opsany
}  

# Update Proxy
proxy_update(){
    shell_log "======Update Proxy======"
    UPDATE_VERSION=$1
    # Proxy config
    MYSQL_SERVER_IP=$(kubectl get svc | grep opsany-base-mysql | awk -F ' ' '{print $3}' | grep '^[1-10]')
    CONTROL_SECRET_KEY=$(cat ${INSTALL_PATH}/conf/.control_secret_key)
    /bin/cp conf/proxy/proxy.ini ${INSTALL_PATH}/conf/proxy/proxy.ini
    /bin/cp conf/proxy/saltapi.ini ${INSTALL_PATH}/conf/proxy/saltapi.ini
    /bin/cp conf/proxy/saltmaster.ini ${INSTALL_PATH}/conf/proxy/saltmaster.ini
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
    mkdir -p ${INSTALL_PATH}/logs/proxy
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
        ${PAAS_DOCKER_REG}/opsany-paas-proxy:${UPDATE_VERSION}

    # OpsAny Database Init
    docker exec -e OPS_ANY_ENV=production \
        opsany-paas-proxy /bin/sh -c "/usr/local/bin/python3 /opt/opsany-proxy/manage.py migrate >> ${SHELL_LOG}"
}

websocket_update(){
# Websocket
    UPDATE_VERSION=$1
    BASTION_SECRET_KEY=$(cat ${INSTALL_PATH}/conf/.bastion_secret_key)
    /bin/cp conf/opsany-paas/websocket/websocket.ini ${INSTALL_PATH}/conf/opsany-paas/websocket/websocket.ini
    /bin/cp conf/opsany-paas/websocket/settings_production.py.websocket ${INSTALL_PATH}/conf/opsany-paas/websocket/settings_production.py.websocket
    /bin/cp conf/opsany-paas/websocket/settings_production.py.websocket.init ${INSTALL_PATH}/conf/opsany-paas/websocket/settings_production.py.websocket.init
    sed -i "s/BASTION_SECRET_KEY/${BASTION_SECRET_KEY}/g" ${INSTALL_PATH}/conf/opsany-paas/websocket/settings_production.py.websocket.init
    sed -i "s/WEBSOCKET_GUACD_HOST/${WEBSOCKET_GUACD_HOST}/g" ${INSTALL_PATH}/conf/opsany-paas/websocket/settings_production.py.websocket
    sed -i "s/REDIS_SERVER_IP/${REDIS_SERVER_IP}/g" ${INSTALL_PATH}/conf/opsany-paas/websocket/settings_production.py.websocket
    sed -i "s/REDIS_SERVER_USER/${REDIS_SERVER_USER}/g" ${INSTALL_PATH}/conf/opsany-paas/websocket/settings_production.py.websocket
    sed -i "s/REDIS_SERVER_PORT/${REDIS_SERVER_PORT}/g" ${INSTALL_PATH}/conf/opsany-paas/websocket/settings_production.py.websocket
    sed -i "s/REDIS_SERVER_PASSWORD/${REDIS_SERVER_PASSWORD}/g" ${INSTALL_PATH}/conf/opsany-paas/websocket/settings_production.py.websocket
    sed -i "s/MYSQL_SERVER_IP/${MYSQL_SERVER_IP}/g" ${INSTALL_PATH}/conf/opsany-paas/websocket/settings_production.py.websocket
    sed -i "s/MYSQL_SERVER_PORT/${MYSQL_SERVER_PORT}/g" ${INSTALL_PATH}/conf/opsany-paas/websocket/settings_production.py.websocket
    sed -i "s/MYSQL_OPSANY_PASSWORD/${MYSQL_OPSANY_PASSWORD}/g" ${INSTALL_PATH}/conf/opsany-paas/websocket/settings_production.py.websocket
    sed -i "s/PAAS_PAAS_IP/opsany-paas-openresty/g" ${INSTALL_PATH}/conf/opsany-paas/websocket/settings_production.py.websocket.init
    /bin/cp ${INSTALL_PATH}/conf/opsany-paas/websocket/settings_production.py.websocket ${INSTALL_PATH}/kubernetes/helm/opsany-paas/opsany-paas-websocket/
    /bin/cp ${INSTALL_PATH}/conf/opsany-paas/websocket/settings_production.py.websocket.init ${INSTALL_PATH}/kubernetes/helm/opsany-paas/opsany-paas-websocket/
    /bin/cp ${INSTALL_PATH}/conf/opsany-paas/websocket/websocket.ini ${INSTALL_PATH}/kubernetes/helm/opsany-paas/opsany-paas-websocket/
    /bin/cp -r ../kubernetes/helm/opsany-paas/opsany-paas-websocket/* ${INSTALL_PATH}/kubernetes/helm/opsany-paas/opsany-paas-websocket/
    helm upgrade opsany-paas-websocket ${INSTALL_PATH}/kubernetes/helm/opsany-paas/opsany-paas-websocket/ -n opsany
}

saas_rbac_update(){
    shell_log "======Update RBAC Begin======"
    # Modify configuration
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
    /bin/cp ${INSTALL_PATH}/conf/opsany-saas/rbac/*  ${INSTALL_PATH}/kubernetes/helm/opsany-saas/opsany-saas-rbac/
    /bin/cp -r ../kubernetes/helm/opsany-saas/opsany-saas-rbac/* ${INSTALL_PATH}/kubernetes/helm/opsany-saas/opsany-saas-rbac/
    helm upgrade opsany-saas-rbac ${INSTALL_PATH}/kubernetes/helm/opsany-saas/opsany-saas-rbac/ -n opsany 
    #helm upgrade opsany-saas-rbac ${INSTALL_PATH}/kubernetes/helm/opsany-saas/opsany-saas-rbac/ -n opsany --set annotations."opsany.com/change-cause"="$(date +%Y-%m-%dT%H:%M:%S)"
    
    # Django migrate
    sleep 10
    update_saas_version rbac 统一权限 ${RBAC_SECRET_KEY}
    helm list -n opsany | grep opsany-saas-rbac
    kubectl get pod -n opsany | grep opsany-saas-rbac
    shell_log "======RBAC Update END======"

}

saas_workbench_update(){
    shell_log "======Update workbench Begin======"
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
    /bin/cp ${INSTALL_PATH}/conf/opsany-saas/workbench/*  ${INSTALL_PATH}/kubernetes/helm/opsany-saas/opsany-saas-workbench/
    /bin/cp -r ../kubernetes/helm/opsany-saas/opsany-saas-workbench/* ${INSTALL_PATH}/kubernetes/helm/opsany-saas/opsany-saas-workbench/
    helm upgrade opsany-saas-workbench ${INSTALL_PATH}/kubernetes/helm/opsany-saas/opsany-saas-workbench/ -n opsany 
    #--set annotations."opsany.com/change-cause"="$(date +%Y-%m-%dT%H:%M:%S)"
    
    # Django migrate
    sleep 10
    helm list -n opsany | grep opsany-saas-workbench
    kubectl get pod -n opsany | grep opsany-saas-workbench
    update_saas_version workbench 工作台 ${WORKBENCH_SECRET_KEY}
    shell_log "======Workbench Update END======"
}

saas_cmdb_update(){
    shell_log "======Update cmdb Begin======"
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
    /bin/cp ${INSTALL_PATH}/conf/opsany-saas/cmdb/*  ${INSTALL_PATH}/kubernetes/helm/opsany-saas/opsany-saas-cmdb/
    /bin/cp -r ../kubernetes/helm/opsany-saas/opsany-saas-cmdb/* ${INSTALL_PATH}/kubernetes/helm/opsany-saas/opsany-saas-cmdb/
    helm upgrade opsany-saas-cmdb ${INSTALL_PATH}/kubernetes/helm/opsany-saas/opsany-saas-cmdb/ -n opsany 
    #--set annotations."opsany.com/change-cause"="$(date +%Y-%m-%dT%H:%M:%S)"
    
    # Django migrate
    sleep 10
    helm list -n opsany | grep opsany-saas-cmdb
    kubectl get pod -n opsany | grep opsany-saas-cmdb
    update_saas_version cmdb 资源平台 ${CMDB_SECRET_KEY}
    shell_log "======CMDB Update END======"    
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
    /bin/cp ${INSTALL_PATH}/conf/opsany-saas/control/*  ${INSTALL_PATH}/kubernetes/helm/opsany-saas/opsany-saas-control/
    /bin/cp -r ../kubernetes/helm/opsany-saas/opsany-saas-control/* ${INSTALL_PATH}/kubernetes/helm/opsany-saas/opsany-saas-control/
    helm upgrade opsany-saas-control ${INSTALL_PATH}/kubernetes/helm/opsany-saas/opsany-saas-control/ -n opsany
    
    # Django migrate
    sleep 10
    helm list -n opsany | grep opsany-saas-control
    kubectl get pod -n opsany | grep opsany-saas-control
    update_saas_version control 管控平台 ${CONTROL_SECRET_KEY}
    shell_log "======Control Update END======"       
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
    /bin/cp ${INSTALL_PATH}/conf/opsany-saas/job/*  ${INSTALL_PATH}/kubernetes/helm/opsany-saas/opsany-saas-job/
    /bin/cp -r ../kubernetes/helm/opsany-saas/opsany-saas-job/* ${INSTALL_PATH}/kubernetes/helm/opsany-saas/opsany-saas-job/
    helm upgrade opsany-saas-job ${INSTALL_PATH}/kubernetes/helm/opsany-saas/opsany-saas-job/ -n opsany
    
    # Django migrate
    sleep 10
    helm list -n opsany | grep opsany-saas-job
    kubectl get pod -n opsany | grep opsany-saas-job
    update_saas_version job 作业平台 ${JOB_SECRET_KEY}
    shell_log "======Job Update END======"       
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
    /bin/cp ${INSTALL_PATH}/conf/opsany-saas/monitor/*  ${INSTALL_PATH}/kubernetes/helm/opsany-saas/opsany-saas-monitor/
    /bin/cp -r ../kubernetes/helm/opsany-saas/opsany-saas-monitor/* ${INSTALL_PATH}/kubernetes/helm/opsany-saas/opsany-saas-monitor/
    helm upgrade opsany-saas-monitor ${INSTALL_PATH}/kubernetes/helm/opsany-saas/opsany-saas-monitor/ -n opsany
    
   # Django migrate
    sleep 10
    helm list -n opsany | grep opsany-saas-monitor
    kubectl get pod -n opsany | grep opsany-saas-monitor
    update_saas_version monitor 基础监控 ${MONITOR_SECRET_KEY}
    shell_log "======Monitor Update END======"       
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
    /bin/cp ${INSTALL_PATH}/conf/opsany-saas/cmp/*  ${INSTALL_PATH}/kubernetes/helm/opsany-saas/opsany-saas-cmp/
    /bin/cp -r ../kubernetes/helm/opsany-saas/opsany-saas-cmp/* ${INSTALL_PATH}/kubernetes/helm/opsany-saas/opsany-saas-cmp/
    helm upgrade opsany-saas-cmp ${INSTALL_PATH}/kubernetes/helm/opsany-saas/opsany-saas-cmp/ -n opsany
    
    # Django migrate
    sleep 10
    helm list -n opsany | grep opsany-saas-cmp
    kubectl get pod -n opsany | grep opsany-saas-cmp
    update_saas_version cmp 云管平台 ${CMP_SECRET_KEY}
    shell_log "======CMP Update END======"       
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
    /bin/cp ${INSTALL_PATH}/conf/opsany-saas/bastion/*  ${INSTALL_PATH}/kubernetes/helm/opsany-saas/opsany-saas-bastion/
    /bin/cp -r ../kubernetes/helm/opsany-saas/opsany-saas-bastion/* ${INSTALL_PATH}/kubernetes/helm/opsany-saas/opsany-saas-bastion/
    helm upgrade opsany-saas-bastion ${INSTALL_PATH}/kubernetes/helm/opsany-saas/opsany-saas-bastion/ -n opsany

    # Django migrate
    sleep 10
    helm list -n opsany | grep opsany-saas-bastion
    kubectl get pod -n opsany | grep opsany-saas-bastion
    update_saas_version bastion 堡垒机 ${BASTION_SECRET_KEY}
    shell_log "======Bastion Update END======"       
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
    /bin/cp ${INSTALL_PATH}/conf/opsany-saas/devops/*  ${INSTALL_PATH}/kubernetes/helm/opsany-saas/opsany-saas-devops/
    /bin/cp -r ../kubernetes/helm/opsany-saas/opsany-saas-devops/* ${INSTALL_PATH}/kubernetes/helm/opsany-saas/opsany-saas-devops/
    helm upgrade opsany-saas-devops ${INSTALL_PATH}/kubernetes/helm/opsany-saas/opsany-saas-devops/ -n opsany

    # Django migrate
    sleep 10
    helm list -n opsany | grep opsany-saas-devops
    kubectl get pod -n opsany | grep opsany-saas-devops
    update_saas_version devops 应用平台 ${DEVOPS_SECRET_KEY}
    shell_log "======Bastion Update END======"           
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
    /bin/cp ${INSTALL_PATH}/conf/opsany-saas/pipeline/*  ${INSTALL_PATH}/kubernetes/helm/opsany-saas/opsany-saas-pipeline/
    /bin/cp -r ../kubernetes/helm/opsany-saas/opsany-saas-pipeline/* ${INSTALL_PATH}/kubernetes/helm/opsany-saas/opsany-saas-pipeline/
    helm upgrade opsany-saas-pipeline ${INSTALL_PATH}/kubernetes/helm/opsany-saas/opsany-saas-pipeline/ -n opsany

    # Django migrate
    sleep 10
    helm list -n opsany | grep opsany-saas-pipeline
    kubectl get pod -n opsany | grep opsany-saas-pipeline
    update_saas_version pipeline 流水线 ${PIPELINE_SECRET_KEY}
    shell_log "======Bastion Update END======"           
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
    /bin/cp ${INSTALL_PATH}/conf/opsany-saas/deploy/*  ${INSTALL_PATH}/kubernetes/helm/opsany-saas/opsany-saas-deploy/
    /bin/cp -r ../kubernetes/helm/opsany-saas/opsany-saas-deploy/* ${INSTALL_PATH}/kubernetes/helm/opsany-saas/opsany-saas-deploy/
    helm upgrade opsany-saas-deploy ${INSTALL_PATH}/kubernetes/helm/opsany-saas/opsany-saas-deploy/ -n opsany

    # Django migrate
    sleep 10
    helm list -n opsany | grep opsany-saas-deploy
    kubectl get pod -n opsany | grep opsany-saas-deploy
    update_saas_version deploy 持续部署 ${DEPLOY_SECRET_KEY}
    shell_log "======Bastion Update END======"               
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
    /bin/cp ${INSTALL_PATH}/conf/opsany-saas/repo/*  ${INSTALL_PATH}/kubernetes/helm/opsany-saas/opsany-saas-repo/
    /bin/cp -r ../kubernetes/helm/opsany-saas/opsany-saas-repo/* ${INSTALL_PATH}/kubernetes/helm/opsany-saas/opsany-saas-repo/
    helm upgrade opsany-saas-repo ${INSTALL_PATH}/kubernetes/helm/opsany-saas/opsany-saas-repo/ -n opsany

    # Django migrate
    sleep 10
    helm list -n opsany | grep opsany-saas-repo
    kubectl get pod -n opsany | grep opsany-saas-repo
    update_saas_version repo 制品仓库 ${REPO_SECRET_KEY}
    shell_log "======Repo Update END======"               
}

saas_code_update(){
    shell_log "======Update code======"
    # Dashboard Configure
    UPDATE_VERSION=$1
    CODE_SECRET_KEY=$(cat ${INSTALL_PATH}/conf/.code_secret_key)
    /bin/cp conf/opsany-saas/code/* ${INSTALL_PATH}/conf/opsany-saas/code/
    sed -i "s/DOMAIN_NAME/${DOMAIN_NAME}/g" ${INSTALL_PATH}/conf/opsany-saas/code/code-init.py
    sed -i "s/CODE_SECRET_KEY/${CODE_SECRET_KEY}/g" ${INSTALL_PATH}/conf/opsany-saas/code/code-init.py
    sed -i "s/MYSQL_SERVER_IP/${MYSQL_SERVER_IP}/g" ${INSTALL_PATH}/conf/opsany-saas/code/code-prod.py
    sed -i "s/MYSQL_SERVER_PORT/${MYSQL_SERVER_PORT}/g" ${INSTALL_PATH}/conf/opsany-saas/code/code-prod.py
    sed -i "s/MYSQL_OPSANY_CODE_PASSWORD/${MYSQL_OPSANY_CODE_PASSWORD}/g" ${INSTALL_PATH}/conf/opsany-saas/code/code-prod.py
    /bin/cp ${INSTALL_PATH}/conf/opsany-saas/code/*  ${INSTALL_PATH}/kubernetes/helm/opsany-saas/opsany-saas-code/
    /bin/cp -r ../kubernetes/helm/opsany-saas/opsany-saas-code/* ${INSTALL_PATH}/kubernetes/helm/opsany-saas/opsany-saas-code/
    helm upgrade opsany-saas-code ${INSTALL_PATH}/kubernetes/helm/opsany-saas/opsany-saas-code/ -n opsany

    # Django migrate
    sleep 10
    helm list -n opsany | grep opsany-saas-code
    kubectl get pod -n opsany | grep opsany-saas-code
    update_saas_version code 代码仓库 ${CODE_SECRET_KEY}
    shell_log "======Repo Update END======"             
}

saas_llmops_update(){
    shell_log "======Update llmops======"
    # llmops Configure
    UPDATE_VERSION=$1
    LLMOPS_SECRET_KEY=$(cat ${INSTALL_PATH}/conf/.llmops_secret_key)
    /bin/cp conf/opsany-saas/llmops/* ${INSTALL_PATH}/conf/opsany-saas/llmops/
    sed -i "s/DOMAIN_NAME/${DOMAIN_NAME}/g" ${INSTALL_PATH}/conf/opsany-saas/llmops/llmops-init.py
    sed -i "s/LLMOPS_SECRET_KEY/${LLMOPS_SECRET_KEY}/g" ${INSTALL_PATH}/conf/opsany-saas/llmops/llmops-init.py
    sed -i "s/MYSQL_SERVER_IP/${MYSQL_SERVER_IP}/g" ${INSTALL_PATH}/conf/opsany-saas/llmops/llmops-prod.py
    sed -i "s/MYSQL_SERVER_PORT/${MYSQL_SERVER_PORT}/g" ${INSTALL_PATH}/conf/opsany-saas/llmops/llmops-prod.py
    sed -i "s/MYSQL_OPSANY_LLMOPS_PASSWORD/${MYSQL_OPSANY_LLMOPS_PASSWORD}/g" ${INSTALL_PATH}/conf/opsany-saas/llmops/llmops-prod.py
    /bin/cp ${INSTALL_PATH}/conf/opsany-saas/llmops/*  ${INSTALL_PATH}/kubernetes/helm/opsany-saas/opsany-saas-llmops/
    /bin/cp -r ../kubernetes/helm/opsany-saas/opsany-saas-llmops/* ${INSTALL_PATH}/kubernetes/helm/opsany-saas/opsany-saas-llmops/
    helm upgrade opsany-saas-llmops ${INSTALL_PATH}/kubernetes/helm/opsany-saas/opsany-saas-llmops/ -n opsany

    # Django migrate
    sleep 10
    helm list -n opsany | grep opsany-saas-llmops
    kubectl get pod -n opsany | grep opsany-saas-llmops
    update_saas_version llmops 代码仓库 ${LLMOPS_SECRET_KEY}
    shell_log "======Repo Update END======"             
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
        saas_llmops_update $2
		;;
    ops)
	    saas_rbac_update $2
	    saas_workbench_update $2
	    saas_cmdb_update $2
	    saas_control_update $2
	    saas_job_update $2
	    saas_cmp_update $2
	    saas_bastion_update $2
        saas_llmops_update $2
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
    code)
	    saas_code_update $2
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
    llmops)
        llmops_update $2
        ;;
    dev)
        saas_devops_update $2
        saas_pipeline_update $2
        saas_deploy_update $2
        saas_repo_update $2
        saas_code_update $2
        ;;
    all)
	    saas_rbac_update $2
	    saas_workbench_update $2
	    saas_cmdb_update $2
	    saas_control_update $2
	    saas_job_update $2
	    saas_cmp_update $2
	    saas_bastion_update $2
        saas_monitor_update $2
        saas_devops_update $2
        saas_pipeline_update $2
        saas_deploy_update $2
        saas_repo_update $2
        saas_code_update $2
        saas_llmops_update $2
        ;;
	help|*)
	    echo $"Usage: $0 {(ops|dev|all|help) version}"
	    ;;
    esac
}

main $1 $2
