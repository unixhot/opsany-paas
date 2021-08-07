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
    echo "----------------$CTIME ${SHELL_NAME} : ${LOG_INFO}----------------"
    echo "$CTIME ${SHELL_NAME} : ${LOG_INFO}" >> ${SHELL_LOG}
}

# Install Inspection
if [ ! -f ./install.config ];then
      echo "Please Copy install.config and Change: cp install.config.example install.config"
      exit
else
    source ./install.config
fi

# OS Type And repo
if [ -f /etc/redhat-release ];then
    OS_TYPE="CENTOS"
    CENTOS6=$(cat /proc/version | grep 'el6\.')
    CENTOS7=$(cat /proc/version | grep 'el7\.')
    CENTOS8=$(cat /proc/version | grep 'el8\.')
    if [ -n "$CENTOS6" ];then
            OS_VER=6
            curl -s -o /etc/yum.repos.d/epel.repo $EPEL6
        elif [ -n "$CENTOS7" ];then
            OS_VER=7
            curl -s -o /etc/yum.repos.d/epel.repo $EPEL7
        elif [ -n "$CENTOS8" ];then
            OS_VER=8
    fi
elif [ -f /etc/lsb-release ];then
        OS_TYPE="UBUNTU"
        OS_VER=$(cat /etc/lsb-release | grep DISTRIB_RELEASE | awk -F '=' {'print$2'})
else
    shell_log "This OS is not supported!" && exit
fi

# Create Self-signed Server Certificate
ssl_make(){
    # create dir for ssl
    if [ ! -d ./conf/nginx-conf.d/ssl ];then
      mkdir -p ./conf/nginx-conf.d/ssl
    fi
    cp ./conf/openssl.cnf ./conf/nginx-conf.d/ssl/
    cd ./conf/nginx-conf.d/ssl
    shell_log "Create server key..."
    openssl genrsa -des3 -passout pass:opsany -out $DOMAIN_NAME.key 2048 >/dev/null 2>&1

    shell_log "Create server certificate signing request..."
    SUBJECT="/C=CN/ST=BeiJing/L=BeiJing/O=BeiJing/OU=OpsAny/CN=OpsAny"
    openssl req -new -passin pass:opsany -subj $SUBJECT -key $DOMAIN_NAME.key -out $DOMAIN_NAME.csr >/dev/null 2>&1

    shell_log "Remove password..."
    mv $DOMAIN_NAME.key $DOMAIN_NAME.origin.key
    openssl rsa -passin pass:opsany -in $DOMAIN_NAME.origin.key  -out $DOMAIN_NAME.key >/dev/null 2>&1

    shell_log "Sign SSL certificate..."
    openssl x509 -req -days 3650 -extfile openssl.cnf -extensions 'v3_req'  -in $DOMAIN_NAME.csr -signkey $DOMAIN_NAME.key -out $DOMAIN_NAME.crt >/dev/null 2>&1
    openssl x509 -in ${DOMAIN_NAME}.crt -out ${DOMAIN_NAME}.pem -outform PEM >/dev/null 2>&1
    mv ${DOMAIN_NAME}.pem ${DOMAIN_NAME}.origin.pem
    cat ${DOMAIN_NAME}.key ${DOMAIN_NAME}.origin.pem > ${DOMAIN_NAME}.pem
    rm -f ./conf/openssl.cnf
}


# Check Install requirement
install_check(){
  DOCKER_PID=$(ps aux | grep '/usr/bin/containerd' | grep -v 'grep' | wc -l)
  if [ ${DOCKER_PID} -lt 1 ];then
      echo "Please install and start docker first!!!"
      exit
  fi
}

