#!/bin/bash
#******************************************
# Author:       Jason Zhao
# Email:        zhaoshundong@opsany.com
# Organization: OpsAny https://www.opsany.com/
# Description:  OpsAny PaaS Install Script
#******************************************

# Get Data/Time
CTIME=$(date "+%Y-%m-%d-%H-%M")

# Shell Envionment Variables
CDIR=$(pwd)
SHELL_NAME="paas-install.sh"
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
    echo -e "\033[31m---------------- $CTIME ${SHELL_NAME} : ${LOG_INFO} ----------------\033[0m"
    echo "$CTIME ${SHELL_NAME} : ${LOG_INFO}" >> ${SHELL_LOG}
}

# Install Inspection
if [ ! -f ./install.config ];then
      shell_error_log "Please Copy install.config and Change: cp install.config.example install.config"
      exit
else
    PRESTR='Ops'
    STR=`head /dev/urandom | tr -dc A-Za-z0-9 | head -c 5`
    NUM=`echo $RANDOM`
    NEW_PASSWORD=$PRESTR$STR$NUM
    sed -i "s/INIT_PASSWORD/${NEW_PASSWORD}/g" install.config
    source ./install.config
fi

# Create Self-signed Server Certificate
ssl_make(){
    shell_log "======Init: Create Self-signed Server Certificate======"
    # create dir for ssl
    if [ ! -d ./conf/nginx-conf.d/ssl ];then
      mkdir -p ./conf/nginx-conf.d/ssl
    fi
    cp ./conf/openssl.cnf ./conf/nginx-conf.d/ssl/
    cd ./conf/nginx-conf.d/ssl
    openssl genrsa -des3 -passout pass:opsany -out $DOMAIN_NAME.key 2048 >/dev/null 2>&1

    #Create server certificate signing request
    SUBJECT="/C=CN/ST=BeiJing/L=BeiJing/O=BeiJing/OU=OpsAny/CN=OpsAny"
    openssl req -new -passin pass:opsany -subj $SUBJECT -key $DOMAIN_NAME.key -out $DOMAIN_NAME.csr >/dev/null 2>&1

    #Remove password
    mv $DOMAIN_NAME.key $DOMAIN_NAME.origin.key
    openssl rsa -passin pass:opsany -in $DOMAIN_NAME.origin.key  -out $DOMAIN_NAME.key >/dev/null 2>&1

    #Sign SSL certificate
    openssl x509 -req -days 3650 -extfile openssl.cnf -extensions 'v3_req'  -in $DOMAIN_NAME.csr -signkey $DOMAIN_NAME.key -out $DOMAIN_NAME.crt >/dev/null 2>&1
    openssl x509 -in ${DOMAIN_NAME}.crt -out ${DOMAIN_NAME}.pem -outform PEM >/dev/null 2>&1
    mv ${DOMAIN_NAME}.pem ${DOMAIN_NAME}.origin.pem
    cat ${DOMAIN_NAME}.key ${DOMAIN_NAME}.origin.pem > ${DOMAIN_NAME}.pem
    rm -f ./conf/openssl.cnf
}


# Check Install requirement
install_check(){
  shell_warning_log "======Begin: Getting started is the first step to success.======"
  if [ -f /etc/redhat-release ];then
      setenforce 0
  fi
}

minio(){
    mkdir -p ${INSTALL_PATH}/minio-volume
    docker run -d --restart=always --name opsany-base-minio \
    -p 8020:9000 \
    -p 8021:9001 \
    -v ${INSTALL_PATH}/minio-volume:/data \
    -e "MINIO_ROOT_USER=opsany" \
    -e "MINIO_ROOT_PASSWORD=123456.coM" \
    quay.io/minio/minio server /data --console-address ":9001"
}

