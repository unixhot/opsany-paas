#!/bin/bash
#******************************************
# Author:       Jason Zhao
# Email:        zhaoshundong@opsany.com
# Organization: OpsAny https://www.opsany.com/
# Description:  OpsAny Test Script
#******************************************

# Get Data/Time
CTIME=$(date "+%Y-%m-%d-%H-%M")

# Shell Envionment Variables
CDIR=$(pwd)
SHELL_NAME="opsany-test.sh"
SHELL_LOG="${CDIR}/${SHELL_NAME}.log"
PAAS_DOCKER_REG="registry.cn-beijing.aliyuncs.com/opsany"
LOCAL_INTERFACE="eth0"
LOCAL_IP=$(ip addr show ${LOCAL_INTERFACE} | grep 'inet ' | awk '{print $2}' | cut -d/ -f1)

# Shell Log Record
shell_log(){
    LOG_INFO=$1
    echo -e "\033[32m------ $CTIME ${SHELL_NAME} : ${LOG_INFO} ------\033[0m"
    echo "$CTIME ${SHELL_NAME} : ${LOG_INFO}" >> ${SHELL_LOG}
}

shell_warning_log(){
    LOG_INFO=$1
    echo -e "\033[33m------ $CTIME ${SHELL_NAME} : ${LOG_INFO} ------\033[0m"
    echo "$CTIME ${SHELL_NAME} : ${LOG_INFO}" >> ${SHELL_LOG}
}

shell_error_log(){
    LOG_INFO=$1
    echo -e "\033[31m------ $CTIME ${SHELL_NAME} : ${LOG_INFO} ------\033[0m"
    echo "$CTIME ${SHELL_NAME} : ${LOG_INFO}" >> ${SHELL_LOG}
}

