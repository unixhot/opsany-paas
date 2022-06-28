#!/bin/bash
#******************************************
# Author:       Jason Zhao
# Email:        zhaoshundong@opsany.com
# Organization: OpsAny https://www.opsany.com/
# Description:  OpsAny SAAS Dashboard Install Script
#******************************************

# Data/Time
CTIME=$(date "+%Y-%m-%d-%H-%M")

# Shell Envionment Variables
CDIR=$(pwd)
PAAS_DIR="/opt/opsany-paas/"
SHELL_NAME="dashboard-install.sh"
SHELL_LOG="${SHELL_NAME}.log"
ADMIN_PASSWORD=""
MYSQL_OPSANY_DASHBOARD_PASSWORD="OpsAny@2020"

# Check SAAS Package
if [ ! -d /opt/opsany-saas ];then
    echo "======Download the SAAS package first======"
    exit;
fi

# Install Inspection
if [ ! -f "$PAAS_DIR"/install/install.config ];then
      echo "Please Change Directory to ${PAAS_DIR}/install"
      exit
else
    grep '^[A-Z]' "$PAAS_DIR"/install/install.config > install.env
    source ./install.env && rm -f install.env
    if [ -z "$ADMIN_PASSWORD" ];then
        source ${INSTALL_PATH}/conf/.passwd_env
    fi
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
    #dashbaord
    mysql -h "${MYSQL_SERVER_IP}" -u root -p"${MYSQL_ROOT_PASSWORD}" -e "create database dashboard DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;"
    mysql -h "${MYSQL_SERVER_IP}" -u root -p"${MYSQL_ROOT_PASSWORD}" -e "grant all on dashboard.* to dashboard@'%' identified by "\"${MYSQL_OPSANY_DASHBOARD_PASSWORD}\"";"
    mysql -h "${MYSQL_SERVER_IP}" -u root -p"${MYSQL_ROOT_PASSWORD}" -e "grant all on dashboard.* to opsany@'%' identified by "\"${MYSQL_OPSANY_PASSWORD}\"";" 
    
}

# SaaS Env
saas_env(){
    shell_log "======Add SaaS Env======"
    python3 add_env_script.py --mysql_host ${MYSQL_SERVER_IP} --mysql_username root --mysql_password ${MYSQL_ROOT_PASSWORD} --config_file_path ./dashboard.config
}

# SaaS Deploy
saas_deploy(){
    shell_log "======Dashboard SaaS Deploy======"
    cd $CDIR 
    if [ ! -f dashboard-opsany-1.6.0.tar.gz ];then
        wget https://opsany-saas.oss-cn-beijing.aliyuncs.com/dashboard-opsany-1.6.0.tar.gz
    fi
    python3 saas_deploy_add.py --domain $DOMAIN_NAME --username admin --password ${ADMIN_PASSWORD} --file_name dashboard-opsany-*.tar.gz
}

saas_init(){
    # Add Nav
    python3 add_nav_script.py --paas_domain https://$DOMAIN_NAME --paas_username admin --paas_password ${ADMIN_PASSWORD} --config_file_path ./dashboard.config
}

# Main
main(){
    case "$1" in
        install)
        mysql_init
        saas_env
        saas_deploy
        saas_init
        ;;
	help|*)
            echo $"Usage: $0 {install|help}"
	    ;;
    esac
}

main $1