# Install Initialize
opsany_init(){
    shell_log "======Init: Install Init======"
    mkdir -p ${INSTALL_PATH}/{uploads/guacamole,uploads/workbench/icon,conf,esb,logs/proxy,saas/apps,saas/saasapp,proxy-volume/certs,proxy-volume/pki,proxy-volume/srv/pillar,proxy-volume/srv/salt,proxy-volume/etc,paasagent-volume,redis-volume,mongodb-volume,mysql-volume,st2-volume,grafana-volume/plugins,grafana-volume/data}
    mkdir -p ${INSTALL_PATH}/{prometheus-volume/conf,prometheus-volume/data,consul-volume/data,consul-volume/config,uploads/prometheus-config/rules,prometheus-volume/template,prometheus-volume/alertmanager}
    cd $CDIR
    /bin/cp -r ../install/conf ${INSTALL_PATH}/
    /bin/cp -r ../install/init ${INSTALL_PATH}/
    /bin/cp -r ./uploads/* ${INSTALL_PATH}/uploads/
    /bin/cp -r ../paas-ce/saas/saas-logo/* ${INSTALL_PATH}/uploads/workbench/icon/
    /bin/cp -r ./conf/prometheus/* ${INSTALL_PATH}/prometheus-volume/conf/
    /bin/cp conf/consul.hcl ${INSTALL_PATH}/consul-volume/config/
    chmod -R 777 ${INSTALL_PATH}/prometheus-volume/

    ## init for esb
    /bin/cp -r ../paas-ce/paas/esb/components/generic/apis/ ${INSTALL_PATH}/esb/
    
    ## init for saltstack 
    /bin/cp -a ${CDIR}/../install/conf/salt ${INSTALL_PATH}/proxy-volume/etc/
    /bin/cp -a ${CDIR}/../install/conf/salt/certs/* ${INSTALL_PATH}/proxy-volume/certs/

    # init for redis
    /bin/cp ${CDIR}/../install/conf/redis/redis.conf ${INSTALL_PATH}/redis-volume/
    sed -i "s/"REDIS_SERVER_PASSWORD"/"${REDIS_SERVER_PASSWORD}"/g" ${INSTALL_PATH}/redis-volume/redis.conf
}

esb_init(){
    shell_log "======Init: ESB Initialize======"
    #cmdb
    sed -i "s/DOMAIN_NAME/$DOMAIN_NAME/g" ${INSTALL_PATH}/esb/apis/cmdb/toolkit/configs.py
    sed -i "s#/t/cmdb#/o/cmdb#g" ${INSTALL_PATH}/esb/apis/cmdb/toolkit/tools.py
    #control
    sed -i "s/DOMAIN_NAME/$DOMAIN_NAME/g" ${INSTALL_PATH}/esb/apis/control/toolkit/configs.py
    sed -i "s#/t/control#/o/control#g" ${INSTALL_PATH}/esb/apis/control/toolkit/tools.py
    #rbac
    sed -i "s/DOMAIN_NAME/$DOMAIN_NAME/g" ${INSTALL_PATH}/esb/apis/rbac/toolkit/configs.py
    sed -i "s#/t/rbac#/o/rbac#g" ${INSTALL_PATH}/esb/apis/rbac/toolkit/configs.py
    #job
    sed -i "s/DOMAIN_NAME/$DOMAIN_NAME/g" ${INSTALL_PATH}/esb/apis/task/toolkit/configs.py
    sed -i "s#/t/job#/o/job#g" ${INSTALL_PATH}/esb/apis/task/toolkit/tools.py
    sed -i "s/DOMAIN_NAME/$DOMAIN_NAME/g" ${INSTALL_PATH}/esb/apis/job/toolkit/configs.py
    sed -i "s#/t/job#/o/job#g" ${INSTALL_PATH}/esb/apis/job/toolkit/tools.py
    #workbench
    sed -i "s/DOMAIN_NAME/$DOMAIN_NAME/g" ${INSTALL_PATH}/esb/apis/workbench/toolkit/configs.py
    sed -i "s#/t/workbench#/o/workbench#g" ${INSTALL_PATH}/esb/apis/workbench/toolkit/tools.py
    #monitor
    sed -i "s/DOMAIN_NAME/$DOMAIN_NAME/g" ${INSTALL_PATH}/esb/apis/monitor/toolkit/configs.py
    sed -i "s#/t/monitor#/o/monitor#g" ${INSTALL_PATH}/esb/apis/monitor/toolkit/tools.py
    #cmp
    sed -i "s/DOMAIN_NAME/$DOMAIN_NAME/g" ${INSTALL_PATH}/esb/apis/cmp/toolkit/configs.py
    sed -i "s#/t/cmp#/o/cmp#g" ${INSTALL_PATH}/esb/apis/cmp/toolkit/tools.py
    #devops
    sed -i "s/DOMAIN_NAME/$DOMAIN_NAME/g" ${INSTALL_PATH}/esb/apis/devops/toolkit/configs.py
    sed -i "s#/t/devops#/o/devops#g" ${INSTALL_PATH}/esb/apis/devops/toolkit/tools.py
    #pipeline
    sed -i "s/DOMAIN_NAME/$DOMAIN_NAME/g" ${INSTALL_PATH}/esb/apis/pipeline/toolkit/configs.py
    sed -i "s#/t/pipeline#/o/pipeline#g" ${INSTALL_PATH}/esb/apis/pipeline/toolkit/tools.py
    #deploy
    sed -i "s/DOMAIN_NAME/$DOMAIN_NAME/g" ${INSTALL_PATH}/esb/apis/deploy/toolkit/configs.py
    sed -i "s#/t/deploy#/o/deploy#g" ${INSTALL_PATH}/esb/apis/deploy/toolkit/tools.py
    #repo
    sed -i "s/DOMAIN_NAME/$DOMAIN_NAME/g" ${INSTALL_PATH}/esb/apis/repo/toolkit/configs.py
    sed -i "s#/t/repo#/o/repo#g" ${INSTALL_PATH}/esb/apis/repo/toolkit/tools.py
    #code
    sed -i "s/DOMAIN_NAME/$DOMAIN_NAME/g" ${INSTALL_PATH}/esb/apis/code/toolkit/configs.py
    sed -i "s#/t/code#/o/code#g" ${INSTALL_PATH}/esb/apis/code/toolkit/tools.py
    #bastion
    sed -i "s/DOMAIN_NAME/$DOMAIN_NAME/g" ${INSTALL_PATH}/esb/apis/bastion/toolkit/configs.py
    sed -i "s#/t/bastion#/o/bastion#g" ${INSTALL_PATH}/esb/apis/bastion/toolkit/configs.py
    # llmops
    sed -i "s/DOMAIN_NAME/$DOMAIN_NAME/g" ${INSTALL_PATH}/esb/apis/llmops/toolkit/configs.py
    sed -i "s#/t/llmops#/o/llmops#g" ${INSTALL_PATH}/esb/apis/llmops/toolkit/configs.py
}


# PaaS Share Service Start
paas_install(){
    # Redis
    shell_log "======Base Service: Start Redis======"
    docker run -d --restart=always --name opsany-base-redis \
    -p 6379:6379 -v ${INSTALL_PATH}/redis-volume:/data \
    -v ${INSTALL_PATH}/redis-volume/redis.conf:/data/redis.conf \
    -v /etc/localtime:/etc/localtime:ro \
    ${PAAS_DOCKER_REG}/redis:6.2.19-alpine redis-server /data/redis.conf
    
    # MySQL
    shell_log "======Base Service: Start MySQL======"
    docker run -d --restart=always --name opsany-base-mysql \
    -e MYSQL_ROOT_PASSWORD="$MYSQL_ROOT_PASSWORD" \
    -p 3306:3306 -v ${INSTALL_PATH}/mysql-volume:/var/lib/mysql \
    -v ${INSTALL_PATH}/conf/mysqld.cnf:/etc/mysql/conf.d/mysqld.cnf \
    -v ${INSTALL_PATH}/logs:/var/log/mysql \
    -v /etc/localtime:/etc/localtime:ro \
    ${PAAS_DOCKER_REG}/mysql:8.0.30 --character-set-server=utf8 --collation-server=utf8_general_ci
    #${PAAS_DOCKER_REG}/mysql:5.6.50 --character-set-server=utf8 --collation-server=utf8_general_ci
    
    # MongoDB
    shell_log "======Base Service: Start MongoDB======"
    docker run -d --restart=always --name opsany-base-mongodb \
    -e MONGO_INITDB_ROOT_USERNAME="$MONGO_INITDB_ROOT_USERNAME" \
    -e MONGO_INITDB_ROOT_PASSWORD="$MONGO_INITDB_ROOT_PASSWORD" \
    -p 27017:27017 -v ${INSTALL_PATH}/mongodb-volume:/data/db \
    -v /etc/localtime:/etc/localtime:ro \
    ${PAAS_DOCKER_REG}/mongo:4.4.1-bionic
    
    # Guacd
    shell_log "======Base Service: Start Guacd======"
    docker run -d --restart=always --name opsany-base-guacd \
    -p 4822:4822 \
    -v ${INSTALL_PATH}/uploads/guacamole:/srv/guacamole \
    -v /etc/localtime:/etc/localtime:ro \
    ${PAAS_DOCKER_REG}/guacd:1.2.0
}

# MySQL Initialize
mysql_init(){
    shell_log "======Base Service: MySQL Initialize======"
    sleep 15
    cd ${CDIR}/../install/
    docker cp init opsany-base-mysql:/opt/
    export MYSQL_PWD=${MYSQL_ROOT_PASSWORD}
    # Check MySQL Status
    max_attempts=60
    attempt=0
    mysqladmin_command="mysqladmin ping -h "${MYSQL_SERVER_IP}" -u root"
    while [ $attempt -lt $max_attempts ]; do
        shell_log "Trying to connect to mysql..."
        if $mysqladmin_command > /dev/null 2>&1; then
            shell_log "MySQL has started."
            break
        else
            shell_log "The MySQL service is not started. Wait 10 seconds and try again."
            sleep 10
            attempt=$((attempt + 1))
        fi
    done
    #For MySQL 8.0
    mysql -h "${MYSQL_SERVER_IP}" -u root  -e "CREATE DATABASE IF NOT EXISTS opsany_paas DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;"
    mysql -h "${MYSQL_SERVER_IP}" -u root  -e "CREATE DATABASE IF NOT EXISTS opsany_proxy DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;"
    mysql -h "${MYSQL_SERVER_IP}" -u root  -e "CREATE USER opsany@'%' identified by "\"${MYSQL_OPSANY_PASSWORD}\"";"
    mysql -h "${MYSQL_SERVER_IP}" -u root  -e "grant all on opsany_paas.* to opsany@'%';"
    mysql -h "${MYSQL_SERVER_IP}" -u root  -e "grant all on opsany_proxy.* to opsany@'%';"
    mysql -h "${MYSQL_SERVER_IP}" -u root  opsany_paas < init/opsany-paas.sql
    mysql -h "${MYSQL_SERVER_IP}" -u root  opsany_paas < ./init/esb-init/esb_api_doc.sql
    mysql -h "${MYSQL_SERVER_IP}" -u root  opsany_paas < ./init/esb-init/esb_channel.sql
    mysql -h "${MYSQL_SERVER_IP}" -u root  opsany_paas < ./init/esb-init/esb_component_system.sql
}

# PaaS Service Start
paas_start(){
    # paas service
    shell_log "======PaaS Service: Start paas Service======"
    # PaaS Config
    sed -i "s/PAAS_LOGIN_IP/${PAAS_LOGIN_IP}/g" ${INSTALL_PATH}/conf/opsany-paas/paas/settings_production.py.paas
    sed -i "s/PAAS_APPENGINE_IP/${PAAS_APPENGINE_IP}/g" ${INSTALL_PATH}/conf/opsany-paas/paas/settings_production.py.paas
    sed -i "s/DOMAIN_NAME/${DOMAIN_NAME}/g" ${INSTALL_PATH}/conf/opsany-paas/paas/settings_production.py.paas
    sed -i "s/LOCAL_IP/${LOCAL_IP}/g" ${INSTALL_PATH}/conf/opsany-paas/paas/settings_production.py.paas
    sed -i "s/MYSQL_SERVER_IP/${MYSQL_SERVER_IP}/g" ${INSTALL_PATH}/conf/opsany-paas/paas/settings_production.py.paas
    sed -i "s/MYSQL_OPSANY_PASSWORD/${MYSQL_OPSANY_PASSWORD}/g" ${INSTALL_PATH}/conf/opsany-paas/paas/settings_production.py.paas
    sed -i "s/MYSQL_SERVER_PORT/${MYSQL_SERVER_PORT}/g" ${INSTALL_PATH}/conf/opsany-paas/paas/settings_production.py.paas

    docker pull ${PAAS_DOCKER_REG}/opsany-paas-paas:4.0.0
    docker run -d --restart=always --name opsany-paas-paas \
    -p 8001:8001 -v ${INSTALL_PATH}/logs:/opt/opsany/logs \
    -v ${INSTALL_PATH}/conf/opsany-paas/paas/settings_production.py.paas:/opt/opsany/paas/paas/conf/settings_production.py \
    -v ${INSTALL_PATH}/conf/opsany-paas/paas/paas.ini:/etc/supervisord.d/paas.ini \
    -v /etc/localtime:/etc/localtime:ro \
    ${PAAS_DOCKER_REG}/opsany-paas-paas:4.0.0
    
    #login service
    shell_log "======PaaS Service: Start login Service======"

    # RBAC secret key for login
    RBAC_SECRET_KEY=$(uuid -v4)
    echo $RBAC_SECRET_KEY > ${INSTALL_PATH}/conf/.rbac_secret_key

    #Login Config
    sed -i "s/RBAC_SECRET_KEY/${RBAC_SECRET_KEY}/g" ${INSTALL_PATH}/conf/opsany-paas/login/settings_production.py.login
    sed -i "s/DOMAIN_NAME/${DOMAIN_NAME}/g" ${INSTALL_PATH}/conf/opsany-paas/login/settings_production.py.login
    sed -i "s/LOCAL_IP/${LOCAL_IP}/g" ${INSTALL_PATH}/conf/opsany-paas/login/settings_production.py.login
    sed -i "s/MYSQL_SERVER_IP/${MYSQL_SERVER_IP}/g" ${INSTALL_PATH}/conf/opsany-paas/login/settings_production.py.login
    sed -i "s/MYSQL_OPSANY_PASSWORD/${MYSQL_OPSANY_PASSWORD}/g" ${INSTALL_PATH}/conf/opsany-paas/login/settings_production.py.login
    sed -i "s/MYSQL_SERVER_PORT/${MYSQL_SERVER_PORT}/g" ${INSTALL_PATH}/conf/opsany-paas/login/settings_production.py.login

    docker pull ${PAAS_DOCKER_REG}/opsany-paas-login:4.0.0
    docker run -d --restart=always --name opsany-paas-login \
    -p 8003:8003 -v ${INSTALL_PATH}/logs:/opt/opsany/logs \
    -v ${INSTALL_PATH}/conf/opsany-paas/login/settings_production.py.login:/opt/opsany/paas/login/conf/settings_production.py \
    -v ${INSTALL_PATH}/conf/opsany-paas/login/login.ini:/etc/supervisord.d/login.ini \
    -v /etc/localtime:/etc/localtime:ro \
    ${PAAS_DOCKER_REG}/opsany-paas-login:4.0.0
    
    # esb service
    shell_log "======PaaS Service: Start esb Service======"
    # ESB Config
    sed -i "s/PAAS_LOGIN_IP/${PAAS_LOGIN_IP}/g" ${INSTALL_PATH}/conf/opsany-paas/esb/settings_production.py.esb
    sed -i "s/PAAS_PAAS_IP/${PAAS_PAAS_IP}/g" ${INSTALL_PATH}/conf/opsany-paas/esb/settings_production.py.esb
    sed -i "s/REDIS_SERVER_IP/${REDIS_SERVER_IP}/g" ${INSTALL_PATH}/conf/opsany-paas/esb/settings_production.py.esb
    sed -i "s/REDIS_SERVER_PASSWORD/${REDIS_SERVER_PASSWORD}/g" ${INSTALL_PATH}/conf/opsany-paas/esb/settings_production.py.esb
    sed -i "s/MYSQL_SERVER_IP/${MYSQL_SERVER_IP}/g" ${INSTALL_PATH}/conf/opsany-paas/esb/settings_production.py.esb
    sed -i "s/MYSQL_OPSANY_PASSWORD/${MYSQL_OPSANY_PASSWORD}/g" ${INSTALL_PATH}/conf/opsany-paas/esb/settings_production.py.esb
    sed -i "s/MYSQL_SERVER_PORT/${MYSQL_SERVER_PORT}/g" ${INSTALL_PATH}/conf/opsany-paas/esb/settings_production.py.esb

    docker pull ${PAAS_DOCKER_REG}/opsany-paas-esb:4.0.0
    docker run -d --restart=always --name opsany-paas-esb \
    -p 8002:8002 -v ${INSTALL_PATH}/logs:/opt/opsany/logs \
    -v ${INSTALL_PATH}/esb/apis:/opt/opsany/paas/esb/components/generic/apis \
    -v ${INSTALL_PATH}/conf/opsany-paas/esb/settings_production.py.esb:/opt/opsany/paas/esb/configs/default.py \
    -v ${INSTALL_PATH}/conf/opsany-paas/esb/esb.ini:/etc/supervisord.d/esb.ini \
    -v /etc/localtime:/etc/localtime:ro \
    ${PAAS_DOCKER_REG}/opsany-paas-esb:4.0.0
    
    # appengine service
    shell_log "======PaaS Service: Start appengine Service======"
    # App Engine Config
    sed -i "s/MYSQL_SERVER_IP/${MYSQL_SERVER_IP}/g" ${INSTALL_PATH}/conf/opsany-paas/appengine/settings_production.py.appengine
    sed -i "s/MYSQL_OPSANY_PASSWORD/${MYSQL_OPSANY_PASSWORD}/g" ${INSTALL_PATH}/conf/opsany-paas/appengine/settings_production.py.appengine
    sed -i "s/MYSQL_SERVER_PORT/${MYSQL_SERVER_PORT}/g" ${INSTALL_PATH}/conf/opsany-paas/appengine/settings_production.py.appengine
    docker pull ${PAAS_DOCKER_REG}/opsany-paas-appengine:4.0.0
    docker run -d --restart=always --name opsany-paas-appengine \
    -p 8000:8000 -v ${INSTALL_PATH}/logs:/opt/opsany/logs \
    -v ${INSTALL_PATH}/conf/opsany-paas/appengine/settings_production.py.appengine:/opt/opsany/paas/appengine/controller/settings.py \
    -v ${INSTALL_PATH}/conf/opsany-paas/appengine/appengine.ini:/etc/supervisord.d/appengine.ini \
    -v /etc/localtime:/etc/localtime:ro \
    ${PAAS_DOCKER_REG}/opsany-paas-appengine:4.0.0
    
    # websocket service
    shell_log "======PaaS Service: Start websocket Service======"
    BASTION_SECRET_KEY=$(uuid -v4)
    echo $BASTION_SECRET_KEY > ${INSTALL_PATH}/conf/.bastion_secret_key   
    # Websocket
    sed -i "s/BASTION_SECRET_KEY/${BASTION_SECRET_KEY}/g" ${INSTALL_PATH}/conf/opsany-paas/websocket/settings_production.py.websocket.init
    sed -i "s/WEBSOCKET_GUACD_HOST/${WEBSOCKET_GUACD_HOST}/g" ${INSTALL_PATH}/conf/opsany-paas/websocket/settings_production.py.websocket
    sed -i "s/REDIS_SERVER_IP/${REDIS_SERVER_IP}/g" ${INSTALL_PATH}/conf/opsany-paas/websocket/settings_production.py.websocket
    sed -i "s/REDIS_SERVER_USER/${REDIS_SERVER_USER}/g" ${INSTALL_PATH}/conf/opsany-paas/websocket/settings_production.py.websocket
    sed -i "s/REDIS_SERVER_PORT/${REDIS_SERVER_PORT}/g" ${INSTALL_PATH}/conf/opsany-paas/websocket/settings_production.py.websocket
    sed -i "s/REDIS_SERVER_PASSWORD/${REDIS_SERVER_PASSWORD}/g" ${INSTALL_PATH}/conf/opsany-paas/websocket/settings_production.py.websocket
    sed -i "s/MYSQL_SERVER_IP/${MYSQL_SERVER_IP}/g" ${INSTALL_PATH}/conf/opsany-paas/websocket/settings_production.py.websocket
    sed -i "s/MYSQL_SERVER_PORT/${MYSQL_SERVER_PORT}/g" ${INSTALL_PATH}/conf/opsany-paas/websocket/settings_production.py.websocket
    sed -i "s/MYSQL_OPSANY_PASSWORD/${MYSQL_OPSANY_PASSWORD}/g" ${INSTALL_PATH}/conf/opsany-paas/websocket/settings_production.py.websocket
    sed -i "s/PAAS_PAAS_IP/${PAAS_PAAS_IP}/g" ${INSTALL_PATH}/conf/opsany-paas/websocket/settings_production.py.websocket.init
    docker pull ${PAAS_DOCKER_REG}/opsany-paas-websocket:4.0.0
    docker run -d --restart=always --name opsany-paas-websocket \
    -p 8004:8004 -v ${INSTALL_PATH}/logs:/opt/opsany/logs \
    -v ${INSTALL_PATH}/uploads:/opt/opsany/uploads \
    -v ${INSTALL_PATH}/conf/opsany-paas/websocket/settings_production.py.websocket:/opt/opsany/websocket/config/prod.py \
    -v ${INSTALL_PATH}/conf/opsany-paas/websocket/settings_production.py.websocket.init:/opt/opsany/websocket/config/__init__.py \
    -v ${INSTALL_PATH}/conf/opsany-paas/websocket/websocket.ini:/etc/supervisord.d/websocket.ini \
    -v /usr/share/zoneinfo:/usr/share/zoneinfo \
    -v /etc/localtime:/etc/localtime:ro \
    ${PAAS_DOCKER_REG}/opsany-paas-websocket:4.0.0
    
    #openresty
    shell_log "======PaaS Service: Start openresty Service======"
    # OpenResty
    sed -i "s/DOMAIN_NAME/${DOMAIN_NAME}/g" ${INSTALL_PATH}/conf/nginx-conf.d/opsany_paas.conf
    sed -i "s/LOCAL_IP/${LOCAL_IP}/g" ${INSTALL_PATH}/conf/nginx-conf.d/opsany_paas.conf
    sed -i "s/DOMAIN_NAME/${DOMAIN_NAME}/g" ${INSTALL_PATH}/conf/nginx-conf.d/opsany_proxy.conf
    sed -i "s/LOCAL_IP/${LOCAL_IP}/g" ${INSTALL_PATH}/conf/nginx-conf.d/opsany_proxy.conf
    docker run -d --restart=always --name opsany-base-openresty \
    -p 80:80 -p 443:443 -p 8011:8011 -p 8012:8012 \
    -v ${INSTALL_PATH}/logs:/opt/opsany/logs \
    -v ${INSTALL_PATH}/conf/nginx-conf.d:/etc/nginx/conf.d \
    -v ${INSTALL_PATH}/conf/nginx.conf:/etc/nginx/nginx.conf \
    -v ${INSTALL_PATH}/uploads:/opt/opsany/uploads \
    -v /etc/localtime:/etc/localtime:ro \
    ${PAAS_DOCKER_REG}/openresty:1.17.8.2-alpine

    # copy init script to websocket
    docker cp ../saas/ opsany-paas-websocket:/opt/opsany/
    docker cp ./init/ opsany-paas-websocket:/opt/opsany/
    shell_warning_log "======End: The end is a new beginning.======"
}

# Main
main(){
    case "$1" in
	install)
          install_check
          ssl_make
          opsany_init
          esb_init
          paas_install
          sleep 10
          mysql_init
          paas_start
	  ;;
	help|*)
		echo $"Usage: $0 {install|help}"
	        ;;
    esac
}

main $1