ubuntu1604(){
    shell_log "ubuntu 16.04"
    docker run -d --restart=always --name opsany-ubuntu-test-16.04 \
	--hostname opsany-ubuntu-test-1604 \
        -p 6001:22 \
        -v /etc/localtime:/etc/localtime:ro \
        ${PAAS_DOCKER_REG}/ubuntu-test:16.04
    IPADDR=$(docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' opsany-ubuntu-test-16.04)
    PORT="22"
    shell_warning_log "opsany-ubuntu-test-16.04: Host IP: $LOCAL_IP Host Port: 6001 , Container IP: $IPADDR Container Port: $PORT  User: root Password: 123456.coM"
}

ubuntu1804(){
    shell_log "ubuntu 18.04"
    docker run -d --restart=always --name opsany-ubuntu-test-18.04 \
	--hostname opsany-ubuntu-test-1804 \
        -p 6002:22 \
        -v /etc/localtime:/etc/localtime:ro \
        ${PAAS_DOCKER_REG}/ubuntu-test:18.04
    IPADDR=$(docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' opsany-ubuntu-test-18.04)
    PORT="22"
    shell_warning_log "opsany-ubuntu-test-18.04: Host IP: $LOCAL_IP Host Port: 6002 , Container IP: $IPADDR Container Port: $PORT  User: root Password: 123456.coM"
}

ubuntu2004(){
    shell_log "ubuntu 20.04"
    docker run -d --restart=always --name opsany-ubuntu-test-20.04 \
	--hostname opsany-ubuntu-test-2004 \
        -p 6003:22 \
        -v /etc/localtime:/etc/localtime:ro \
        ${PAAS_DOCKER_REG}/ubuntu-test:20.04
    IPADDR=$(docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' opsany-ubuntu-test-20.04)
    PORT="22"
    shell_warning_log "opsany-ubuntu-test-20.04: Host IP: $LOCAL_IP Host Port: 6003 , Container IP: $IPADDR Container Port: $PORT  User: root Password: 123456.coM"
}

ubuntu2204(){
    shell_log "ubuntu 22.04"
    docker run -d --restart=always --name opsany-ubuntu-test-22.04 \
	--hostname opsany-ubuntu-test-2204 \
        -p 6004:22 \
        -v /etc/localtime:/etc/localtime:ro \
        ${PAAS_DOCKER_REG}/ubuntu-test:22.04
    IPADDR=$(docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' opsany-ubuntu-test-22.04)
    PORT="22"
    shell_warning_log "opsany-ubuntu-test-22.04: Host IP: $LOCAL_IP Host Port: 6004 , Container IP: $IPADDR Container Port: $PORT  User: root Password: 123456.coM"
}

ubuntu2404(){
    shell_log "ubuntu 16.04"
    docker run -d --restart=always --name opsany-ubuntu-test-24.04 \
	--hostname opsany-ubuntu-test-2404 \
        -p 6005:22 \
        -v /etc/localtime:/etc/localtime:ro \
        ${PAAS_DOCKER_REG}/ubuntu-test:24.04
    IPADDR=$(docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' opsany-ubuntu-test-24.04)
    PORT="22"
    shell_warning_log "opsany-ubuntu-test-24.04: Host IP: $LOCAL_IP Host Port: 6005 , Container IP: $IPADDR Container Port: $PORT  User: root Password: 123456.coM"
}

almalinux810(){
    shell_log "almalinux 8.10"
    docker run -d --restart=always --name opsany-almalinux-test-8.10 \
	--hostname opsany-almalinux-test-8 \
        -p 6006:22 \
        -v /etc/localtime:/etc/localtime:ro \
        ${PAAS_DOCKER_REG}/almalinux-test:8.10
    IPADDR=$(docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' opsany-almalinux-test-8.10)
    PORT="22"
    shell_warning_log "opsany-almalinux-test-8.10: Host IP: $LOCAL_IP Host Port: 6006 , Container IP: $IPADDR Container Port: $PORT  User: root Password: 123456.coM"
}

almalinux905(){
    shell_log "almalinux 9.5"
    docker run -d --restart=always --name opsany-almalinux-test-9.5 \
	--hostname opsany-almalinux-test-9 \
        -p 6007:22 \
        -v /etc/localtime:/etc/localtime:ro \
        ${PAAS_DOCKER_REG}/almalinux-test:9.5
    IPADDR=$(docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' opsany-almalinux-test-9.5)
    PORT="22"
    shell_warning_log "opsany-almalinux-test-9.5: Host IP: $LOCAL_IP Host Port: 6007 , Container IP: $IPADDR Container Port: $PORT  User: root Password: 123456.coM"
}

rockylinux810(){
    shell_log "rockylinux 8.10"
    docker run -d --restart=always --name opsany-rockylinux-test-8.10 \
	--hostname opsany-rockylinux-test-8 \
        -p 6008:22 \
        -v /etc/localtime:/etc/localtime:ro \
        ${PAAS_DOCKER_REG}/rockylinux-test:8.10
    IPADDR=$(docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' opsany-rockylinux-test-8.10)
    PORT="22"
    shell_warning_log "opsany-rockylinux-test-8.10: Host IP: $LOCAL_IP Host Port: 6008 , Container IP: $IPADDR Container Port: $PORT  User: root Password: 123456.coM"
}

rockylinux904(){
    shell_log "rockylinux 9.4"
    docker run -d --restart=always --name opsany-rockylinux-test-9.4 \
	--hostname opsany-rockylinux-test-9 \
        -p 6009:22 \
        -v /etc/localtime:/etc/localtime:ro \
        ${PAAS_DOCKER_REG}/rockylinux-test:9.4
    IPADDR=$(docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' opsany-rockylinux-test-9.4)
    PORT="22"
    shell_warning_log "opsany-rockylinux-test-9.4: Host IP: $LOCAL_IP Host Port: 6009 , Container IP: $IPADDR Container Port: $PORT  User: root Password: 123456.coM"
}

remove_all(){
    docker stop opsany-ubuntu-test-16.04 && docker rm opsany-ubuntu-test-16.04
    docker stop opsany-ubuntu-test-18.04 && docker rm opsany-ubuntu-test-18.04
    docker stop opsany-ubuntu-test-20.04 && docker rm opsany-ubuntu-test-20.04
    docker stop opsany-ubuntu-test-22.04 && docker rm opsany-ubuntu-test-22.04
    docker stop opsany-ubuntu-test-24.04 && docker rm opsany-ubuntu-test-24.04
    docker stop opsany-almalinux-test-8.10 && docker rm opsany-almalinux-test-8.10
    docker stop opsany-almalinux-test-9.5 && docker rm opsany-almalinux-test-9.5
    docker stop opsany-rockylinux-test-9.4 && docker rm opsany-rockylinux-test-9.4
    docker stop opsany-rockylinux-test-8.10 && docker rm opsany-rockylinux-test-8.10
}
# Main
main(){
    case "$1" in
	ubuntu)
        ubuntu1604
        ubuntu1804
        ubuntu2004
        ubuntu2204
        ubuntu2404
	    ;;
    almalinux)
        almalinux810
        almalinux905
        ;;
    rockylinux)
        almalinux810
        almalinux905
        ;;
    all)
        ubuntu1604
        ubuntu1804
        ubuntu2004
        ubuntu2204
        ubuntu2404
        almalinux810
        almalinux905
        rockylinux810
        rockylinux904
        ;;
    remove)
        remove_all
        ;;
	help|*)
		echo $"Usage: $0 {all|ubuntu|centos|alam|rocky|remove|help}"
	        ;;
    esac
}

main $1
