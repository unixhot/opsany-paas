#!/bin/bash
#******************************************
# Author:       Jason Zhao
# Email:        zhaoshundong@opsany.com
# Organization: OpsAny https://www.opsany.com/
# Description:  OpsAny PaaS Install Script for Kubernetes
#******************************************

# Get Data/Time
CTIME=$(date "+%Y-%m-%d-%H-%M")

# Shell Envionment Variables
CDIR=$(pwd)
SHELL_NAME="paas-k8s-install.sh"
SHELL_LOG="${CDIR}/${SHELL_NAME}.log"

# Shell Log Record
shell_log(){
    LOG_INFO=$1
    echo -e "\033[32m---------------- $CTIME ${SHELL_NAME} : ${LOG_INFO} ----------------\033[0m"
    echo "$CTIME ${SHELL_NAME} : ${LOG_INFO}" >> ${SHELL_LOG}
}

shell_warning_log(){
    LOG_INFO=$1
    echo -e "\033[33m---------------- $CTIME ${SHELL_NAME} : ${LOG_INFO} ----------------\033[0m"
    echo "$CTIME ${SHELL_NAME} : ${LOG_INFO}" >> ${SHELL_LOG}
}

shell_error_log(){
    LOG_INFO=$1
    echo -e "\033[31m---------------- $CTIME ${SHELL_NAME} : ${LOG_INFO} ----------------\033[0m"
    echo "$CTIME ${SHELL_NAME} : ${LOG_INFO}" >> ${SHELL_LOG}
}

# Install Inspection
if [ ! -f ./install-k8s.config ];then
      shell_error_log "Please Copy install.config and Change: cp install.config.example install.config"
      exit
else
    grep '^[A-Z]' install-k8s.config > install.env
    source ./install.env && rm -f install.env
fi

# Create Self-signed Server Certificate
ssl_make(){
    shell_log "Create Self-signed Server Certificate"
    # create dir for ssl
    if [ ! -d ./conf/nginx-conf.d/ssl ];then
      mkdir -p ./conf/nginx-conf.d/ssl
    fi
    cp ./conf/openssl.cnf ./conf/nginx-conf.d/ssl/
    cd ./conf/nginx-conf.d/ssl
    openssl genrsa -des3 -passout pass:opsany -out $DOMAIN_NAME.key 2048 >/dev/null 2>&1

    #Create server certificate signing request
    SUBJECT="/C=CN/ST=BeiJing/L=BeiJing/O=BeiJing/OU=OpsAny/CN=OpsAny"
    openssl req -new -passin pass:opsany -subj $SUBJECT -key $DOMAIN_NAME.key -out $DOMAIN_NAME.csr >/dev/null 2>&1

    #Remove password
    mv $DOMAIN_NAME.key $DOMAIN_NAME.origin.key
    openssl rsa -passin pass:opsany -in $DOMAIN_NAME.origin.key  -out $DOMAIN_NAME.key >/dev/null 2>&1

    #Sign SSL certificate
    openssl x509 -req -days 3650 -extfile openssl.cnf -extensions 'v3_req'  -in $DOMAIN_NAME.csr -signkey $DOMAIN_NAME.key -out $DOMAIN_NAME.crt >/dev/null 2>&1
    openssl x509 -in ${DOMAIN_NAME}.crt -out ${DOMAIN_NAME}.pem -outform PEM >/dev/null 2>&1
    mv ${DOMAIN_NAME}.pem ${DOMAIN_NAME}.origin.pem
    cat ${DOMAIN_NAME}.key ${DOMAIN_NAME}.origin.pem > ${DOMAIN_NAME}.pem
    rm -f ./conf/openssl.cnf
}

# Check Install requirement
install_check(){
  shell_warning_log "The beginning is the first step to success"
  if [ -f /etc/redhat-release ];then
      setenforce 0
  fi
}

