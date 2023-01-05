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
SHELL_NAME="proxy-install.sh"
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
    setenforce 0
fi

replace_domain(){
    shell_log "Replace PaaS config files"
    # 替换默认安装文件中的配置
    sed -i "s/${OLD_DOMAIN_NAME}/${NEW_DOMAIN_NAME}/g" ${INSTALL_PATH}/esb/apis/cmdb/toolkit/configs.py
    sed -i "s/${OLD_DOMAIN_NAME}/${NEW_DOMAIN_NAME}/g" ${INSTALL_PATH}/esb/apis/control/toolkit/configs.py
    sed -i "s/${OLD_DOMAIN_NAME}/${NEW_DOMAIN_NAME}/g" ${INSTALL_PATH}/esb/apis/rbac/toolkit/configs.py
    sed -i "s/${OLD_DOMAIN_NAME}/${NEW_DOMAIN_NAME}/g" ${INSTALL_PATH}/esb/apis/task/toolkit/configs.py
    sed -i "s/${OLD_DOMAIN_NAME}/${NEW_DOMAIN_NAME}/g" ${INSTALL_PATH}/esb/apis/workbench/toolkit/configs.py
    sed -i "s/${OLD_DOMAIN_NAME}/${NEW_DOMAIN_NAME}/g" ${INSTALL_PATH}/esb/apis/monitor/toolkit/configs.py
    sed -i "s/${OLD_DOMAIN_NAME}/${NEW_DOMAIN_NAME}/g" ${INSTALL_PATH}/esb/apis/cmp/toolkit/configs.py
    sed -i "s/${OLD_DOMAIN_NAME}/${NEW_DOMAIN_NAME}/g" ${INSTALL_PATH}/esb/apis/devops/toolkit/configs.py
    sed -i "s/${OLD_DOMAIN_NAME}/${NEW_DOMAIN_NAME}/g" ${INSTALL_PATH}/esb/apis/bastion/toolkit/configs.py
    sed -i "s/${OLD_DOMAIN_NAME}/${NEW_DOMAIN_NAME}/g" ${INSTALL_PATH}/conf/settings_production.py.paas
    sed -i "s/${OLD_DOMAIN_NAME}/${NEW_DOMAIN_NAME}/g" ${INSTALL_PATH}/conf/settings_production.py.login
    sed -i "s/${OLD_DOMAIN_NAME}/${NEW_DOMAIN_NAME}/g" ${INSTALL_PATH}/conf/proxy/settings_production.py.proxy
    shell_log "替换nginx域名，替换后如无法访问，请自行检查nginx配置"
    sed -i "s/${OLD_DOMAIN_NAME}/${NEW_DOMAIN_NAME}/g" ${INSTALL_PATH}/conf/nginx-conf.d/nginx_paas.conf


    shell_log "Replace SaaS config files"
    # 替换已经安装的saas服务域名（可采用重新部署）
    sed -i "s/${OLD_DOMAIN_NAME}/${NEW_DOMAIN_NAME}/g"  ${INSTALL_PATH}/saas/apps/projects/rbac/conf/supervisord.conf
    sed -i "s/${OLD_DOMAIN_NAME}/${NEW_DOMAIN_NAME}/g"  ${INSTALL_PATH}/saas/apps/projects/workbench/conf/supervisord.conf
    sed -i "s/${OLD_DOMAIN_NAME}/${NEW_DOMAIN_NAME}/g"  ${INSTALL_PATH}/saas/apps/projects/cmdb/conf/supervisord.conf
    sed -i "s/${OLD_DOMAIN_NAME}/${NEW_DOMAIN_NAME}/g"  ${INSTALL_PATH}/saas/apps/projects/control/conf/supervisord.conf
    sed -i "s/${OLD_DOMAIN_NAME}/${NEW_DOMAIN_NAME}/g"  ${INSTALL_PATH}/saas/apps/projects/job/conf/supervisord.conf
    sed -i "s/${OLD_DOMAIN_NAME}/${NEW_DOMAIN_NAME}/g"  ${INSTALL_PATH}/saas/apps/projects/cmp/conf/supervisord.conf
    sed -i "s/${OLD_DOMAIN_NAME}/${NEW_DOMAIN_NAME}/g"  ${INSTALL_PATH}/saas/apps/projects/devops/conf/supervisord.conf
    sed -i "s/${OLD_DOMAIN_NAME}/${NEW_DOMAIN_NAME}/g"  ${INSTALL_PATH}/saas/apps/projects/monitor/conf/supervisord.conf
    sed -i "s/${OLD_DOMAIN_NAME}/${NEW_DOMAIN_NAME}/g"  ${INSTALL_PATH}/saas/apps/projects/bastion/conf/supervisord.conf
    sed -i "s/${OLD_DOMAIN_NAME}/${NEW_DOMAIN_NAME}/g"  ${INSTALL_PATH}/saas/apps/projects/pipeline/conf/supervisord.conf
    sed -i "s/${OLD_DOMAIN_NAME}/${NEW_DOMAIN_NAME}/g"  ${INSTALL_PATH}/saas/apps/projects/deploy/conf/supervisord.conf

}

restart_paas(){
    service_list='opsany-paas-paas opsany-paas-login opsany-paas-esb opsany-paas-appengine opsany-paas-websocket opsany-paas-paasagent'
    for service in $service_list;do
        shell_log "Restart $service" && docker restart $service;
    done
}

restart_saas(){
    cd /opt/opsany-paas/install && /bin/bash ./saas-restart.sh 
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
    replace_domain;
    restart_paas;
    restart_saas;
}

main $1 $2
