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
}

jenkins_install(){
    # Step1: Create Jenkins Home
    mkdir -p ${INSTALL_PATH}/jenkins-home && chmod -R 777 ${INSTALL_PATH}/jenkins-home
    # Step2: Start Jenkins Master
    docker run --restart=always --name opsany-devops-jenkins -t \
    -v /etc/localtime:/etc/localtime:ro \
    -v ${INSTALL_PATH}/jenkins-home:/var/jenkins_home \
    -p 8008:8080 -p 8009:5000 \
    -d ${PAAS_DOCKER_REG}/jenkins:2.452.2-lts
}

nexux_install(){
    # Step1: Create Nexus Data
    mkdir -p ${INSTALL_PATH}/nexus-data && chmod -R 777 ${INSTALL_PATH}/nexus-data
    # Step2: Start Nexus Server
    docker run -d -p 8014:8081 -p 8015:5000 --restart=always --name opsany-devops-nexus \
        -v ${INSTALL_PATH}/nexus-data:/nexus-data  \
        -e INSTALL4J_ADD_VM_PARAMS="-Xms500m -Xmx500m -XX:MaxDirectMemorySize=500m" \
        ${PAAS_DOCKER_REG}/nexus3:3.37.0
}

snoar_install(){
    # Step1: Init 
    sysctl -w vm.max_map_count=262144
    sysctl -w fs.file-max=65536
    ulimit -n 65536
    ulimit -u 4096

    # Step2: Start SonarQube Server
    docker run --restart=always --name opsany-devops-sonarqube -t \
        -v /etc/localtime:/etc/localtime:ro \
        -p 8016:9000 \
        -d ${PAAS_DOCKER_REG}/sonarqube:9.9.6-community
}

# Main
main(){
    case "$1" in
    jenkins)
        jenkins_install
        ;;
    nexus)
        nexus_install
        ;;
    sonar)
        snoar_install
        ;;
    all)
        jenkins_install
        nexus_install
        snoar_install
        ;;
    help|*)
        echo $"Usage: $0 {jenkins|nexus|sonar|all|help}"
        ;;
    esac
}

main $1
