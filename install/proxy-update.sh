#!/bin/bash
#******************************************
# Author:       Jason Zhao
# Email:        zhaoshundong@opsany.com
# Organization: OpsAny https://www.opsany.com/
# Description:  OpsAny Community Edition Proxy Update Script
#******************************************

# Data/Time Variables
CTIME=$(date "+%Y-%m-%d-%H-%M")

# Shell Envionment Variables
CDIR=$(pwd)
SHELL_NAME="proxy-update.sh"
SHELL_LOG="${SHELL_NAME}.log"
ADMIN_PASSWORD=""

# Shell Log Record
shell_log(){
    # Show green
    LOG_INFO=$1
    echo -e "\033[32m---------------- $CTIME ${SHELL_NAME} : ${LOG_INFO} ----------------\033[0m"
    echo "$CTIME ${SHELL_NAME} : ${LOG_INFO}" >> ${SHELL_LOG}
}

shell_warning_log(){
    # Show yellow
    LOG_INFO=$1
    echo -e "\033[33m---------------- $CTIME ${SHELL_NAME} : ${LOG_INFO} ----------------\033[0m"
    echo "$CTIME ${SHELL_NAME} : ${LOG_INFO}" >> ${SHELL_LOG}
}

shell_error_log(){
    # Show red
    LOG_INFO=$1
    echo -e "\033[31m---------------- $CTIME ${SHELL_NAME} : ${LOG_INFO} ----------------\033[0m"
    echo "$CTIME ${SHELL_NAME} : ${LOG_INFO}" >> ${SHELL_LOG}
}

# Install Inspection
if [ ! -f ./install.config ];then
      shell_error_log "Please Change Directory to ${INSTALL_PATH}/install"
      exit
else
    grep '^[A-Z]' install.config > install.env
    source ./install.env && rm -f install.env
    if [ -z "$ADMIN_PASSWORD" ];then
        source ${INSTALL_PATH}/conf/.passwd_env
    fi
fi

