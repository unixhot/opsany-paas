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

# Check Install requirement
install_init(){
    shell_log "=====Begin: Init======"
    # Configuration file write to DB
    pip3 install requests==2.25.1 grafana-api==1.0.3 mysql-connector==2.2.9 SQLAlchemy==1.4.22 \
             -i http://mirrors.aliyun.com/pypi/simple/ \
             --trusted-host mirrors.aliyun.com
    mkdir -p ${INSTALL_PATH}/{zabbix-volume/alertscripts,zabbix-volume/externalscripts,zabbix-volume/snmptraps}
    mkdir -p ${INSTALL_PATH}/{zabbix-mysql8-volume,conf/mysql8,logs/mysql8}
    /bin/cp ./conf/mysqld.cnf ${INSTALL_PATH}/conf/mysql8/mysqld.cnf
}

# Start Zabbix
zabbix_5_0_install(){
    shell_log "=====Start Zabbix 5.0LTS======"
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
    # Jenkins Master
    docker run --restart=always --name opsany-devops-jenkins -t \
      -v /etc/localtime:/etc/localtime:ro \
      -v ${INSTALL_PATH}/jenkins-home:/var/jenkins_home \
      -p 8008:8080 -p 8009:5000 \
      -d ${PAAS_DOCKER_REG}/jenkins:2.452.2-lts
}

zabbix_6_0_install(){

    shell_log "=====Start mysql 8.0======"
    docker run -d --restart=always --name opsany-zabbix-mysql8 \
    -e MYSQL_ROOT_PASSWORD="$MYSQL_ROOT_PASSWORD" \
    -p 3307:3306 -v ${INSTALL_PATH}/zabbix-mysql8-volume:/var/lib/mysql \
    -v ${INSTALL_PATH}/conf/mysql8/mysqld.cnf:/etc/mysql/mysql.conf.d/mysqld.cnf \
    -v ${INSTALL_PATH}/logs/mysql8:/var/log/mysql \
    -v /etc/localtime:/etc/localtime:ro \
    ${PAAS_DOCKER_REG}/mysql:8.0 --character-set-server=utf8 --collation-server=utf8_general_ci



    shell_log "=====Start Zabbix 6.0 LTS======"
    docker run --restart=always --name opsany-zabbix-server-6.0 -t \
      -e DB_SERVER_HOST="${MYSQL_SERVER_IP}" \
      -e DB_SERVER_PORT="3307" \
      -e MYSQL_DATABASE="${ZABBIX_DB_NAME}" \
      -e MYSQL_USER="${ZABBIX_DB_USER}" \
      -e MYSQL_PASSWORD="${ZABBIX_DB_PASSWORD}" \
      -e MYSQL_ROOT_PASSWORD="${MYSQL_ROOT_PASSWORD}" \
      -p 10051:10051 \
      -v ${INSTALL_PATH}/zabbix-volume/alertscripts:/usr/lib/zabbix/alertscripts \
      -v ${INSTALL_PATH}/zabbix-volume/externalscripts:/usr/lib/zabbix/externalscripts \
      -v ${INSTALL_PATH}/zabbix-volume/snmptraps:/var/lib/zabbix/snmptraps \
      -v /etc/localtime:/etc/localtime:ro \
      -d ${PAAS_DOCKER_REG}/zabbix-server-mysql:6.0-centos-latest


    sleep 20
    
    docker run --restart=always --name opsany-zabbix-web-6.0 -t \
      -e ZBX_SERVER_HOST="${MYSQL_SERVER_IP}" \
      -e DB_SERVER_HOST="${MYSQL_SERVER_IP}" \
      -e DB_SERVER_PORT="3307" \
      -e MYSQL_DATABASE="${ZABBIX_DB_NAME}" \
      -e MYSQL_USER="${ZABBIX_DB_USER}" \
      -e MYSQL_PASSWORD="${ZABBIX_DB_PASSWORD}" \
      -e MYSQL_ROOT_PASSWORD="${MYSQL_ROOT_PASSWORD}" \
      -v /etc/localtime:/etc/localtime:ro \
      -p 8006:8080 \
      -d ${PAAS_DOCKER_REG}/zabbix-web-nginx-mysql:6.0-centos-latest
      

}

