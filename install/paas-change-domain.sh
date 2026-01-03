#!/bin/bash
#******************************************
# Author:       Daoge、Jason Zhao
# Email:        zhaoshundong@opsany.com
# Description:  OpsAny PaaS Change Access Domain
#******************************************

# Get Data/Time
CTIME=$(date "+%Y-%m-%d-%H-%M")

# Shell Envionment Variables
CDIR=$(pwd)
SHELL_NAME="paas-change-domain.sh"
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
    echo -e "\031[32m---------------- $CTIME ${SHELL_NAME} : ${LOG_INFO} ----------------\033[0m"
    echo "$CTIME ${SHELL_NAME} : ${LOG_INFO}" >> ${SHELL_LOG}
}

# Install Inspection
if [ ! -f ./install.config ];then
      shell_error_log "Please Copy install.config and Change: cp install.config.example install.config"
      exit
else
    grep '^[A-Z]' install.config > install.env
    source ./install.env && rm -f install.env
fi

# Create Self-signed Server Certificate
ssl_make(){
    shell_log "======Init: Create Self-signed Server Certificate======"
    # create dir for ssl
    if [ ! -d ./conf/nginx-conf.d/ssl ];then
      mkdir -p ./conf/nginx-conf.d/ssl
    fi
    cp ./conf/openssl.cnf ./conf/nginx-conf.d/ssl/
    cd ./conf/nginx-conf.d/ssl
    openssl genrsa -des3 -passout pass:opsany -out $NEW_DOMAIN_NAME.key 2048 >/dev/null 2>&1

    #Create server certificate signing request
    SUBJECT="/C=CN/ST=BeiJing/L=BeiJing/O=BeiJing/OU=OpsAny/CN=OpsAny"
    openssl req -new -passin pass:opsany -subj $SUBJECT -key $NEW_DOMAIN_NAME.key -out $NEW_DOMAIN_NAME.csr >/dev/null 2>&1

    #Remove password
    mv $NEW_DOMAIN_NAME.key $NEW_DOMAIN_NAME.origin.key
    openssl rsa -passin pass:opsany -in $NEW_DOMAIN_NAME.origin.key  -out $NEW_DOMAIN_NAME.key >/dev/null 2>&1

    #Sign SSL certificate
    openssl x509 -req -days 3650 -extfile openssl.cnf -extensions 'v3_req'  -in $NEW_DOMAIN_NAME.csr -signkey $NEW_DOMAIN_NAME.key -out $NEW_DOMAIN_NAME.crt >/dev/null 2>&1
    openssl x509 -in ${NEW_DOMAIN_NAME}.crt -out ${NEW_DOMAIN_NAME}.pem -outform PEM >/dev/null 2>&1
    mv ${NEW_DOMAIN_NAME}.pem ${NEW_DOMAIN_NAME}.origin.pem
    cat ${NEW_DOMAIN_NAME}.key ${NEW_DOMAIN_NAME}.origin.pem > ${NEW_DOMAIN_NAME}.pem
    rm -f ./conf/openssl.cnf
}


