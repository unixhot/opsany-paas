#!/bin/bash
#******************************************
# Author:       Jason Zhao
# Email:        zhaoshundong@opsany.com
# Organization: OpsAny https://www.opsany.com/
# Description:  OpsAny SAAS DevOps Install Script
#******************************************

# Data/Time
CTIME=$(date "+%Y-%m-%d-%H-%M")

# Shell Envionment Variables
CDIR=$(pwd)
SHELL_NAME="saas-devops-install.sh"
SHELL_LOG="${SHELL_NAME}.log"

# Check SAAS Package
if [ ! -d ../../opsany-saas ];then
    echo "======Download the SAAS package first======"
    exit;
fi

# Install Inspection
if [ ! -f ./install.config ];then
      echo "Please Change Directory to ${INSTALL_PATH}/install"
      exit
else
    grep '^[A-Z]' install.config > install.env
    source ./install.env && rm -f install.env
fi

# Shell Log Record
shell_log(){
    LOG_INFO=$1
    echo "----------------$CTIME ${SHELL_NAME} : ${LOG_INFO}----------------"
    echo "$CTIME ${SHELL_NAME} : ${LOG_INFO}" >> ${SHELL_LOG}
}

# SaaS DB Initialize
mysql_init(){
    shell_log "======MySQL Initialize======"
    cd ${CDIR}
    #devops
    mysql -h "${MYSQL_SERVER_IP}" -u root -p"${MYSQL_ROOT_PASSWORD}" -e "create database devops DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;"
    mysql -h "${MYSQL_SERVER_IP}" -u root -p"${MYSQL_ROOT_PASSWORD}" -e "create database deploy DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;"
    mysql -h "${MYSQL_SERVER_IP}" -u root -p"${MYSQL_ROOT_PASSWORD}" -e "create database pipeline DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;"
    mysql -h "${MYSQL_SERVER_IP}" -u root -p"${MYSQL_ROOT_PASSWORD}" -e "create database repo DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;"
    mysql -h "${MYSQL_SERVER_IP}" -u root -p"${MYSQL_ROOT_PASSWORD}" -e "grant all on devops.* to devops@'%' identified by "\"${MYSQL_OPSANY_DEVOPS_PASSWORD}\"";"
    mysql -h "${MYSQL_SERVER_IP}" -u root -p"${MYSQL_ROOT_PASSWORD}" -e "grant all on deploy.* to devops@'%' identified by "\"${MYSQL_OPSANY_DEVOPS_PASSWORD}\"";"
    mysql -h "${MYSQL_SERVER_IP}" -u root -p"${MYSQL_ROOT_PASSWORD}" -e "grant all on pipeline.* to devops@'%' identified by "\"${MYSQL_OPSANY_DEVOPS_PASSWORD}\"";"
    mysql -h "${MYSQL_SERVER_IP}" -u root -p"${MYSQL_ROOT_PASSWORD}" -e "grant all on repo.* to devops@'%' identified by "\"${MYSQL_OPSANY_DEVOPS_PASSWORD}\"";"
    mysql -h "${MYSQL_SERVER_IP}" -u root -p"${MYSQL_ROOT_PASSWORD}" -e "grant all on devops.* to opsany@'%' identified by "\"${MYSQL_OPSANY_PASSWORD}\"";"
    mysql -h "${MYSQL_SERVER_IP}" -u root -p"${MYSQL_ROOT_PASSWORD}" -e "grant all on deploy.* to opsany@'%' identified by "\"${MYSQL_OPSANY_PASSWORD}\"";"
    mysql -h "${MYSQL_SERVER_IP}" -u root -p"${MYSQL_ROOT_PASSWORD}" -e "grant all on pipeline.* to opsany@'%' identified by "\"${MYSQL_OPSANY_PASSWORD}\"";"
    mysql -h "${MYSQL_SERVER_IP}" -u root -p"${MYSQL_ROOT_PASSWORD}" -e "grant all on repo.* to opsany@'%' identified by "\"${MYSQL_OPSANY_PASSWORD}\"";"

}

# workbench nav icon, app list icon
copy_logo(){
  cd $CDIR
  /bin/cp -r ../paas-ce/saas/saas-logo/* /opt/opsany/uploads/workbench/icon/
  /bin/cp -r ../paas-ce/saas/saas-logo/* /opt/opsany-paas/paas-ce/paas/paas/media/applogo/
}


# SaaS Deploy
saas_deploy(){
    cd $CDIR
    cd ../../opsany-saas/
    /bin/cp *.tar.gz ../opsany-paas/saas/
    cd $CDIR
    cd ../saas/ && ls *.tar.gz
    if [ $? -ne 0 ];then
        echo "Please Download SAAS first" && exit
    fi
    python3 deploy.py --domain $DOMAIN_NAME --username admin --password admin --file_name devops-opsany-*.tar.gz
    python3 deploy.py --domain $DOMAIN_NAME --username admin --password admin --file_name deploy-opsany-*.tar.gz
    python3 deploy.py --domain $DOMAIN_NAME --username admin --password admin --file_name pipeline-opsany-*.tar.gz
    #python3 deploy.py --domain $DOMAIN_NAME --username admin --password admin --file_name repo-opsany-*.tar.gz
    python3 init-ce-devops.py --domain https://${DOMAIN_NAME} --username admin  --password admin
    shell_log "======OpsAny: Make Ops Perfect======"

}

# Main
main(){
    mysql_init
    copy_logo
    saas_deploy
}

main
