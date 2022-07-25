#!/bin/bash
#******************************************
# Author:       Jason Zhao
# Email:        zhaoshundong@opsany.com
# Organization: OpsAny https://www.opsany.com/
# Description:  OpsAny ESB Update Script
#******************************************

# Get Data/Time
CTIME=$(date "+%Y-%m-%d-%H-%M")

# Shell Envionment Variables
CDIR=$(pwd)
SHELL_NAME="saas-esb-update.sh"
SHELL_LOG="${CDIR}/${SHELL_NAME}.log"

# Shell Log Record
shell_log(){
    LOG_INFO=$1
    echo "----------------$CTIME ${SHELL_NAME} : ${LOG_INFO}----------------"
    echo "$CTIME ${SHELL_NAME} : ${LOG_INFO}" >> ${SHELL_LOG}
}

# Install Inspection
if [ ! -f ./install.config ];then
      echo "Please Copy install.config and Change: cp install.config.example install.config"
      exit
else
    grep '^[A-Z]' install.config > install.env
    source ./install.env && rm -f install.env
fi


# ESB Update
esb_update(){
    shell_log "======ESB Update======"
    /bin/cp -r ../paas-ce/paas/esb/components/generic/apis/* ${INSTALL_PATH}/esb/apis/
    sed -i "s/DOMAIN_NAME/$DOMAIN_NAME/g" ${INSTALL_PATH}/esb/apis/cmdb/toolkit/configs.py
    sed -i "s#/t/cmdb#/o/cmdb#g" ${INSTALL_PATH}/esb/apis/cmdb/toolkit/tools.py
    sed -i "s/DOMAIN_NAME/$DOMAIN_NAME/g" ${INSTALL_PATH}/esb/apis/control/toolkit/configs.py
    sed -i "s#/t/control#/o/control#g" ${INSTALL_PATH}/esb/apis/control/toolkit/tools.py
    sed -i "s/DOMAIN_NAME/$DOMAIN_NAME/g" ${INSTALL_PATH}/esb/apis/rbac/toolkit/configs.py
    sed -i "s#/t/rbac#/o/rbac#g" ${INSTALL_PATH}/esb/apis/rbac/toolkit/configs.py
    sed -i "s/DOMAIN_NAME/$DOMAIN_NAME/g" ${INSTALL_PATH}/esb/apis/task/toolkit/configs.py
    sed -i "s#/t/job#/o/job#g" ${INSTALL_PATH}/esb/apis/task/toolkit/tools.py
    sed -i "s/DOMAIN_NAME/$DOMAIN_NAME/g" ${INSTALL_PATH}/esb/apis/workbench/toolkit/configs.py
    sed -i "s#/t/workbench#/o/workbench#g" ${INSTALL_PATH}/esb/apis/workbench/toolkit/tools.py
    sed -i "s/DOMAIN_NAME/$DOMAIN_NAME/g" ${INSTALL_PATH}/esb/apis/monitor/toolkit/configs.py
    sed -i "s#/t/monitor#/o/monitor#g" ${INSTALL_PATH}/esb/apis/monitor/toolkit/tools.py
    sed -i "s/DOMAIN_NAME/$DOMAIN_NAME/g" ${INSTALL_PATH}/esb/apis/cmp/toolkit/configs.py
    sed -i "s#/t/cmp#/o/cmp#g" ${INSTALL_PATH}/esb/apis/cmp/toolkit/tools.py
    sed -i "s/DOMAIN_NAME/$DOMAIN_NAME/g" ${INSTALL_PATH}/esb/apis/devops/toolkit/configs.py
    sed -i "s#/t/devops#/o/devops#g" ${INSTALL_PATH}/esb/apis/devops/toolkit/tools.py
    sed -i "s/DOMAIN_NAME/$DOMAIN_NAME/g" ${INSTALL_PATH}/esb/apis/bastion/toolkit/configs.py
    sed -i "s#/t/bastion#/o/bastion#g" ${INSTALL_PATH}/esb/apis/bastion/toolkit/configs.py
}

esb_restart(){
    mysql -h "${MYSQL_SERVER_IP}" -u root -p"${MYSQL_ROOT_PASSWORD}" opsany_paas < ./init/esb-init/esb_api_doc.sql
    mysql -h "${MYSQL_SERVER_IP}" -u root -p"${MYSQL_ROOT_PASSWORD}" opsany_paas < ./init/esb-init/esb_channel.sql
    mysql -h "${MYSQL_SERVER_IP}" -u root -p"${MYSQL_ROOT_PASSWORD}" opsany_paas < ./init/esb-init/esb_component_system.sql
    docker restart opsany-paas-esb
}

# Main
main(){
    esb_update
    esb_restart
}

main