# Install Initialize
opsany_init(){
    shell_log "Start: Install Init"
    mkdir -p ${INSTALL_PATH}/{uploads/guacamole,uploads/workbench/icon,conf,esb,logs,saas/apps,saas/saasapp,salt-volume/certs,salt-volume/srv/pillar,salt-volume/srv/salt,salt-volume/etc,paasagent-volume,redis-volume,mongodb-volume,mysql-volume}
    cd $CDIR
    /bin/cp -r ../install/conf ${INSTALL_PATH}/
    /bin/cp -r ../uploads/* ${INSTALL_PATH}/uploads/
    /bin/cp -r ../paas-ce/saas/saas-logo/* ${INSTALL_PATH}/uploads/workbench/icon/
    ## init for esb
    /bin/cp -r ../paas-ce/paas/esb/components/generic/apis/ ${INSTALL_PATH}/esb/
    ## init for saltstack 
    /bin/cp -a ${CDIR}/../install/conf/salt ${INSTALL_PATH}/salt-volume/etc/
    /bin/cp -a ${CDIR}/../install/conf/salt/certs/* ${INSTALL_PATH}/salt-volume/certs/
    shell_log "End: Install Init"
}

# PaaS Share Service Start
paas_install(){
    # RabbitMQ
    shell_log "======Start RabbitMQ====="
    docker run -d --restart=always --name opsany-rabbitmq \
    -e RABBITMQ_DEFAULT_USER="$RABBITMQ_DEFAULT_USER" \
    -e RABBITMQ_DEFAULT_PASS="$RABBITMQ_DEFAULT_PASS" \
    -p 15672:15672 -p 5672:5672 \
    -v /etc/localtime:/etc/localtime:ro \
    ${PAAS_DOCKER_REG}/rabbitmq:3.8.9-management-alpine
    
    # Redis
    shell_log "======Start Redis======"
    docker run -d --restart=always --name opsany-redis \
    -p 6379:6379 -v ${INSTALL_PATH}/redis-volume:/data \
    -v ${INSTALL_PATH}/conf/redis.conf:/data/redis.conf \
    -v /etc/localtime:/etc/localtime:ro \
    ${PAAS_DOCKER_REG}/redis:6.0.9-alpine redis-server /data/redis.conf
    
    # MySQL
    shell_log "======Start MySQL======"
    docker run -d --restart=always --name opsany-mysql \
    -e MYSQL_ROOT_PASSWORD="$MYSQL_ROOT_PASSWORD" \
    -p 3306:3306 -v ${INSTALL_PATH}/mysql-volume:/var/lib/mysql \
    -v ${INSTALL_PATH}/conf/mysqld.cnf:/etc/mysql/mysql.conf.d/mysqld.cnf \
    -v ${INSTALL_PATH}/logs:/var/log/mysql \
    -v /etc/localtime:/etc/localtime:ro \
    ${PAAS_DOCKER_REG}/mysql:5.6.50 --character-set-server=utf8 --collation-server=utf8_general_ci
    
    # MongoDB
    shell_log "======Start MongoDB======"
    docker run -d --restart=always --name opsany-mongodb \
    -e MONGO_INITDB_ROOT_USERNAME="$MONGO_INITDB_ROOT_USERNAME" \
    -e MONGO_INITDB_ROOT_PASSWORD="$MONGO_INITDB_ROOT_PASSWORD" \
    -p 27017:27017 -v ${INSTALL_PATH}/mongodb-volume:/data/db \
    -v /etc/localtime:/etc/localtime:ro \
    ${PAAS_DOCKER_REG}/mongo:4.4.1-bionic
    
    # Guacd
    shell_log "======Start Guacd======"
    docker run -d --restart=always --name opsany-guacd \
    -p 4822:4822 \
    -v ${INSTALL_PATH}/uploads/guacamole:/srv/guacamole \
    -v /etc/localtime:/etc/localtime:ro \
    ${PAAS_DOCKER_REG}/guacd:1.2.0
}

# MySQL Initialize
mysql_init(){
    shell_log "======MySQL Initialize======"
    sleep 10
    cd ${CDIR}/../install/
    export MYSQL_PWD=${MYSQL_ROOT_PASSWORD}
    mysql -h "${LOCAL_IP}" -u root  -e "CREATE DATABASE IF NOT EXISTS opsany_paas DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;"
    mysql -h "${LOCAL_IP}" -u root  -e "grant all on opsany_paas.* to opsany@'%' identified by "\"${MYSQL_OPSANY_PASSWORD}\"";" 
    mysql -h "${LOCAL_IP}" -u root  opsany_paas < init/opsany-paas.sql
}

# ESB Initialize
esb_init(){
    shell_log "======ESB Initialize======"
    sed -i "s/dev.opsany.cn/$DOMAIN_NAME/g" ${INSTALL_PATH}/esb/apis/cmdb/toolkit/configs.py
    sed -i "s#/t/cmdb#/o/cmdb#g" ${INSTALL_PATH}/esb/apis/cmdb/toolkit/tools.py
    sed -i "s/dev.opsany.cn/$DOMAIN_NAME/g" ${INSTALL_PATH}/esb/apis/control/toolkit/configs.py
    sed -i "s#/t/control#/o/control#g" ${INSTALL_PATH}/esb/apis/control/toolkit/tools.py
    sed -i "s/dev.opsany.cn/$DOMAIN_NAME/g" ${INSTALL_PATH}/esb/apis/rbac/toolkit/configs.py
    sed -i "s#/t/rbac#/o/rbac#g" ${INSTALL_PATH}/esb/apis/rbac/toolkit/configs.py
    sed -i "s/dev.opsany.cn/$DOMAIN_NAME/g" ${INSTALL_PATH}/esb/apis/task/toolkit/configs.py
    sed -i "s#/t/job#/o/job#g" ${INSTALL_PATH}/esb/apis/task/toolkit/tools.py
    sed -i "s/dev.opsany.cn/$DOMAIN_NAME/g" ${INSTALL_PATH}/esb/apis/workbench/toolkit/configs.py
    sed -i "s#/t/workbench#/o/workbench#g" ${INSTALL_PATH}/esb/apis/workbench/toolkit/tools.py
    sed -i "s/dev.opsany.cn/$DOMAIN_NAME/g" ${INSTALL_PATH}/esb/apis/monitor/toolkit/configs.py
    sed -i "s#/t/monitor#/o/monitor#g" ${INSTALL_PATH}/esb/apis/monitor/toolkit/tools.py
    sed -i "s/dev.opsany.cn/$DOMAIN_NAME/g" ${INSTALL_PATH}/esb/apis/cmp/toolkit/configs.py
    sed -i "s#/t/cmp#/o/cmp#g" ${INSTALL_PATH}/esb/apis/cmp/toolkit/tools.py
    sed -i "s/dev.opsany.cn/$DOMAIN_NAME/g" ${INSTALL_PATH}/esb/apis/devops/toolkit/configs.py
    sed -i "s#/t/devops#/o/devops#g" ${INSTALL_PATH}/esb/apis/devops/toolkit/tools.py
}

# PaaS Configuration
paas_config(){
    shell_log "======PAAS Configuration======"
    # PaaS Config
    sed -i "s/PAAS_LOGIN_IP/${PAAS_LOGIN_IP}/g" ${INSTALL_PATH}/conf/settings_production.py.paas
    sed -i "s/PAAS_APPENGINE_IP/${PAAS_APPENGINE_IP}/g" ${INSTALL_PATH}/conf/settings_production.py.paas
    sed -i "s/DOMAIN_NAME/${DOMAIN_NAME}/g" ${INSTALL_PATH}/conf/settings_production.py.paas
    sed -i "s/LOCAL_IP/${LOCAL_IP}/g" ${INSTALL_PATH}/conf/settings_production.py.paas
    sed -i "s/MYSQL_SERVER_IP/${MYSQL_SERVER_IP}/g" ${INSTALL_PATH}/conf/settings_production.py.paas
    sed -i "s/MYSQL_OPSANY_PASSWORD/${MYSQL_OPSANY_PASSWORD}/g" ${INSTALL_PATH}/conf/settings_production.py.paas
    
    #Login Config
    sed -i "s/DOMAIN_NAME/${DOMAIN_NAME}/g" ${INSTALL_PATH}/conf/settings_production.py.login
    sed -i "s/LOCAL_IP/${LOCAL_IP}/g" ${INSTALL_PATH}/conf/settings_production.py.login
    sed -i "s/MYSQL_SERVER_IP/${MYSQL_SERVER_IP}/g" ${INSTALL_PATH}/conf/settings_production.py.login
    sed -i "s/MYSQL_OPSANY_PASSWORD/${MYSQL_OPSANY_PASSWORD}/g" ${INSTALL_PATH}/conf/settings_production.py.login
    
    # App Engine Config
    sed -i "s/MYSQL_SERVER_IP/${MYSQL_SERVER_IP}/g" ${INSTALL_PATH}/conf/settings_production.py.appengine
    sed -i "s/MYSQL_OPSANY_PASSWORD/${MYSQL_OPSANY_PASSWORD}/g" ${INSTALL_PATH}/conf/settings_production.py.appengine
    
    # ESB Config
    sed -i "s/PAAS_LOGIN_IP/${PAAS_LOGIN_IP}/g" ${INSTALL_PATH}/conf/settings_production.py.esb
    sed -i "s/PAAS_PAAS_IP/${PAAS_PAAS_IP}/g" ${INSTALL_PATH}/conf/settings_production.py.esb
    sed -i "s/REDIS_SERVER_IP/${REDIS_SERVER_IP}/g" ${INSTALL_PATH}/conf/settings_production.py.esb
    sed -i "s/REDIS_SERVER_PASSWORD/${REDIS_SERVER_PASSWORD}/g" ${INSTALL_PATH}/conf/settings_production.py.esb
    sed -i "s/MYSQL_SERVER_IP/${MYSQL_SERVER_IP}/g" ${INSTALL_PATH}/conf/settings_production.py.esb
    sed -i "s/MYSQL_OPSANY_PASSWORD/${MYSQL_OPSANY_PASSWORD}/g" ${INSTALL_PATH}/conf/settings_production.py.esb
    
    # Websocket
    sed -i "s/WEBSOCKET_GUACD_HOST/${WEBSOCKET_GUACD_HOST}/g" ${INSTALL_PATH}/conf/settings_production.py.websocket
    sed -i "s/REDIS_SERVER_IP/${REDIS_SERVER_IP}/g" ${INSTALL_PATH}/conf/settings_production.py.websocket
    sed -i "s/REDIS_SERVER_PASSWORD/${REDIS_SERVER_PASSWORD}/g" ${INSTALL_PATH}/conf/settings_production.py.websocket
    sed -i "s/MYSQL_SERVER_IP/${MYSQL_SERVER_IP}/g" ${INSTALL_PATH}/conf/settings_production.py.websocket
    sed -i "s/MYSQL_OPSANY_PASSWORD/${MYSQL_OPSANY_PASSWORD}/g" ${INSTALL_PATH}/conf/settings_production.py.websocket
    sed -i "s/dev.opsany.cn/${PAAS_PAAS_IP}/g" ${INSTALL_PATH}/conf/settings_production.py.websocket.init
    
    # OpenResty
    sed -i "s/DOMAIN_NAME/${DOMAIN_NAME}/g" ${INSTALL_PATH}/conf/nginx-conf.d/nginx_paas.conf
    sed -i "s/LOCAL_IP/${LOCAL_IP}/g" ${INSTALL_PATH}/conf/nginx-conf.d/nginx_paas.conf

    # Heartbeat
    sed -i "s/ES_SERVER_IP/${ES_SERVER_IP}/g" ${INSTALL_PATH}/conf/heartbeat.yml
    sed -i "s/ES_PASSWORD/${ES_PASSWORD}/g" ${INSTALL_PATH}/conf/heartbeat.yml
}

# PaaS Service Start
paas_start(){
    #paas
    shell_log "======Start paas Service======"
    docker run -d --restart=always --name opsany-paas-paas \
    -p 8001:8001 -v ${INSTALL_PATH}/logs:/opt/opsany/logs \
    -v ${INSTALL_PATH}/conf/settings_production.py.paas:/opt/opsany/paas/paas/conf/settings_production.py \
    -v /etc/localtime:/etc/localtime:ro \
    ${PAAS_DOCKER_REG}/opsany-paas-paas:${PAAS_VERSION}
    
    #login
    shell_log "======Start login Service======"
    docker run -d --restart=always --name opsany-paas-login \
    -p 8003:8003 -v ${INSTALL_PATH}/logs:/opt/opsany/logs \
    -v ${INSTALL_PATH}/conf/settings_production.py.login:/opt/opsany/paas/login/conf/settings_production.py \
    -v /etc/localtime:/etc/localtime:ro \
    ${PAAS_DOCKER_REG}/opsany-paas-login:${PAAS_VERSION}
    
    #esb
    shell_log "======Start esb Service======"
    docker run -d --restart=always --name opsany-paas-esb \
    -p 8002:8002 -v ${INSTALL_PATH}/logs:/opt/opsany/logs \
    -v ${INSTALL_PATH}/esb/apis:/opt/opsany/paas/esb/components/generic/apis \
    -v ${INSTALL_PATH}/conf/settings_production.py.esb:/opt/opsany/paas/esb/configs/default.py \
    -v /etc/localtime:/etc/localtime:ro \
    ${PAAS_DOCKER_REG}/opsany-paas-esb:${PAAS_VERSION}
    
    #appengine
    shell_log "======Start appengine Service======"
    docker run -d --restart=always --name opsany-paas-appengine \
    -p 8000:8000 -v ${INSTALL_PATH}/logs:/opt/opsany/logs \
    -v ${INSTALL_PATH}/conf/settings_production.py.appengine:/opt/opsany/paas/appengine/controller/settings.py \
    -v /etc/localtime:/etc/localtime:ro \
    ${PAAS_DOCKER_REG}/opsany-paas-appengine:${PAAS_VERSION}
    
    #websocket
    shell_log "======Start websocket Service======"
    docker run -d --restart=always --name opsany-paas-websocket \
    -p 8004:8004 -v ${INSTALL_PATH}/logs:/opt/opsany/logs \
    -v ${INSTALL_PATH}/uploads:/opt/opsany/uploads \
    -v ${INSTALL_PATH}/conf/settings_production.py.websocket:/opt/opsany/websocket/config/prod.py \
    -v ${INSTALL_PATH}/conf/settings_production.py.websocket.init:/opt/opsany/websocket/config/__init__.py \
    -v /etc/localtime:/etc/localtime:ro \
    ${PAAS_DOCKER_REG}/opsany-paas-websocket:${PAAS_VERSION}
    
    #openresty
    shell_log "======Start openresty Service======"
    docker run -d --restart=always --name opsany-openresty \
    -p 80:80 -p 443:443 -v ${INSTALL_PATH}/logs:/opt/opsany/logs \
    -v ${INSTALL_PATH}/conf/nginx-conf.d:/etc/nginx/conf.d \
    -v ${INSTALL_PATH}/conf/nginx.conf:/etc/nginx/nginx.conf \
    -v ${INSTALL_PATH}/uploads:/opt/opsany/uploads \
    -v /etc/localtime:/etc/localtime:ro \
    ${PAAS_DOCKER_REG}/openresty:1.17.8.2-alpine

}

# Start PaasAgent
paas_agent_start(){
    shell_log "======Register paas-agent Service======"
    sleep 10
    BK_PAAS_PRIVATE_ADDR=${LOCAL_IP}
    BK_PAASAGENT_SERVER_PORT=4245
    BK_PAASAGENT_NGINX_PROXY_PORT=8085
    BIND_ADDR=${LOCAL_IP}
    MODE=prod
    resp=$(curl -k --connect-timeout 10 -s -H 'Content-Type:application/x-www-form-urlencoded' \
        -X POST -d "agent_ip=$BIND_ADDR&mode=$MODE&agent_port=$BK_PAASAGENT_SERVER_PORT&web_port=$BK_PAASAGENT_NGINX_PROXY_PORT" \
        "https://$BK_PAAS_PRIVATE_ADDR/v1/agent/init/")
    token=$(jq -r .token <<<"$resp" 2>/dev/null)
    sid=$(jq -r .sid <<<"$resp" 2>/dev/null)
    
    if [[ -z "$token" || -z "$sid" ]]; then
        shell_log "Register Faild：$resp"
    else
        shell_log "Register Succeed"
    fi
    
    sed -i "s/BK_PAASAGENT_SID/$sid/g" ${INSTALL_PATH}/conf/paas_agent_config.yaml
    sed -i "s/BK_PAASAGENT_TOKEN/$token/g" ${INSTALL_PATH}/conf/paas_agent_config.yaml
    sed -i "s/LOCAL_IP/${LOCAL_IP}/g" ${INSTALL_PATH}/conf/paas_agent_config.yaml
    
    shell_log "======Start paas-agent Service======"
    docker run -d --restart=always --name opsany-paas-paasagent \
    -p 4245:4245 -p 8085:8085 \
    -v ${INSTALL_PATH}/logs:/opt/opsany/logs/ \
    -v ${INSTALL_PATH}/conf/paas_agent_config.yaml:/opt/opsany/paas-agent/etc/paas_agent_config.yaml \
    -v ${INSTALL_PATH}/conf/paasagent.conf:/etc/nginx/conf.d/paasagent.conf \
    -v ${INSTALL_PATH}/uploads:/opt/opsany/uploads \
    -v ${INSTALL_PATH}/saas/apps:/opt/opsany/paas-agent/apps \
    -v ${INSTALL_PATH}/saas/saasapp:/opt/opsany/paas-agent/saasapp \
    -v ${INSTALL_PATH}/salt-volume/srv/:/srv/ \
    -v ${INSTALL_PATH}/salt-volume/etc/salt/:/etc/salt/ \
    -v ${INSTALL_PATH}/salt-volume/cache/:/var/cache/salt/ \
    -v /etc/localtime:/etc/localtime:ro \
    ${PAAS_DOCKER_REG}/opsany-paas-paasagent:${PAAS_VERSION}
    
    sleep 10
    
    # PaasAgent healthz
    code=$(curl -s -o /dev/null -w "%{http_code}" http://$BIND_ADDR:$BK_PAASAGENT_SERVER_PORT/healthz )
    if [[ $code != 200 ]]; then
        echo "paasagent($MODE)Start Faild，Check (http://$BIND_ADDR:$BK_PAASAGENT_SERVER_PORT/healthz) Error" >&2
        exit 1
    fi
    
    # Activate PaasAgent
    shell_log "====== Activate paas-agent======"
    resp=$(curl -k -s "https://$BK_PAAS_PRIVATE_ADDR/v1/agent/init/?agent_ip=$BIND_ADDR")
    if [[ $(jq -r .agent_ip <<<"$resp" ) = "$BIND_ADDR" ]]; then
        shell_log "Activate PaaSAgent($MODE): $BIND_ADDR:$BK_PAASAGENT_SERVER_PORT Succeed"
    else
        echo "Activate PaaSAgent($MODE): $BIND_ADDR:$BK_PAASAGENT_SERVER_PORT Faild [$resp]" >&2
        exit 2
    fi
}

# Active RabbitMQ
rabbitmq_active(){
    shell_log "======Activate RabbitMQ======"
    curl -k --connect-timeout 10 \
            -H 'Content-Type:application/x-www-form-urlencoded' \
            -X POST \
            -d "mq_ip=$RABBIT_SERVER_IP&username=$RABBITMQ_DEFAULT_USER&password=$RABBITMQ_DEFAULT_PASS" \
            "https://$BK_PAAS_PRIVATE_ADDR/v1/rabbitmq/init/"
    echo ""
    shell_log "======The end is the beginning.======"
    }

# Main
main(){
    install_check
    ssl_make
    opsany_init
    paas_install
    sleep 10
    mysql_init
    esb_init
    paas_config
    paas_start
    paas_agent_start
    rabbitmq_active
}

main