replace_domain(){
    shell_log "Replace PaaS config files"
    # 替换默认安装文件中的配置
    sed -i "s/${OLD_DOMAIN_NAME}/${NEW_DOMAIN_NAME}/g" ${INSTALL_PATH}/conf/opsany-paas/login/settings_production.py.login
    sed -i "s/${OLD_DOMAIN_NAME}/${NEW_DOMAIN_NAME}/g" ${INSTALL_PATH}/conf/opsany-paas/paas/settings_production.py.paas
    sed -i "s/${OLD_DOMAIN_NAME}/${NEW_DOMAIN_NAME}/g" ${INSTALL_PATH}/conf/proxy/settings_production.py.proxy
    shell_log "替换nginx域名，替换后如无法访问，请自行检查nginx配置"
    sed -i "s/${OLD_DOMAIN_NAME}/${NEW_DOMAIN_NAME}/g" ${INSTALL_PATH}/conf/nginx-conf.d/opsany_paas.conf
    sed -i "s/${OLD_DOMAIN_NAME}/${NEW_DOMAIN_NAME}/g" ${INSTALL_PATH}/conf/nginx-conf.d/opsany_proxy.conf

    shell_log "Replace SaaS config files"
    # 替换已经安装的saas服务域名（可采用重新部署）
    sed -i "s/${OLD_DOMAIN_NAME}/${NEW_DOMAIN_NAME}/g"  ${INSTALL_PATH}/conf/opsany-saas/rbac/rbac-init.py
    sed -i "s/${OLD_DOMAIN_NAME}/${NEW_DOMAIN_NAME}/g"  ${INSTALL_PATH}/conf/opsany-saas/workbench/workbench-init.py
    sed -i "s/${OLD_DOMAIN_NAME}/${NEW_DOMAIN_NAME}/g"  ${INSTALL_PATH}/conf/opsany-saas/cmdb/cmdb-init.py
    sed -i "s/${OLD_DOMAIN_NAME}/${NEW_DOMAIN_NAME}/g"  ${INSTALL_PATH}/conf/opsany-saas/control/control-init.py
    sed -i "s/${OLD_DOMAIN_NAME}/${NEW_DOMAIN_NAME}/g"  ${INSTALL_PATH}/conf/opsany-saas/job/job-init.py
    sed -i "s/${OLD_DOMAIN_NAME}/${NEW_DOMAIN_NAME}/g"  ${INSTALL_PATH}/conf/opsany-saas/cmp/cmp-init.py
    sed -i "s/${OLD_DOMAIN_NAME}/${NEW_DOMAIN_NAME}/g"  ${INSTALL_PATH}/conf/opsany-saas/devops/devops-init.py
    sed -i "s/${OLD_DOMAIN_NAME}/${NEW_DOMAIN_NAME}/g"  ${INSTALL_PATH}/conf/opsany-saas/monitor/monitor-init.py
    sed -i "s/${OLD_DOMAIN_NAME}/${NEW_DOMAIN_NAME}/g"  ${INSTALL_PATH}/conf/opsany-saas/bastion/bastion-init.py
    sed -i "s/${OLD_DOMAIN_NAME}/${NEW_DOMAIN_NAME}/g"  ${INSTALL_PATH}/conf/opsany-saas/dashboard/dashboard-init.py
    sed -i "s/${OLD_DOMAIN_NAME}/${NEW_DOMAIN_NAME}/g"  ${INSTALL_PATH}/conf/opsany-saas/repo/repo-init.py
    sed -i "s/${OLD_DOMAIN_NAME}/${NEW_DOMAIN_NAME}/g"  ${INSTALL_PATH}/conf/opsany-saas/pipeline/pipeline-init.py
    sed -i "s/${OLD_DOMAIN_NAME}/${NEW_DOMAIN_NAME}/g"  ${INSTALL_PATH}/conf/opsany-saas/deploy/deploy-init.py
    sed -i "s/${OLD_DOMAIN_NAME}/${NEW_DOMAIN_NAME}/g"  ${INSTALL_PATH}/conf/opsany-saas/code/code-init.py
}

restart_paas(){
    service_list='opsany-paas-paas opsany-paas-login opsany-paas-esb opsany-paas-appengine opsany-paas-websocket opsany-paas-proxy opsany-base-openresty'
    for service in $service_list;do
        shell_log "Restart $service" && docker restart $service;
    done
}
restart_saas(){
    service_list='opsany-saas-ce-rbac opsany-saas-ce-workbench opsany-saas-ce-cmdb opsany-saas-ce-control opsany-saas-ce-job opsany-saas-ce-monitor opsany-saas-ce-devops opsany-saas-ce-cmp opsany-saas-ce-bastion opsany-saas-ce-pipeline opsany-saas-ce-deploy opsany-saas-ce-repo'
    for service in $service_list;do
        shell_log "Restart $service" && docker restart $service;
    done
}

main(){
    # Setting the Old Domain name
    OLD_DOMAIN_NAME=$1

    # Setting the New Domain name
    NEW_DOMAIN_NAME=$2

    if [ -z "${OLD_DOMAIN_NAME}" -o -z "${NEW_DOMAIN_NAME}" ];then
        shell_warning_log "./paas-change-domain.sh old_domanin_name new_domain_name"
        exit 1
    fi
    ssl_make
    replace_domain;
    restart_paas;
    restart_saas;
}

main $1 $2
