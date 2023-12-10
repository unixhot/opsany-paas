#!/bin/bash
#******************************************
# Author:       Jason Zhao
# Email:        zhaoshundong@opsany.com
# Organization: OpsAny https://www.opsany.com/
# Description:  Zabbix Server Install Script
#******************************************

# Data/Time
CTIME=$(date "+%Y-%m-%d-%H-%M")

# Shell Envionment Variables
CDIR=$(pwd)
SHELL_NAME="zabbix-install.sh"
SHELL_LOG="${SHELL_NAME}.log"
ADMIN_PASSWORD=""

# Install Inspection
if [ ! -f ./install.config ];then
      echo "Please Change Directory to ${INSTALL_PATH}/install"
      exit
else
    grep '^[A-Z]' install.config > install.env
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

# Check Install requirement
install_init(){
    # Configuration file write to DB
    pip3 install requests==2.25.1 grafana-api==1.0.3 mysql-connector==2.2.9 SQLAlchemy==1.4.22 \
             -i http://mirrors.aliyun.com/pypi/simple/ \
             --trusted-host mirrors.aliyun.com
    mkdir -p ${INSTALL_PATH}/{es-volume,zabbix-volume/alertscripts,zabbix-volume/externalscripts,zabbix-volume/snmptraps}
    mkdir -p ${INSTALL_PATH}/uploads/monitor/heartbeat-monitors.d
    chmod -R 777 ${INSTALL_PATH}/es-volume
    # Heartbeat
    sed -i "s/ES_SERVER_IP/${ES_SERVER_IP}/g" ${INSTALL_PATH}/conf/heartbeat.yml
    sed -i "s/ES_PASSWORD/${ES_PASSWORD}/g" ${INSTALL_PATH}/conf/heartbeat.yml
}

# Start Zabbix
zabbix_install(){
    shell_log "=====Start Zabbix======"
    docker run --restart=always --name opsany-zabbix-server-st2 -t \
      -e DB_SERVER_HOST="${MYSQL_SERVER_IP}" \
      -e MYSQL_DATABASE="${ZABBIX_DB_NAME}" \
      -e MYSQL_USER="${ZABBIX_DB_USER}" \
      -e MYSQL_PASSWORD="${ZABBIX_DB_PASSWORD}" \
      -e MYSQL_ROOT_PASSWORD="${MYSQL_ROOT_PASSWORD}" \
      -e ZBX_JAVAGATEWAY="zabbix-java-gateway" \
      -p 10051:10051 \
      -v ${INSTALL_PATH}/zabbix-volume/alertscripts:/usr/lib/zabbix/alertscripts \
      -v ${INSTALL_PATH}/zabbix-volume/externalscripts:/usr/lib/zabbix/externalscripts \
      -v ${INSTALL_PATH}/zabbix-volume/snmptraps:/var/lib/zabbix/snmptraps \
      -v /etc/localtime:/etc/localtime:ro \
      -d ${PAAS_DOCKER_REG}/zabbix-server-mysql:alpine-5.0-st2

    sleep 20
    
    docker run --restart=always --name opsany-zabbix-web -t \
      -e ZBX_SERVER_HOST="${MYSQL_SERVER_IP}" \
      -e DB_SERVER_HOST="${MYSQL_SERVER_IP}" \
      -e MYSQL_DATABASE="${ZABBIX_DB_NAME}" \
      -e MYSQL_USER="${ZABBIX_DB_USER}" \
      -e MYSQL_PASSWORD="${ZABBIX_DB_PASSWORD}" \
      -e MYSQL_ROOT_PASSWORD="${MYSQL_ROOT_PASSWORD}" \
      -v /etc/localtime:/etc/localtime:ro \
      -p 8006:8080 \
      -d ${PAAS_DOCKER_REG}/zabbix-web-nginx-mysql:alpine-5.0-latest
}

# Main
main(){
    case "$1" in
    zabbix)
        install_init
        zabbix_install
        ;;
	help|*)
		echo $"Usage: $0 {zabbix|help}"
	        ;;
esac
}

main $1