# Update Proxy
proxy_update(){
    shell_log "======Update Proxy======"
    UPDATE_VERSION=$1
    # Proxy config
    CONTROL_SECRET_KEY=$(cat ${INSTALL_PATH}/conf/.control_secret_key)
    /bin/cp conf/proxy/proxy.ini ${INSTALL_PATH}/conf/proxy/proxy.ini
    /bin/cp conf/proxy/saltmaster.ini ${INSTALL_PATH}/conf/proxy/saltmaster.ini
    /bin/cp conf/proxy/settings_production.py.proxy ${INSTALL_PATH}/conf/proxy/
    sed -i "s/REDIS_SERVER_IP/${REDIS_SERVER_IP}/g" ${INSTALL_PATH}/conf/proxy/settings_production.py.proxy
    sed -i "s/REDIS_SERVER_PASSWORD/${REDIS_SERVER_PASSWORD}/g" ${INSTALL_PATH}/conf/proxy/settings_production.py.proxy
    sed -i "s/MYSQL_SERVER_IP/${MYSQL_SERVER_IP}/g" ${INSTALL_PATH}/conf/proxy/settings_production.py.proxy
    sed -i "s/MYSQL_OPSANY_PASSWORD/${MYSQL_OPSANY_PASSWORD}/g" ${INSTALL_PATH}/conf/proxy/settings_production.py.proxy
    sed -i "s/local-proxy.opsany.com/${PROXY_LOCAL_IP}/g" ${INSTALL_PATH}/conf/proxy/settings_production.py.proxy
    sed -i "s/public-proxy.opsany.com/${PROXY_PUBLIC_IP}/g" ${INSTALL_PATH}/conf/proxy/settings_production.py.proxy
    sed -i "s/LOCAL_IP/${PROXY_PUBLIC_IP} ${PROXY_LOCAL_IP}/g" ${INSTALL_PATH}/conf/proxy/nginx-conf.d/nginx_proxy.conf
    sed -i "s/DOMAIN_NAME/${PROXY_PUBLIC_IP} ${PROXY_LOCAL_IP}/g" ${INSTALL_PATH}/conf/proxy/nginx-conf.d/nginx_proxy.conf
    sed -i "s/RABBIT_SERVER_IP/${RABBIT_SERVER_IP}/g" ${INSTALL_PATH}/conf/proxy/settings_production.py.proxy
    sed -i "s/RABBITMQ_DEFAULT_USER/${RABBITMQ_DEFAULT_USER}/g" ${INSTALL_PATH}/conf/proxy/settings_production.py.proxy
    sed -i "s/RABBITMQ_DEFAULT_PASS/${RABBITMQ_DEFAULT_PASS}/g" ${INSTALL_PATH}/conf/proxy/settings_production.py.proxy
    sed -i "s/CONTROL_SECRET_KEY_PROXY/${CONTROL_SECRET_KEY}/g" ${INSTALL_PATH}/conf/proxy/settings_production.py.proxy
    cp ../saas/invscript_proxy.py ${INSTALL_PATH}/conf/proxy/
    sed -i "s/LOCALHOST/${MYSQL_SERVER_IP}/g" ${INSTALL_PATH}/conf/proxy/invscript_proxy.py
    sed -i "s/PROXY_PASSWORD/${MYSQL_OPSANY_PASSWORD}/g" ${INSTALL_PATH}/conf/proxy/invscript_proxy.py
    sed -i "s/CONTROL_SECRET_KEY/${CONTROL_SECRET_KEY}/g" ${INSTALL_PATH}/conf/proxy/invscript_proxy.py
    chmod +x ${INSTALL_PATH}/conf/proxy/invscript_proxy.py

    # Starter container
    docker stop opsany-paas-proxy && docker rm opsany-paas-proxy 
    docker stop opsany-proxy-proxy && docker rm opsany-proxy-proxy 
    docker pull ${PAAS_DOCKER_REG}/opsany-paas-proxy:${UPDATE_VERSION}
    mkdir -p ${INSTALL_PATH}/logs/proxy
    docker run --restart=always --name opsany-proxy-proxy -d \
        -p 4505:4505 -p 4506:4506 -p 8010:8010 \
        -v ${INSTALL_PATH}/logs/proxy:/opt/opsany/logs/proxy \
        -v ${INSTALL_PATH}/proxy-volume/certs/:/etc/pki/tls/certs/ \
        -v ${INSTALL_PATH}/proxy-volume/etc/salt/:/etc/salt/ \
        -v ${INSTALL_PATH}/proxy-volume/cache/:/var/cache/salt/ \
        -v ${INSTALL_PATH}/proxy-volume/srv/salt:/srv/salt/ \
        -v ${INSTALL_PATH}/proxy-volume/srv/pillar:/srv/pillar/ \
        -v ${INSTALL_PATH}/proxy-volume/srv/playbook:/srv/playbook/ \
        -v ${INSTALL_PATH}/proxy-volume/pki:/opt/opsany/pki \
        -v ${INSTALL_PATH}/uploads:/opt/opsany/uploads \
        -v ${INSTALL_PATH}/conf/proxy/settings_production.py.proxy:/opt/opsany-proxy/config/prod.py \
        -v ${INSTALL_PATH}/conf/proxy/invscript_proxy.py:/opt/opsany-proxy/invscript_proxy.py \
        -v ${INSTALL_PATH}/conf/proxy/proxy.ini:/etc/supervisord.d/proxy.ini \
        -v ${INSTALL_PATH}/conf/proxy/saltmaster.ini:/etc/supervisord.d/saltmaster.ini \
        -v ${INSTALL_PATH}/prometheus-volume/conf/alertmanager.yml:/opt/opsany/alertmanager.yml \
        -v /etc/localtime:/etc/localtime:ro \
        ${PAAS_DOCKER_REG}/opsany-paas-proxy:${UPDATE_VERSION}

    # OpsAny Database Init
    docker exec -e OPS_ANY_ENV=production \
        opsany-paas-proxy /bin/sh -c "/usr/local/bin/python3 /opt/opsany-proxy/manage.py migrate >> ${SHELL_LOG}"
}