zabbix_7_0_install(){

    shell_log "=====Start mysql 8.0======"
    docker run -d --restart=always --name opsany-zabbix-mysql8 \
    -e MYSQL_ROOT_PASSWORD="$MYSQL_ROOT_PASSWORD" \
    -p 3307:3306 -v ${INSTALL_PATH}/zabbix-mysql8-volume:/var/lib/mysql \
    -v ${INSTALL_PATH}/conf/mysql8/mysqld.cnf:/etc/mysql/mysql.conf.d/mysqld.cnf \
    -v ${INSTALL_PATH}/logs/mysql8:/var/log/mysql \
    -v /etc/localtime:/etc/localtime:ro \
    ${PAAS_DOCKER_REG}/mysql:8.0 --character-set-server=utf8 --collation-server=utf8_general_ci --default-authentication-plugin=caching_sha2_password



   shell_log "=====Start Zabbix 7.0 LTS======"
   docker run --restart=always --name opsany-zabbix-server-7.0 -t \
     -e DB_SERVER_HOST="${MYSQL_SERVER_IP}" \
     -e DB_SERVER_PORT="3307" \
     -e MYSQL_DATABASE="${ZABBIX_DB_NAME}" \
     -e MYSQL_USER="${ZABBIX_DB_USER}" \
     -e MYSQL_PASSWORD="${ZABBIX_DB_PASSWORD}" \
     -e MYSQL_ROOT_PASSWORD="${MYSQL_ROOT_PASSWORD}" \
     -p 10051:10051 \
     -v ${INSTALL_PATH}/zabbix-volume/alertscripts:/usr/lib/zabbix/alertscripts \
     -v ${INSTALL_PATH}/zabbix-volume/externalscripts:/usr/lib/zabbix/externalscripts \
     -v ${INSTALL_PATH}/zabbix-volume/snmptraps:/var/lib/zabbix/snmptraps \
     -v /etc/localtime:/etc/localtime:ro \
     -d ${PAAS_DOCKER_REG}/zabbix-server-mysql:7.0-centos-latest


   sleep 20
   
   docker run --restart=always --name opsany-zabbix-web-7.0 -t \
     -e ZBX_SERVER_HOST="${MYSQL_SERVER_IP}" \
     -e DB_SERVER_HOST="${MYSQL_SERVER_IP}" \
     -e DB_SERVER_PORT="3307" \
     -e MYSQL_DATABASE="${ZABBIX_DB_NAME}" \
     -e MYSQL_USER="${ZABBIX_DB_USER}" \
     -e MYSQL_PASSWORD="${ZABBIX_DB_PASSWORD}" \
     -e MYSQL_ROOT_PASSWORD="${MYSQL_ROOT_PASSWORD}" \
     -v /etc/localtime:/etc/localtime:ro \
     -p 8006:8080 \
     -d ${PAAS_DOCKER_REG}/zabbix-web-nginx-mysql:7.0-centos-latest
     

}

zabbix_uninstall5(){
    shell_log "=====Uninstall Zabbix 5.0======"
    docker stop opsany-zabbix-web
    docker stop opsany-zabbix-server-st2
    docker rm opsany-zabbix-web
    docker rm opsany-zabbix-server-st2
    rm -rf ${INSTALL_PATH}/zabbix-volume
}

zabbix_uninstall6(){
    shell_log "=====Uninstall Zabbix 6.0======"
    docker stop opsany-zabbix-web-6.0
    docker stop opsany-zabbix-server-6.0
    docker stop opsany-zabbix-mysql8
    docker rm opsany-zabbix-web-6.0
    docker rm opsany-zabbix-server-6.0
    docker rm opsany-zabbix-mysql8
    rm -rf ${INSTALL_PATH}/{zabbix-volume,logs/mysql8,conf/mysql8,zabbix-mysql8-volume}
}

zabbix_uninstall7(){
    shell_log "=====Uninstall Zabbix 7.0======"
    docker stop opsany-zabbix-web-7.0
    docker stop opsany-zabbix-server-7.0
    docker stop opsany-zabbix-mysql8
    docker rm opsany-zabbix-web-7.0
    docker rm opsany-zabbix-server-7.0
    docker rm opsany-zabbix-mysql8
    rm -rf ${INSTALL_PATH}/{zabbix-volume,logs/mysql8,conf/mysql8,zabbix-mysql8-volume}
}

# Main
main(){
    case "$1" in
    5.0)
        install_init
        zabbix_5_0_install
        ;;
    6.0)
        install_init
        zabbix_6_0_install
        ;;
    7.0)
        install_init
        zabbix_7_0_install
        ;;
    uninstall5)
        zabbix_uninstall5
        ;;
    uninstall6)
        zabbix_uninstall6
        ;;
    uninstall7)
        zabbix_uninstall7
        ;;
        help|*)
                echo $"Usage: $0 {5.0|6.0|7.0|uninstall5|uninstall6|uninstall7|help}"
                ;;
esac
}

main $1
