#!/bin/bash
#******************************************
# Author:       Jason Zhao
# Email:        zhaoshundong@opsany.com
# Organization: OpsAny https://www.opsany.com/
# Description:  OpsAny SAAS Monitor Install Script
#******************************************

# Data/Time
CTIME=$(date "+%Y-%m-%d-%H-%M")

# Shell Envionment Variables
CDIR=$(pwd)
SHELL_NAME="saas-monitor-install.sh"
SHELL_LOG="${SHELL_NAME}.log"

# Check SAAS Package
if [ ! -d ../../opsany-saas ];then
    echo "======Download the SAAS package first======"
    exit;
fi

# Configuration file write to DB
pip3 install requests==2.25.1 grafana-api==1.0.3 mysql-connector==2.2.9 SQLAlchemy==1.4.22 \
             -i http://mirrors.aliyun.com/pypi/simple/ \
             --trusted-host mirrors.aliyun.com

# Install Inspection
if [ ! -f ./install.config ];then
      echo "Please Change Directory to ${INSTALL_PATH}/install"
      exit
else
    grep '^[A-Z]' install.config > install.env
    source ./install.env && rm -f install.env
    #/bin/cp -r conf ${INSTALL_PATH}/
fi

# Shell Log Record
shell_log(){
    LOG_INFO=$1
    echo "----------------$CTIME ${SHELL_NAME} : ${LOG_INFO}----------------"
    echo "$CTIME ${SHELL_NAME} : ${LOG_INFO}" >> ${SHELL_LOG}
}

# Check Install requirement
saas_init(){
    mkdir -p ${INSTALL_PATH}/{zabbix-volume/alertscripts,zabbix-volume/externalscripts,zabbix-volume/snmptraps,grafana-volume/plugins}
    mkdir -p ${INSTALL_PATH}/uploads/monitor/heartbeat-monitors.d
}

# Start Zabbix
zabbix_install(){
    shell_log "=====Start Zabbix======"
    docker run --restart=always --name opsany-zabbix-server -t \
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
      -d ${PAAS_DOCKER_REG}/zabbix-server-mysql:alpine-5.0-latest

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

# Start Grafana
grafana_install(){
    # Grafana
    shell_log "=====Start Grafana======"
    docker run -d --restart=always --name opsany-grafana \
    -v ${INSTALL_PATH}/conf/grafana/grafana.ini:/etc/grafana/grafana.ini \
    -v ${INSTALL_PATH}/conf/grafana/grafana.key:/etc/grafana/grafana.key \
    -v ${INSTALL_PATH}/conf/grafana/grafana.pem:/etc/grafana/grafana.pem \
    -v /etc/localtime:/etc/localtime:ro \
    -p 8007:3000 \
    ${PAAS_DOCKER_REG}/opsany-grafana:7.3.5
}

# Start Elasticsearch
es_install(){
    #Elasticsearch
    shell_log "====Start Elasticsearch"
    docker run -d --restart=always --name opsany-elasticsearch \
    -e "discovery.type=single-node" \
    -e "ELASTIC_PASSWORD=${ES_PASSWORD}" \
    -e "xpack.license.self_generated.type=trial" \
    -e "xpack.security.enabled=true" \
    -e "bootstrap.memory_lock=true" \
    -e "ES_JAVA_OPTS=-Xms512m -Xmx512m" \
    -v /etc/localtime:/etc/localtime:ro \
    -p 9200:9200 -p 9300:9300 \
    ${PAAS_DOCKER_REG}/elasticsearch:7.12.0
    
    #heartbeat
    shell_log "====Start Heartbeat===="
    docker run -d --restart=always --name opsany-heartbeat \
    -v ${INSTALL_PATH}/conf/heartbeat.yml:/etc/heartbeat/heartbeat.yml \
    -v ${INSTALL_PATH}/uploads/monitor/heartbeat-monitors.d:/etc/heartbeat/monitors.d \
    -v ${INSTALL_PATH}/logs:/var/log/heartbeat \
    -v /etc/localtime:/etc/localtime:ro \
    ${PAAS_DOCKER_REG}/opsany-heartbeat:7.13.2
    
}

# SaaS DB Initialize
mysql_init(){
    shell_log "======MySQL Initialize======"
    
    #monitor
    mysql -h "${MYSQL_SERVER_IP}" -u root -p"${MYSQL_ROOT_PASSWORD}" -e "create database monitor DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;"
    mysql -h "${MYSQL_SERVER_IP}" -u root -p"${MYSQL_ROOT_PASSWORD}" -e "grant all on monitor.* to monitor@'%' identified by "\"${MYSQL_OPSANY_MONITOR_PASSWORD}\"";"
    mysql -h "${MYSQL_SERVER_IP}" -u root -p"${MYSQL_ROOT_PASSWORD}" -e "grant all on monitor.* to opsany@'%' identified by "\"${MYSQL_OPSANY_PASSWORD}\"";" 
    
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
    python3 deploy.py --domain $DOMAIN_NAME --username admin --password admin --file_name monitor-opsany-*.tar.gz
    #python3 deploy.py --domain $DOMAIN_NAME --username admin --password admin --file_name log-opsany-*.tar.gz
    #python3 deploy.py --domain $DOMAIN_NAME --username admin --password admin --file_name apm-opsany-*.tar.gz
    python3 init-ce-monitor.py --domain $DOMAIN_NAME --private_ip $LOCAL_IP --paas_username admin --paas_password admin --zabbix_password zabbix --grafana_password admin --zabbix_api_password OpsAny@2020 --modify_zabbix_password OpsAny@2020 --modify_grafana_password OpsAny@2020
}

# Main
main(){
    saas_init
    mysql_init
    zabbix_install
    grafana_install
    es_install
    saas_deploy
}

main