redis_update(){
    # Redis
    shell_log "======Start Redis======"
    docker pull ${PAAS_DOCKER_REG}/redis:${UPDATE_VERSION}
    docker stop opsany-proxy-redis && docker rm opsany-proxy-redis
    docker run -d --restart=always --name opsany-proxy-redis \
    -p 6379:6379 -v ${INSTALL_PATH}/redis-volume:/data \
    -v ${INSTALL_PATH}/redis-volume/redis.conf:/data/redis.conf \
    -v /etc/localtime:/etc/localtime:ro \
    ${PAAS_DOCKER_REG}/redis:${UPDATE_VERSION} redis-server /data/redis.conf
}

mysql_update(){
    # MySQL
    shell_log "======Start MySQL======"
    docker stop opsany-proxy-mysql && docker rm opsany-proxy-mysql
    docker run -d --restart=always --name opsany-proxy-mysql \
    docker run -d --restart=always --name opsany-proxy-mysql \
    -e MYSQL_ROOT_PASSWORD="$MYSQL_ROOT_PASSWORD" \
    -p 3306:3306 -v ${INSTALL_PATH}/mysql-volume:/var/lib/mysql \
    -v ${INSTALL_PATH}/conf/mysql/mysqld.cnf:/etc/mysql/mysql.conf.d/mysqld.cnf \
    -v ${INSTALL_PATH}/logs:/var/log/mysql \
    -v /etc/localtime:/etc/localtime:ro \
    ${PAAS_DOCKER_REG}/mysql:${UPDATE_VERSION} --character-set-server=utf8mb4 --collation-server=utf8mb4_unicode_ci
}  
    
guacd_update(){
# Guacd
    shell_log "======Start Guacd======"
    docker run -d --restart=always --name opsany-proxy-guacd \
    -p 4822:4822 \
    -v ${INSTALL_PATH}/uploads/guacamole:/srv/guacamole \
    -v /etc/localtime:/etc/localtime:ro \
    ${PAAS_DOCKER_REG}/guacd:${UPDATE_VERSION}
}  

openresty_update(){
    shell_log "======PaaS Service: Update openresty======"
    # OpenResty
    sed -i "s/DOMAIN_NAME/${DOMAIN_NAME}/g" ${INSTALL_PATH}/conf/nginx-conf.d/opsany_paas.conf
    sed -i "s/LOCAL_IP/${LOCAL_IP}/g" ${INSTALL_PATH}/conf/nginx-conf.d/opsany_paas.conf
    sed -i "s/DOMAIN_NAME/${DOMAIN_NAME}/g" ${INSTALL_PATH}/conf/nginx-conf.d/opsany_proxy.conf
    sed -i "s/LOCAL_IP/${LOCAL_IP}/g" ${INSTALL_PATH}/conf/nginx-conf.d/opsany_proxy.conf
    docker pull ${PAAS_DOCKER_REG}/openresty:${UPDATE_VERSION}
    docker stop opsany-proxy-openresty && docker rm opsany-proxy-openresty
    docker run -d --restart=always --name opsany-proxy-openresty \
    -p 80:80 -p 443:443 -p 8011:8011 -p 8012:8012 \
    -v ${INSTALL_PATH}/logs:/opt/opsany/logs \
    -v ${INSTALL_PATH}/conf/nginx-conf.d:/etc/nginx/conf.d \
    -v ${INSTALL_PATH}/conf/nginx.conf:/etc/nginx/nginx.conf \
    -v ${INSTALL_PATH}/uploads:/opt/opsany/uploads \
    -v /etc/localtime:/etc/localtime:ro \
    ${PAAS_DOCKER_REG}/openresty:${UPDATE_VERSION}
}

# Main
main(){
    UPDATE_VERSION=$2
    case "$1" in
        proxy)
            proxy_update $2
            ;;
        mysql)
            mysql_update $2
            ;;
        redis)
            redis_update $2
            ;;
        guacd)
            guacd_update $2
            ;;
        openresty)
            openresty_update $2
            ;;
	help|*)
	    echo $"Usage: $0 {(proxy|mysql|redis|guacd|openresty|help) version}"
	    ;;
    esac
}

main $1 $2
