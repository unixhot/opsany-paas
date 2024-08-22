#!/bin/bash
#******************************************
# Author:       Jason Zhao
# Email:        zhaoshundong@opsany.com
# Organization: OpsAny https://www.opsany.com/
# Description:  OpsAny Proxy Install Script
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
    mkdir -p ${INSTALL_PATH}/{uploads/guacamole,conf,logs/proxy,proxy-volume/certs,proxy-volume/srv/pillar,proxy-volume/srv/salt,proxy-volume/etc,proxy-volume/pki,redis-volume,mysql-volume}
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

base_install(){
    # Redis
    shell_log "======Start Redis======"
    docker run -d --restart=always --name opsany-proxy-redis \
    -p 6379:6379 -v ${INSTALL_PATH}/redis-volume:/data \
    -v ${INSTALL_PATH}/redis-volume/redis.conf:/data/redis.conf \
    -v /etc/localtime:/etc/localtime:ro \
    ${PAAS_DOCKER_REG}/redis:6.0.9-alpine redis-server /data/redis.conf
    
    # MySQL
    shell_log "======Start MySQL======"
    docker run -d --restart=always --name opsany-proxy-mysql \
    -e MYSQL_ROOT_PASSWORD="$MYSQL_ROOT_PASSWORD" \
    -p 3306:3306 -v ${INSTALL_PATH}/mysql-volume:/var/lib/mysql \
    -v ${INSTALL_PATH}/conf/mysqld.cnf:/etc/mysql/mysql.conf.d/mysqld.cnf \
    -v ${INSTALL_PATH}/logs:/var/log/mysql \
    -v /etc/localtime:/etc/localtime:ro \
    ${PAAS_DOCKER_REG}/mysql:5.6.50 --character-set-server=utf8 --collation-server=utf8_general_ci
    
    # Guacd
    shell_log "======Start Guacd======"
    docker run -d --restart=always --name opsany-proxy-guacd \
    -p 4822:4822 \
    -v ${INSTALL_PATH}/uploads/guacamole:/srv/guacamole \
    -v /etc/localtime:/etc/localtime:ro \
    ${PAAS_DOCKER_REG}/guacd:1.2.0
}

proxy_config(){
    shell_log "======MySQL Initialize======"
    sleep 10
    cd ${CDIR}/../install/
    export MYSQL_PWD=${MYSQL_ROOT_PASSWORD}
    mysql -h "${MYSQL_SERVER_IP}" -u root  -e "CREATE DATABASE IF NOT EXISTS opsany_proxy DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;"
    mysql -h "${MYSQL_SERVER_IP}" -u root  -e "grant all on opsany_proxy.* to opsany@'%' identified by "\"${MYSQL_OPSANY_PASSWORD}\"";" 
    #mysql -h "${MYSQL_SERVER_IP}" -u root  opsany_paas < init/opsany-proxy.sql

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

    cd ../saas/
    cp invscript_proxy.py ${INSTALL_PATH}/conf/proxy/
    sed -i "s/LOCALHOST/${MYSQL_SERVER_IP}/g" ${INSTALL_PATH}/conf/proxy/invscript_proxy.py
    sed -i "s/PROXY_PASSWORD/${MYSQL_OPSANY_PASSWORD}/g" ${INSTALL_PATH}/conf/proxy/invscript_proxy.py
    chmod +x ${INSTALL_PATH}/conf/proxy/invscript_proxy.py
}

proxy_start(){
    # Proxy
    shell_log "======Start Proxy======"
    docker pull ${PAAS_DOCKER_REG}/opsany-paas-proxy:2.2.0
    docker run --restart=always --name opsany-paas-proxy -d \
        -p 4505:4505 -p 4506:4506 -p 8010:8010 \
        -v ${INSTALL_PATH}/logs/proxy:/opt/opsany/logs/proxy \
        -v ${INSTALL_PATH}/proxy-volume/certs/:/etc/pki/tls/certs/ \
        -v ${INSTALL_PATH}/proxy-volume/etc/salt/:/etc/salt/ \
        -v ${INSTALL_PATH}/proxy-volume/cache/:/var/cache/salt/ \
        -v ${INSTALL_PATH}/proxy-volume/srv/salt:/srv/salt/ \
        -v ${INSTALL_PATH}/proxy-volume/srv/pillar:/srv/pillar/ \
        -v ${INSTALL_PATH}/proxy-volume/srv/playbook:/srv/playbook/ \
        -v ${INSTALL_PATH}/uploads:/opt/opsany/uploads \
        -v ${INSTALL_PATH}/conf/proxy/settings_production.py.proxy-standalone:/opt/opsany-proxy/config/prod.py \
        -v ${INSTALL_PATH}/conf/proxy/invscript_proxy.py:/opt/opsany-proxy/invscript_proxy.py \
        -v ${INSTALL_PATH}/conf/proxy/proxy.ini:/etc/supervisord.d/proxy.ini \
        -v ${INSTALL_PATH}/conf/proxy/saltapi.ini:/etc/supervisord.d/saltapi.ini \
        -v ${INSTALL_PATH}/conf/proxy/saltmaster.ini:/etc/supervisord.d/saltmaster.ini \
        -v ${INSTALL_PATH}/proxy-volume/pki:/opt/opsany/pki \
        -v /etc/localtime:/etc/localtime:ro \
        ${PAAS_DOCKER_REG}/opsany-paas-proxy:2.2.0

    #openresty
    shell_log "======Start openresty Service======"
    docker run -d --restart=always --name opsany-proxy-openresty \
    -p 8011:443 -p 8012:80 \
    -v ${INSTALL_PATH}/logs:/opt/opsany/logs \
    -v ${INSTALL_PATH}/conf/proxy/nginx-conf.d:/etc/nginx/conf.d \
    -v ${INSTALL_PATH}/conf/proxy/nginx.conf:/etc/nginx/nginx.conf \
    -v ${INSTALL_PATH}/uploads:/opt/opsany/uploads \
    -v /etc/localtime:/etc/localtime:ro \
    ${PAAS_DOCKER_REG}/openresty:1.17.8.2-alpine

    # OpsAny Database Init
    docker exec -e OPS_ANY_ENV=production \
        opsany-paas-proxy /bin/sh -c "/usr/local/bin/python3 /opt/opsany-proxy/manage.py makemigrations && /usr/local/bin/python3 /opt/opsany-proxy/manage.py migrate"

    # Create Proxy Token
    PROXY_TOKEN=$(docker exec -e OPS_ANY_ENV=production \
            opsany-paas-proxy /bin/sh -c " /usr/local/bin/python3 /opt/opsany-proxy/manage.py create_access" | grep 'Access' | awk -F ': ' '{print $2}' | awk -F '.' '{print $1}')
    shell_warning_log "Proxy Token: ${PROXY_TOKEN}"
}

# Main
main(){
    case "$1" in
	install)
            install_check
            install_init
            base_install
            proxy_config
            proxy_start
		;;
	help|*)
		echo $"Usage: $0 {install|help}"
	        ;;
    esac
}

main $1
