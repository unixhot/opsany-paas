#!/bin/bash
#******************************************
# Author:       Jason Zhao
# Email:        zhaoshundong@opsany.com
# Organization: OpsAny https://www.opsany.com/
# Description:  ST2 Install Script
#******************************************

# Get Data/Time
CTIME=$(date "+%Y-%m-%d-%H-%M")

# Shell Envionment Variables
CDIR=$(pwd)
SHELL_NAME="st2-install.sh"
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
    if [ -f /etc/redhat-release ];then
      setenforce 0
    fi
fi

# Check Install requirement
install_check(){
  DOCKER_PID=$(ps aux | grep '/usr/bin/containerd' | grep -v 'grep' | wc -l)
  if [ ${DOCKER_PID} -lt 1 ];then
      shell_error_log "Please install and start docker first!!!"
      exit
  fi
}

# Install Initialize
install_init(){
    shell_log "Start: Install Init"
    mkdir -p ${INSTALL_PATH}/{uploads/guacamole,conf,logs,proxy-volume/certs,proxy-volume/srv/pillar,proxy-volume/srv/salt,proxy-volume/etc,proxy-volume/pki,redis-volume,mysql-volume}
    cd $CDIR
    /bin/cp -r ../install/conf ${INSTALL_PATH}/
    #/bin/cp -r ../install/init ${INSTALL_PATH}/

    ## init for saltstack 
    /bin/cp -a ${CDIR}/../install/conf/salt ${INSTALL_PATH}/proxy-volume/etc/
    /bin/cp -a ${CDIR}/../install/conf/salt/certs/* ${INSTALL_PATH}/proxy-volume/certs/

    # init for redis
    /bin/cp ${CDIR}/../install/conf/redis/redis.conf ${INSTALL_PATH}/redis-volume/
    sed -i "s/"REDIS_SERVER_PASSWORD"/"${REDIS_SERVER_PASSWORD}"/g" ${INSTALL_PATH}/redis-volume/redis.conf
    shell_log "End: Install Init"
}

st2_config(){

    shell_log "======Proxy Configure======"
    # Proxy
    sed -i "s/REDIS_SERVER_IP/${REDIS_SERVER_IP}/g" ${INSTALL_PATH}/conf/proxy/settings_production.py.proxy-standalone
    sed -i "s/REDIS_SERVER_PASSWORD/${REDIS_SERVER_PASSWORD}/g" ${INSTALL_PATH}/conf/proxy/settings_production.py.proxy-standalone
    sed -i "s/MYSQL_SERVER_IP/${MYSQL_SERVER_IP}/g" ${INSTALL_PATH}/conf/proxy/settings_production.py.proxy-standalone
    sed -i "s/MYSQL_OPSANY_PASSWORD/${MYSQL_OPSANY_PASSWORD}/g" ${INSTALL_PATH}/conf/proxy/settings_production.py.proxy-standalone
    sed -i "s/local-proxy.opsany.com/${PROXY_LOCAL_IP}/g" ${INSTALL_PATH}/conf/proxy/settings_production.py.proxy-standalone
    sed -i "s/public-proxy.opsany.com/${PROXY_PUBLIC_IP}/g" ${INSTALL_PATH}/conf/proxy/settings_production.py.proxy-standalone
    
    # OpenResty
    sed -i "s/LOCAL_IP/${PROXY_LOCAL_IP}/g" ${INSTALL_PATH}/conf/proxy/nginx-conf.d/nginx_proxy.conf 
    sed -i "s/DOMAIN_NAME/${PROXY_PUBLIC_IP} ${PROXY_LOCAL_IP}/g" ${INSTALL_PATH}/conf/proxy/nginx-conf.d/nginx_proxy.conf
}

st2_start(){
    ST2_VERSION="3.8.0"
    ST2_IMAGE_REPO="stackstorm/"
    ST2_EXPOSE_HTTP="0.0.0.0:8005"
    #docker-compose
    shell_log "======Start openresty Service======"
    cd opsany-st2
    docker-compose up -d
}

# Main
main(){
    case "$1" in
	install)
            install_check
            install_init
            st2_config
            st2_start
		;;
	help|*)
		echo $"Usage: $0 {install|help}"
	        ;;
    esac
}

main $1