# Install Initialize
opsany_init(){
    shell_log "Config: Install Init"
    mkdir -p ${INSTALL_PATH}/{uploads/guacamole,uploads/workbench/icon,conf,esb}
    mkdir -p /data/k8s-nfs/{opsany-logs,opsany-uploads/guacamole,opsany-esb-code,opsany-proxy,opsany-grafana-data}
    chmod 777 /data/k8s-nfs/opsany-grafana-data
    mkdir -p /data/k8s-nfs/opsany-proxy/{salt-certs,salt-etc,salt-cache,salt-srv,salt-pillar,ansible-playbook,ansible-pki}
    cd $CDIR
    /bin/cp -r ./conf ${INSTALL_PATH}/
    /bin/cp -r ../kubernetes ${INSTALL_PATH}/
    /bin/cp ${INSTALL_PATH}/conf/nginx-conf.d/ssl/$DOMAIN_NAME.key ${INSTALL_PATH}/kubernetes/helm/opsany-paas/opsany-paas-openresty/ssl/
    /bin/cp ${INSTALL_PATH}/conf/nginx-conf.d/ssl/$DOMAIN_NAME.pem ${INSTALL_PATH}/kubernetes/helm/opsany-paas/opsany-paas-openresty/ssl/
    sed -i "s/DOMAIN_NAME/$DOMAIN_NAME/g" ${INSTALL_PATH}/kubernetes/helm/opsany-paas/opsany-paas-openresty/templates/deployment.yaml
    sed -i "s/DOMAIN_NAME/$DOMAIN_NAME/g" ${INSTALL_PATH}/kubernetes/helm/opsany-paas/opsany-paas-openresty/templates/secret.yaml
    sed -i "s/DOMAIN_NAME/$DOMAIN_NAME/g" ${INSTALL_PATH}/kubernetes/helm/opsany-paas/opsany-paas-openresty/values.yaml
    /bin/cp -r ./init ${INSTALL_PATH}/
    /bin/cp -r ./uploads/* /data/k8s-nfs/opsany-uploads/
    /bin/cp -r ../paas-ce/saas/saas-logo/* ${INSTALL_PATH}/uploads/workbench/icon/
    ## init for esb
    /bin/cp -r ../paas-ce/paas/esb/components/generic/apis/ ${INSTALL_PATH}/esb/
    
    ## init for Proxy
    /bin/cp -a ./conf/salt/* /data/k8s-nfs/opsany-proxy/salt-etc/
    /bin/cp -a ./conf/salt/certs/* /data/k8s-nfs/opsany-proxy/salt-certs/
    shell_log "End: Install Init"
}

esb_init(){
    shell_log "ESB Initialize"
    #cmdb
    mkdir -p ${INSTALL_PATH}/esb/apis/
    /bin/cp -r /opt/opsany-paas/paas-ce/paas/esb/components/generic/apis/* ${INSTALL_PATH}/esb/apis/
    #cmdb
    sed -i "s/DOMAIN_NAME/$DOMAIN_NAME/g" ${INSTALL_PATH}/esb/apis/cmdb/toolkit/configs.py
    sed -i "s#/t/cmdb#/o/cmdb#g" ${INSTALL_PATH}/esb/apis/cmdb/toolkit/tools.py
    #control
    sed -i "s/DOMAIN_NAME/$DOMAIN_NAME/g" ${INSTALL_PATH}/esb/apis/control/toolkit/configs.py
    sed -i "s#/t/control#/o/control#g" ${INSTALL_PATH}/esb/apis/control/toolkit/tools.py
    #rbac
    sed -i "s/DOMAIN_NAME/$DOMAIN_NAME/g" ${INSTALL_PATH}/esb/apis/rbac/toolkit/configs.py
    sed -i "s#/t/rbac#/o/rbac#g" ${INSTALL_PATH}/esb/apis/rbac/toolkit/configs.py
    #job
    sed -i "s/DOMAIN_NAME/$DOMAIN_NAME/g" ${INSTALL_PATH}/esb/apis/task/toolkit/configs.py
    sed -i "s#/t/job#/o/job#g" ${INSTALL_PATH}/esb/apis/task/toolkit/tools.py
    sed -i "s/DOMAIN_NAME/$DOMAIN_NAME/g" ${INSTALL_PATH}/esb/apis/job/toolkit/configs.py
    sed -i "s#/t/job#/o/job#g" ${INSTALL_PATH}/esb/apis/job/toolkit/tools.py
    #workbench
    sed -i "s/DOMAIN_NAME/$DOMAIN_NAME/g" ${INSTALL_PATH}/esb/apis/workbench/toolkit/configs.py
    sed -i "s#/t/workbench#/o/workbench#g" ${INSTALL_PATH}/esb/apis/workbench/toolkit/tools.py
    #monitor
    sed -i "s/DOMAIN_NAME/$DOMAIN_NAME/g" ${INSTALL_PATH}/esb/apis/monitor/toolkit/configs.py
    sed -i "s#/t/monitor#/o/monitor#g" ${INSTALL_PATH}/esb/apis/monitor/toolkit/tools.py
    #cmp
    sed -i "s/DOMAIN_NAME/$DOMAIN_NAME/g" ${INSTALL_PATH}/esb/apis/cmp/toolkit/configs.py
    sed -i "s#/t/cmp#/o/cmp#g" ${INSTALL_PATH}/esb/apis/cmp/toolkit/tools.py
    #devops
    sed -i "s/DOMAIN_NAME/$DOMAIN_NAME/g" ${INSTALL_PATH}/esb/apis/devops/toolkit/configs.py
    sed -i "s#/t/devops#/o/devops#g" ${INSTALL_PATH}/esb/apis/devops/toolkit/tools.py
    #pipeline
    sed -i "s/DOMAIN_NAME/$DOMAIN_NAME/g" ${INSTALL_PATH}/esb/apis/pipeline/toolkit/configs.py
    sed -i "s#/t/pipeline#/o/pipeline#g" ${INSTALL_PATH}/esb/apis/pipeline/toolkit/tools.py
    #deploy
    sed -i "s/DOMAIN_NAME/$DOMAIN_NAME/g" ${INSTALL_PATH}/esb/apis/deploy/toolkit/configs.py
    sed -i "s#/t/deploy#/o/deploy#g" ${INSTALL_PATH}/esb/apis/deploy/toolkit/tools.py
    #repo
    sed -i "s/DOMAIN_NAME/$DOMAIN_NAME/g" ${INSTALL_PATH}/esb/apis/repo/toolkit/configs.py
    sed -i "s#/t/repo#/o/repo#g" ${INSTALL_PATH}/esb/apis/repo/toolkit/tools.py
    #bastion
    sed -i "s/DOMAIN_NAME/$DOMAIN_NAME/g" ${INSTALL_PATH}/esb/apis/bastion/toolkit/configs.py
    sed -i "s#/t/bastion#/o/bastion#g" ${INSTALL_PATH}/esb/apis/bastion/toolkit/configs.py
    #dashboard
    sed -i "s/DOMAIN_NAME/$DOMAIN_NAME/g" ${INSTALL_PATH}/esb/apis/dashboard/toolkit/configs.py
    sed -i "s#/t/dashboard#/o/dashboard#g" ${INSTALL_PATH}/esb/apis/dashboard/toolkit/tools.py
    /bin/cp -r ${INSTALL_PATH}/esb/apis/* /data/k8s-nfs/opsany-esb-code/
}

# MySQL Initialize
mysql_install(){
    shell_log "MySQL Config"
    sed -i "s/MYSQL_ROOT_PASSWORD/$MYSQL_ROOT_PASSWORD/g" ${INSTALL_PATH}/kubernetes/helm/opsany-base/mysql/values.yaml
    sed -i "s/REDIS_SERVER_PASSWORD/$REDIS_SERVER_PASSWORD/g" ${INSTALL_PATH}/kubernetes/helm/opsany-base/redis/values.yaml
    sed -i "s/MONGO_INITDB_ROOT_PASSWORD/$MONGO_INITDB_ROOT_PASSWORD/g" ${INSTALL_PATH}/kubernetes/helm/opsany-base/mongodb/values.yaml
}

# PaaS Service Start
paas_install(){
    #paas
    shell_log "Config paas Service"
    # PaaS Config
    sed -i "s/PAAS_LOGIN_IP/opsany-paas-login/g" ${INSTALL_PATH}/conf/opsany-paas/paas/settings_production.py.paas
    sed -i "s/PAAS_APPENGINE_IP/opsany-paas-appengine/g" ${INSTALL_PATH}/conf/opsany-paas/paas/settings_production.py.paas
    sed -i "s/DOMAIN_NAME/${DOMAIN_NAME}/g" ${INSTALL_PATH}/conf/opsany-paas/paas/settings_production.py.paas
    sed -i "s/LOCAL_IP/opsany-paas-openresty/g" ${INSTALL_PATH}/conf/opsany-paas/paas/settings_production.py.paas
    sed -i "s/MYSQL_SERVER_IP/${MYSQL_SERVER_IP}/g" ${INSTALL_PATH}/conf/opsany-paas/paas/settings_production.py.paas
    sed -i "s/MYSQL_OPSANY_PASSWORD/${MYSQL_OPSANY_PASSWORD}/g" ${INSTALL_PATH}/conf/opsany-paas/paas/settings_production.py.paas
    /bin/cp ${INSTALL_PATH}/conf/opsany-paas/paas/settings_production.py.paas ${INSTALL_PATH}/kubernetes/helm/opsany-paas/opsany-paas-paas/
    /bin/cp ${INSTALL_PATH}/conf/opsany-paas/paas/paas.ini ${INSTALL_PATH}/kubernetes/helm/opsany-paas/opsany-paas-paas/
}

login_install(){
    #login
    shell_log "Config login Service"
    # RBAC secret key for login
    RBAC_SECRET_KEY=$(uuid -v4)
    echo $RBAC_SECRET_KEY > ${INSTALL_PATH}/conf/.rbac_secret_key

    #Login Config
    sed -i "s/RBAC_SECRET_KEY/${RBAC_SECRET_KEY}/g" ${INSTALL_PATH}/conf/opsany-paas/login/settings_production.py.login
    sed -i "s/DOMAIN_NAME/${DOMAIN_NAME}/g" ${INSTALL_PATH}/conf/opsany-paas/login/settings_production.py.login
    sed -i "s/LOCAL_IP/${LOCAL_IP}/g" ${INSTALL_PATH}/conf/opsany-paas/login/settings_production.py.login
    sed -i "s/MYSQL_SERVER_IP/${MYSQL_SERVER_IP}/g" ${INSTALL_PATH}/conf/opsany-paas/login/settings_production.py.login
    sed -i "s/MYSQL_OPSANY_PASSWORD/${MYSQL_OPSANY_PASSWORD}/g" ${INSTALL_PATH}/conf/opsany-paas/login/settings_production.py.login
    /bin/cp ${INSTALL_PATH}/conf/opsany-paas/login/settings_production.py.login ${INSTALL_PATH}/kubernetes/helm/opsany-paas/opsany-paas-login/
    /bin/cp ${INSTALL_PATH}/conf/opsany-paas/login/login.ini ${INSTALL_PATH}/kubernetes/helm/opsany-paas/opsany-paas-login/
}
    
esb_install(){
    #esb
    shell_log "Config esb Service"
    # ESB Config
    sed -i "s/PAAS_LOGIN_IP/opsany-paas-login/g" ${INSTALL_PATH}/conf/opsany-paas/esb/settings_production.py.esb
    sed -i "s/PAAS_PAAS_IP/opsany-paas-paas/g" ${INSTALL_PATH}/conf/opsany-paas/esb/settings_production.py.esb
    sed -i "s/REDIS_SERVER_IP/${REDIS_SERVER_IP}/g" ${INSTALL_PATH}/conf/opsany-paas/esb/settings_production.py.esb
    sed -i "s/REDIS_SERVER_PASSWORD/${REDIS_SERVER_PASSWORD}/g" ${INSTALL_PATH}/conf/opsany-paas/esb/settings_production.py.esb
    sed -i "s/MYSQL_SERVER_IP/${MYSQL_SERVER_IP}/g" ${INSTALL_PATH}/conf/opsany-paas/esb/settings_production.py.esb
    sed -i "s/MYSQL_OPSANY_PASSWORD/${MYSQL_OPSANY_PASSWORD}/g" ${INSTALL_PATH}/conf/opsany-paas/esb/settings_production.py.esb
    /bin/cp ${INSTALL_PATH}/conf/opsany-paas/esb/settings_production.py.esb ${INSTALL_PATH}/kubernetes/helm/opsany-paas/opsany-paas-esb/
    /bin/cp ${INSTALL_PATH}/conf/opsany-paas/esb/esb.ini ${INSTALL_PATH}/kubernetes/helm/opsany-paas/opsany-paas-esb/
}

appengine_install(){
    #appengine
    # App Engine Config
    sed -i "s/MYSQL_SERVER_IP/${MYSQL_SERVER_IP}/g" ${INSTALL_PATH}/conf/opsany-paas/appengine/settings_production.py.appengine
    sed -i "s/MYSQL_OPSANY_PASSWORD/${MYSQL_OPSANY_PASSWORD}/g" ${INSTALL_PATH}/conf/opsany-paas/appengine/settings_production.py.appengine
    /bin/cp ${INSTALL_PATH}/conf/opsany-paas/appengine/settings_production.py.appengine ${INSTALL_PATH}/kubernetes/helm/opsany-paas/opsany-paas-appengine/
    /bin/cp ${INSTALL_PATH}/conf/opsany-paas/appengine/appengine.ini ${INSTALL_PATH}/kubernetes/helm/opsany-paas/opsany-paas-appengine/
    shell_log "Config appengine Service"
}  

websocket_install(){
    #websocket
    shell_log "Config websocket Service"
    BASTION_SECRET_KEY=$(uuid -v4)
    echo $BASTION_SECRET_KEY > ${INSTALL_PATH}/conf/.bastion_secret_key   
    # Websocket
    sed -i "s/BASTION_SECRET_KEY/${BASTION_SECRET_KEY}/g" ${INSTALL_PATH}/conf/opsany-paas/websocket/settings_production.py.websocket.init
    sed -i "s/WEBSOCKET_GUACD_HOST/opsany-paas-guacd/g" ${INSTALL_PATH}/conf/opsany-paas/websocket/settings_production.py.websocket
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
}

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
    /bin/cp ${INSTALL_PATH}/conf/proxy/invscript_proxy.py ${INSTALL_PATH}/kubernetes/helm/opsany-paas/opsany-paas-proxy/
    /bin/cp ${INSTALL_PATH}/conf/proxy/settings_production.py.proxy ${INSTALL_PATH}/kubernetes/helm/opsany-paas/opsany-paas-proxy/
}

grafana_install(){
    /bin/cp ${INSTALL_PATH}/conf/grafana/* ${INSTALL_PATH}/kubernetes/helm/opsany-paas/opsany-paas-grafana/
}

 openresty_install(){
     #openresty
    shell_log "Config openresty Service"
    # OpenResty
    sed -i "s/DOMAIN_NAME/${DOMAIN_NAME}/g" ${INSTALL_PATH}/conf/nginx-conf.d/opsany_paas_k8s.config
    sed -i "s/DOMAIN_NAME/${DOMAIN_NAME}/g" ${INSTALL_PATH}/conf/nginx-conf.d/opsany_proxy_k8s.config
    /bin/cp ${INSTALL_PATH}/conf/nginx-conf.d/opsany_paas_k8s.config ${INSTALL_PATH}/kubernetes/helm/opsany-paas/opsany-paas-openresty/opsany_paas.conf
    /bin/cp ${INSTALL_PATH}/conf/nginx-conf.d/opsany_proxy_k8s.config ${INSTALL_PATH}/kubernetes/helm/opsany-paas/opsany-paas-openresty/opsany_proxy.conf
    /bin/cp ${INSTALL_PATH}/conf/nginx-conf.d/ssl/${DOMAIN_NAME}.pem ${INSTALL_PATH}/kubernetes/helm/opsany-paas/opsany-paas-openresty/ssl/
    /bin/cp ${INSTALL_PATH}/conf/nginx-conf.d/ssl/${DOMAIN_NAME}.key ${INSTALL_PATH}/kubernetes/helm/opsany-paas/opsany-paas-openresty/ssl/
    shell_warning_log "======The end is the beginning.======"
}   

mysql_init(){
    shell_log "MySQL Initialize Begin"
    MYSQL_SERVER_IP=$(kubectl get svc opsany-base-mysql -n opsany | awk -F ' ' '{print $3}' | tail -1)
    export MYSQL_PWD=${MYSQL_ROOT_PASSWORD}
    mysql -h "${MYSQL_SERVER_IP}" -P ${MYSQL_SERVER_PORT} -u root  -p"${MYSQL_ROOT_PASSWORD}" -e "CREATE DATABASE opsany_paas DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;"
    mysql -h "${MYSQL_SERVER_IP}" -P ${MYSQL_SERVER_PORT} -u root  -p"${MYSQL_ROOT_PASSWORD}" -e "CREATE DATABASE opsany_proxy DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;"
    mysql -h "${MYSQL_SERVER_IP}" -P ${MYSQL_SERVER_PORT} -u root  -p"${MYSQL_ROOT_PASSWORD}" -e "CREATE USER 'opsany'@'%' identified by "\"${MYSQL_OPSANY_PASSWORD}\"";" 
    mysql -h "${MYSQL_SERVER_IP}" -P ${MYSQL_SERVER_PORT} -u root  -p"${MYSQL_ROOT_PASSWORD}" -e "grant all on opsany_paas.* to opsany@'%';" 
    mysql -h "${MYSQL_SERVER_IP}" -P ${MYSQL_SERVER_PORT} -u root  -p"${MYSQL_ROOT_PASSWORD}" -e "grant all on opsany_proxy.* to opsany@'%';" 
    
    #rbac
    mysql -h "${MYSQL_SERVER_IP}" -P ${MYSQL_SERVER_PORT} -u root -p"${MYSQL_ROOT_PASSWORD}" -e "create database rbac DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;"
    mysql -h "${MYSQL_SERVER_IP}" -P ${MYSQL_SERVER_PORT} -u root -p"${MYSQL_ROOT_PASSWORD}" -e "CREATE USER 'rbac'@'%' identified by "\"${MYSQL_OPSANY_RBAC_PASSWORD}\"";"
    mysql -h "${MYSQL_SERVER_IP}" -P ${MYSQL_SERVER_PORT} -u root -p"${MYSQL_ROOT_PASSWORD}" -e "grant all on rbac.* to rbac@'%';"
    
    #workbench
    mysql -h "${MYSQL_SERVER_IP}" -P ${MYSQL_SERVER_PORT} -u root -p"${MYSQL_ROOT_PASSWORD}" -e "create database workbench DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;"
    mysql -h "${MYSQL_SERVER_IP}" -P ${MYSQL_SERVER_PORT} -u root -p"${MYSQL_ROOT_PASSWORD}" -e "CREATE USER 'workbench'@'%' IDENTIFIED BY "\"${MYSQL_OPSANY_WORKBENCH_PASSWORD}\"";"
    mysql -h "${MYSQL_SERVER_IP}" -P ${MYSQL_SERVER_PORT} -u root -p"${MYSQL_ROOT_PASSWORD}" -e "grant all on workbench.* to workbench@'%';"
    
    #cmdb
    mysql -h "${MYSQL_SERVER_IP}" -P ${MYSQL_SERVER_PORT} -u root -p"${MYSQL_ROOT_PASSWORD}" -e "create database cmdb DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;"
    mysql -h "${MYSQL_SERVER_IP}" -P ${MYSQL_SERVER_PORT} -u root -p"${MYSQL_ROOT_PASSWORD}" -e "CREATE USER 'cmdb'@'%' IDENTIFIED BY "\"${MYSQL_OPSANY_CMDB_PASSWORD}\"";"
    mysql -h "${MYSQL_SERVER_IP}" -P ${MYSQL_SERVER_PORT} -u root -p"${MYSQL_ROOT_PASSWORD}" -e "grant all on cmdb.* to cmdb@'%';"
    
    #control
    mysql -h "${MYSQL_SERVER_IP}" -P ${MYSQL_SERVER_PORT} -u root -p"${MYSQL_ROOT_PASSWORD}" -e "create database control DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;"
    mysql -h "${MYSQL_SERVER_IP}" -P ${MYSQL_SERVER_PORT} -u root -p"${MYSQL_ROOT_PASSWORD}" -e "CREATE USER 'control'@'%' identified by "\"${MYSQL_OPSANY_CONTROL_PASSWORD}\"";"
    mysql -h "${MYSQL_SERVER_IP}" -P ${MYSQL_SERVER_PORT} -u root -p"${MYSQL_ROOT_PASSWORD}" -e "grant all on control.* to control@'%';"
    
    #job
    mysql -h "${MYSQL_SERVER_IP}" -P ${MYSQL_SERVER_PORT} -u root -p"${MYSQL_ROOT_PASSWORD}" -e "create database job DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;"
    mysql -h "${MYSQL_SERVER_IP}" -P ${MYSQL_SERVER_PORT} -u root -p"${MYSQL_ROOT_PASSWORD}" -e "CREATE USER 'job'@'%' identified by "\"${MYSQL_OPSANY_JOB_PASSWORD}\"";"
    mysql -h "${MYSQL_SERVER_IP}" -P ${MYSQL_SERVER_PORT} -u root -p"${MYSQL_ROOT_PASSWORD}" -e "grant all on job.* to job@'%';"
    
    #monitor
    mysql -h "${MYSQL_SERVER_IP}" -P ${MYSQL_SERVER_PORT} -u root -p"${MYSQL_ROOT_PASSWORD}" -e "create database monitor DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;"
    mysql -h "${MYSQL_SERVER_IP}" -P ${MYSQL_SERVER_PORT} -u root -p"${MYSQL_ROOT_PASSWORD}" -e "CREATE USER 'monitor'@'%' identified by "\"${MYSQL_OPSANY_MONITOR_PASSWORD}\"";"
    mysql -h "${MYSQL_SERVER_IP}" -P ${MYSQL_SERVER_PORT} -u root -p"${MYSQL_ROOT_PASSWORD}" -e "grant all on monitor.* to monitor@'%';" 
    
    #cmp
    mysql -h "${MYSQL_SERVER_IP}" -P ${MYSQL_SERVER_PORT} -u root -p"${MYSQL_ROOT_PASSWORD}" -e "create database cmp DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;"
    mysql -h "${MYSQL_SERVER_IP}" -P ${MYSQL_SERVER_PORT} -u root -p"${MYSQL_ROOT_PASSWORD}" -e "CREATE USER 'cmp'@'%' identified by "\"${MYSQL_OPSANY_CMP_PASSWORD}\"";"
    mysql -h "${MYSQL_SERVER_IP}" -P ${MYSQL_SERVER_PORT} -u root -p"${MYSQL_ROOT_PASSWORD}" -e "grant all on cmp.* to cmp@'%';" 
    
    #bastion
    mysql -h "${MYSQL_SERVER_IP}" -P ${MYSQL_SERVER_PORT} -u root -p"${MYSQL_ROOT_PASSWORD}" -e "create database bastion DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;"
    mysql -h "${MYSQL_SERVER_IP}" -P ${MYSQL_SERVER_PORT} -u root -p"${MYSQL_ROOT_PASSWORD}" -e "CREATE USER 'bastion'@'%' identified by "\"${MYSQL_OPSANY_BASTION_PASSWORD}\"";"
    mysql -h "${MYSQL_SERVER_IP}" -P ${MYSQL_SERVER_PORT} -u root -p"${MYSQL_ROOT_PASSWORD}" -e "grant all on bastion.* to bastion@'%';" 
    
    #devops
    mysql -h "${MYSQL_SERVER_IP}" -P ${MYSQL_SERVER_PORT} -u root -p"${MYSQL_ROOT_PASSWORD}" -e "create database devops DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;"
    mysql -h "${MYSQL_SERVER_IP}" -P ${MYSQL_SERVER_PORT} -u root -p"${MYSQL_ROOT_PASSWORD}" -e "CREATE USER 'devops'@'%' identified by "\"${MYSQL_OPSANY_DEVOPS_PASSWORD}\"";"
    mysql -h "${MYSQL_SERVER_IP}" -P ${MYSQL_SERVER_PORT} -u root -p"${MYSQL_ROOT_PASSWORD}" -e "grant all on devops.* to devops@'%';" 
    
    #code
    mysql -h "${MYSQL_SERVER_IP}" -P ${MYSQL_SERVER_PORT} -u root -p"${MYSQL_ROOT_PASSWORD}" -e "create database code DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;"
    mysql -h "${MYSQL_SERVER_IP}" -P ${MYSQL_SERVER_PORT} -u root -p"${MYSQL_ROOT_PASSWORD}" -e "CREATE USER 'code'@'%' identified by "\"${MYSQL_OPSANY_CODE_PASSWORD}\"";"
    mysql -h "${MYSQL_SERVER_IP}" -P ${MYSQL_SERVER_PORT} -u root -p"${MYSQL_ROOT_PASSWORD}" -e "grant all on code.* to code@'%';" 

    #pipeline
    mysql -h "${MYSQL_SERVER_IP}" -P ${MYSQL_SERVER_PORT} -u root -p"${MYSQL_ROOT_PASSWORD}" -e "create database pipeline DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;"
    mysql -h "${MYSQL_SERVER_IP}" -P ${MYSQL_SERVER_PORT} -u root -p"${MYSQL_ROOT_PASSWORD}" -e "CREATE USER 'pipeline'@'%' identified by "\"${MYSQL_OPSANY_PIPELINE_PASSWORD}\"";"
    mysql -h "${MYSQL_SERVER_IP}" -P ${MYSQL_SERVER_PORT} -u root -p"${MYSQL_ROOT_PASSWORD}" -e "grant all on pipeline.* to pipeline@'%';" 

    #repo
    mysql -h "${MYSQL_SERVER_IP}" -P ${MYSQL_SERVER_PORT} -u root -p"${MYSQL_ROOT_PASSWORD}" -e "create database repo DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;"
    mysql -h "${MYSQL_SERVER_IP}" -P ${MYSQL_SERVER_PORT} -u root -p"${MYSQL_ROOT_PASSWORD}" -e "CREATE USER 'repo'@'%' identified by "\"${MYSQL_OPSANY_REPO_PASSWORD}\"";"
    mysql -h "${MYSQL_SERVER_IP}" -P ${MYSQL_SERVER_PORT} -u root -p"${MYSQL_ROOT_PASSWORD}" -e "grant all on repo.* to repo@'%';" 

    #deploy
    mysql -h "${MYSQL_SERVER_IP}" -P ${MYSQL_SERVER_PORT} -u root -p"${MYSQL_ROOT_PASSWORD}" -e "create database deploy DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;"
    mysql -h "${MYSQL_SERVER_IP}" -P ${MYSQL_SERVER_PORT} -u root -p"${MYSQL_ROOT_PASSWORD}" -e "CREATE USER 'deploy'@'%' identified by "\"${MYSQL_OPSANY_DEPLOY_PASSWORD}\"";"
    mysql -h "${MYSQL_SERVER_IP}" -P ${MYSQL_SERVER_PORT} -u root -p"${MYSQL_ROOT_PASSWORD}" -e "grant all on deploy.* to deploy@'%';" 

    # create paas tables
    mysql -h "${MYSQL_SERVER_IP}" -P ${MYSQL_SERVER_PORT} -u root  opsany_paas < init/opsany-paas.sql
    mysql -h "${MYSQL_SERVER_IP}" -P ${MYSQL_SERVER_PORT} -u root -p"${MYSQL_ROOT_PASSWORD}" opsany_paas < ./init/esb-init/esb_api_doc.sql
    mysql -h "${MYSQL_SERVER_IP}" -P ${MYSQL_SERVER_PORT} -u root -p"${MYSQL_ROOT_PASSWORD}" opsany_paas < ./init/esb-init/esb_channel.sql
    mysql -h "${MYSQL_SERVER_IP}" -P ${MYSQL_SERVER_PORT} -u root -p"${MYSQL_ROOT_PASSWORD}" opsany_paas < ./init/esb-init/esb_component_system.sql
    mysql -h "${MYSQL_SERVER_IP}" -P ${MYSQL_SERVER_PORT} -u root -p"${MYSQL_ROOT_PASSWORD}" -e "show databases;"
    shell_log "MySQL Initialize End"
}

mongodb_init(){
    shell_log "======MongoDB Initialize Begin======"
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
    kubectl cp ${INSTALL_PATH}/init/mongodb-init/mongodb_init.js opsany-base-mongodb-0:/opt/ -n opsany
    kubectl cp ${INSTALL_PATH}/init/cmdb-init opsany-base-mongodb-0:/opt/ -n opsany
    kubectl exec -it opsany-base-mongodb-0 -n opsany -- mongosh -u root -p $MONGO_INITDB_ROOT_PASSWORD /opt/mongodb_init.js 
    kubectl exec -it opsany-base-mongodb-0 -n opsany -- bash -c "mongoimport -u cmdb -p ${MONGO_CMDB_PASSWORD} --db cmdb --drop --collection field_group < /opt/cmdb-init/field_group.json"
    kubectl exec -it opsany-base-mongodb-0 -n opsany -- bash -c "mongoimport -u cmdb -p ${MONGO_CMDB_PASSWORD} --db cmdb --drop --collection icon_model < /opt/cmdb-init/icon_model.json"
    kubectl exec -it opsany-base-mongodb-0 -n opsany -- bash -c "mongoimport -u cmdb -p ${MONGO_CMDB_PASSWORD} --db cmdb --drop --collection link_relationship_model < /opt/cmdb-init/link_relationship_model.json"
    kubectl exec -it opsany-base-mongodb-0 -n opsany -- bash -c "mongoimport -u cmdb -p ${MONGO_CMDB_PASSWORD} --db cmdb --drop --collection model_group < /opt/cmdb-init/model_group.json"
    kubectl exec -it opsany-base-mongodb-0 -n opsany -- bash -c "mongoimport -u cmdb -p ${MONGO_CMDB_PASSWORD} --db cmdb --drop --collection model_field < /opt/cmdb-init/model_field.json"
    kubectl exec -it opsany-base-mongodb-0 -n opsany -- bash -c "mongoimport -u cmdb -p ${MONGO_CMDB_PASSWORD} --db cmdb --drop --collection model_info < /opt/cmdb-init/model_info.json"
    shell_log "======MongoDB Initialize End======"
}


# Main
main(){
    case "$1" in
    mysql)
        mysql_init
        ;;
    mongodb)
        mongodb_init
        ;;
	install)
          install_check
          ssl_make
          opsany_init
          esb_init
          mysql_install
          paas_install
          login_install
          esb_install
          appengine_install
          websocket_install
          proxy_install
          grafana_install
          openresty_install
	  ;;
	help|*)
		echo $"Usage: $0 {install|help}"
	        ;;
    esac
}

main $1


