#!/bin/bash
#******************************************
# Author:       Jason Zhao
# Email:        zhaoshundong@opsany.com
# Organization: OpsAny https://www.opsany.com/
# Description:  StackStorm Install Script
#******************************************

# Data/Time
CTIME=$(date "+%Y-%m-%d-%H-%M")

# Shell Envionment Variables
CDIR=$(pwd)
SHELL_NAME="st2-install.sh"
SHELL_LOG="${SHELL_NAME}.log"
ST2_VERSION="3.8.0"

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

# Check Install requirement
install_init(){
    shell_log "=====Begin: Init======"
    # StackStorm Docker Volume
    mkdir -p ${INSTALL_PATH}/st2-volume/{keys,packs-configs,virtualenvs,ssh}
    mkdir -p ${INSTALL_PATH}/st2-volume/packs.dev
    chmod -R 777 ${INSTALL_PATH}/st2-volume/packs-configs
    /bin/cp -r ./conf/stackstorm/* ${INSTALL_PATH}/st2-volume/
    sed -i "s/LOCAL_IP/${LOCAL_IP}/g" ${INSTALL_PATH}/st2-volume/files/st2.docker.conf
    sed -i "s/REDIS_SERVER_IP/${REDIS_SERVER_IP}/g" ${INSTALL_PATH}/st2-volume/files/st2.docker.conf
    sed -i "s/REDIS_SERVER_PORT/${REDIS_SERVER_PORT}/g" ${INSTALL_PATH}/st2-volume/files/st2.docker.conf
    sed -i "s/REDIS_SERVER_USERNAME/${REDIS_SERVER_USERNAME}/g" ${INSTALL_PATH}/st2-volume/files/st2.docker.conf
    sed -i "s/REDIS_SERVER_PASSWORD/${REDIS_SERVER_PASSWORD}/g" ${INSTALL_PATH}/st2-volume/files/st2.docker.conf
    sed -i "s/RABBIT_SERVER_IP/${RABBIT_SERVER_IP}/g" ${INSTALL_PATH}/st2-volume/files/st2.docker.conf
    sed -i "s/RABBITMQ_DEFAULT_USER/${RABBITMQ_DEFAULT_USER}/g" ${INSTALL_PATH}/st2-volume/files/st2.docker.conf
    sed -i "s/RABBITMQ_DEFAULT_PASS/${RABBITMQ_DEFAULT_PASS}/g" ${INSTALL_PATH}/st2-volume/files/st2.docker.conf
    sed -i "s/MONGO_SERVER_IP/${MONGO_SERVER_IP}/g" ${INSTALL_PATH}/st2-volume/files/st2.docker.conf
    sed -i "s/MONGO_SERVER_PORT/${MONGO_SERVER_PORT}/g" ${INSTALL_PATH}/st2-volume/files/st2.docker.conf
    sed -i "s/MONGO_EVENT_PASSWORD/${MONGO_EVENT_PASSWORD}/g" ${INSTALL_PATH}/st2-volume/files/st2.docker.conf
    sed -i "s/MONGO_EVENT_PASSWORD/${MONGO_EVENT_PASSWORD}/g" ${INSTALL_PATH}/st2-volume/mongodb_event.js
}

rabbitmq_install(){
    # RabbitMQ
    shell_log "Start RabbitMQ"
    docker run -d --restart=always --name opsany-st2-rabbitmq \
    -e RABBITMQ_DEFAULT_USER="$RABBITMQ_DEFAULT_USER" \
    -e RABBITMQ_DEFAULT_PASS="$RABBITMQ_DEFAULT_PASS" \
    -p 15672:15672 -p 5672:5672 -p 15692:15692 \
    -v /etc/localtime:/etc/localtime:ro \
    ${PAAS_DOCKER_REG}/rabbitmq:3.8.9-management-alpine
}

# Redis
redis_install(){
    shell_log "======Base Service: Start Redis======"
    mkdir -p ${INSTALL_PATH}/st2-redis-volume
    /bin/cp ${CDIR}/conf/redis/redis.conf ${INSTALL_PATH}/st2-redis-volume/
    sed -i "s/"REDIS_SERVER_PASSWORD"/"${REDIS_SERVER_PASSWORD}"/g" ${INSTALL_PATH}/st2-redis-volume/redis.conf
    docker run -d --restart=always --name opsany-st2-redis \
    -p 6379:6379 -v ${INSTALL_PATH}/st2-redis-volume:/data \
    -v ${INSTALL_PATH}/st2-redis-volume/redis.conf:/data/redis.conf \
    -v /etc/localtime:/etc/localtime:ro \
    ${PAAS_DOCKER_REG}/redis:6.0.9-alpine redis-server /data/redis.conf
}

# MongoDB
mongodb_install(){
    shell_log "======Base Service: Start MongoDB======"
    mkdir -p ${INSTALL_PATH}/st2-mongodb-volume
    docker run -d --restart=always --name opsany-st2-mongodb \
    -e MONGO_INITDB_ROOT_USERNAME="$MONGO_INITDB_ROOT_USERNAME" \
    -e MONGO_INITDB_ROOT_PASSWORD="$MONGO_INITDB_ROOT_PASSWORD" \
    -p 27017:27017 -v ${INSTALL_PATH}/st2-mongodb-volume:/data/db \
    -v /etc/localtime:/etc/localtime:ro \
    ${PAAS_DOCKER_REG}/mongo:4.4.1-bionic
    #${PAAS_DOCKER_REG}/mongo:5.0.3
    sleep 15
    docker cp ${INSTALL_PATH}/st2-volume/mongodb_event.js opsany-st2-mongodb:/opt/
    docker exec -e MONGO_INITDB_ROOT_USERNAME=$MONGO_INITDB_ROOT_USERNAME \
                -e MONGO_INITDB_ROOT_PASSWORD=$MONGO_INITDB_ROOT_PASSWORD \
                opsany-st2-mongodb /bin/bash -c "/usr/bin/mongo -u $MONGO_INITDB_ROOT_USERNAME -p $MONGO_INITDB_ROOT_PASSWORD /opt/mongodb_event.js"
    shell_log "======MongoDB: MongoDB Initialize End======"

}

# 创建证书
st2makesecrets_install(){
    shell_log "=====Start makesecrets======"
    docker run --restart=on-failure --name opsany-st2-makesecrets \
    -v ${INSTALL_PATH}/st2-volume/scripts/makesecrets.sh:/makesecrets.sh \
    -v ${INSTALL_PATH}/st2-volume/keys:/etc/st2/keys:rw \
    ${PAAS_DOCKER_REG}/st2actionrunner:${ST2_VERSION} /makesecrets.sh
}

# 启动 st2api 服务
st2api_install(){
    shell_log "=====Start st2api======"
    docker run -d --rm --name opsany-st2-api-copy \
    -v ${INSTALL_PATH}/st2-volume/files/st2.docker.conf:/etc/st2/st2.docker.conf:ro \
    -v ${INSTALL_PATH}/st2-volume/files/st2.user.conf:/etc/st2/st2.user.conf:ro \
    ${PAAS_DOCKER_REG}/st2api:${ST2_VERSION}
    docker cp  opsany-st2-api-copy:/opt/stackstorm/packs ${INSTALL_PATH}/st2-volume/
    docker stop opsany-st2-api-copy
    
    docker run -d --restart=always --name opsany-st2-api \
    -e ST2_AUTH_URL="http://${LOCAL_IP}:8017/" \
    -e ST2_API_URL="http://${LOCAL_IP}:8018/" \
    -e ST2_STREAM_URL="http://${LOCAL_IP}:8019/" \
    -v ${INSTALL_PATH}/st2-volume/files/st2.docker.conf:/etc/st2/st2.docker.conf:ro \
    -v ${INSTALL_PATH}/st2-volume/files/st2.user.conf:/etc/st2/st2.user.conf:ro \
    -v ${INSTALL_PATH}/st2-volume/keys:/etc/st2/keys:ro \
    -v ${INSTALL_PATH}/st2-volume/packs-configs:/opt/stackstorm/configs:rw \
    -v ${INSTALL_PATH}/st2-volume/packs:/opt/stackstorm/packs:rw \
    -v ${INSTALL_PATH}/st2-volume/files/rbac:/opt/stackstorm/rbac:rw \
    -v ${INSTALL_PATH}/st2-volume/packs.dev:/opt/stackstorm/packs.dev:rw \
    -p 8018:9101 \
    ${PAAS_DOCKER_REG}/st2api:${ST2_VERSION}
}

# 启动 st2stream 服务
st2stream_install(){
    shell_log "=====Start st2stream======"
    docker run -d --restart=always --name opsany-st2-stream \
    -v ${INSTALL_PATH}/st2-volume/files/st2.docker.conf:/etc/st2/st2.docker.conf:ro \
    -v ${INSTALL_PATH}/st2-volume/files/st2.user.conf:/etc/st2/st2.user.conf:ro \
    -p 8019:9102 \
    ${PAAS_DOCKER_REG}/st2stream:${ST2_VERSION}
}

# 启动 st2auth 服务
st2auth_install(){
    shell_log "=====Start st2auth======"
    docker run -d --restart=always --name opsany-st2-auth \
    -v ${INSTALL_PATH}/st2-volume/files/st2.docker.conf:/etc/st2/st2.docker.conf:ro \
    -v ${INSTALL_PATH}/st2-volume/files/st2.user.conf:/etc/st2/st2.user.conf:ro \
    -v ${INSTALL_PATH}/st2-volume/files/htpasswd:/etc/st2/htpasswd:ro \
    -p 8017:9100 \
    ${PAAS_DOCKER_REG}/st2auth:${ST2_VERSION}
}

# 启动 st2scheduler 服务
st2scheduler_install(){
    shell_log "=====Start st2scheduler======"
    docker run -d --restart=always --name opsany-st2-scheduler \
    -v ${INSTALL_PATH}/st2-volume/files/st2.docker.conf:/etc/st2/st2.docker.conf:ro \
    -v ${INSTALL_PATH}/st2-volume/files/st2.user.conf:/etc/st2/st2.user.conf:ro \
    ${PAAS_DOCKER_REG}/st2scheduler:${ST2_VERSION}
}

# 启动 st2workflowengine 服务
st2workflowengine_install(){
    shell_log "=====Start st2workflowengine======"
    docker run -d --restart=always --name opsany-st2-workflowengine \
    -v ${INSTALL_PATH}/st2-volume/files/st2.docker.conf:/etc/st2/st2.docker.conf:ro \
    -v ${INSTALL_PATH}/st2-volume/files/st2.user.conf:/etc/st2/st2.user.conf:ro \
    -v ${INSTALL_PATH}/st2-volume/keys:/etc/st2/keys:ro \
    ${PAAS_DOCKER_REG}/st2workflowengine:${ST2_VERSION}
}

# 启动 st2actionrunner 服务
st2actionrunner_install(){
    shell_log "=====Start st2actionrunner======"
    docker run -d --restart=always --name opsany-st2-actionrunner \
    -v ${INSTALL_PATH}/st2-volume/files/st2.docker.conf:/etc/st2/st2.docker.conf:ro \
    -v ${INSTALL_PATH}/st2-volume/files/st2.user.conf:/etc/st2/st2.user.conf:ro \
    -v ${INSTALL_PATH}/st2-volume/packs-configs:/opt/stackstorm/configs:rw \
    -v ${INSTALL_PATH}/st2-volume/packs:/opt/stackstorm/packs:rw \
    -v ${INSTALL_PATH}/st2-volume/packs.dev:/opt/stackstorm/packs.dev:rw \
    -v ${INSTALL_PATH}/st2-volume/virtualenvs:/opt/stackstorm/virtualenvs:rw \
    -v ${INSTALL_PATH}/st2-volume/ssh:/home/stanley/.ssh \
    -v ${INSTALL_PATH}/st2-volume/keys:/etc/st2/keys:ro \
    ${PAAS_DOCKER_REG}/st2actionrunner:${ST2_VERSION}
}

# 启动 st2garbagecollector 服务
st2garbagecollector_install(){
    shell_log "=====Start st2garbagecollector======"
    docker run -d --restart=always --name opsany-st2-garbagecollector \
    -v ${INSTALL_PATH}/st2-volume/files/st2.docker.conf:/etc/st2/st2.docker.conf:ro \
    -v ${INSTALL_PATH}/st2-volume/files/st2.user.conf:/etc/st2/st2.user.conf:ro \
    ${PAAS_DOCKER_REG}/st2garbagecollector:${ST2_VERSION}
}

# 启动 st2notifier 服务
st2notifier_install(){
    shell_log "=====Start st2notifier======"
    docker run -d --restart=always --name opsany-st2-notifier \
    -v ${INSTALL_PATH}/st2-volume/files/st2.docker.conf:/etc/st2/st2.docker.conf:ro \
    -v ${INSTALL_PATH}/st2-volume/files/st2.user.conf:/etc/st2/st2.user.conf:ro \
    ${PAAS_DOCKER_REG}/st2notifier:${ST2_VERSION}
}

# 启动 st2rulesengine 服务
st2rulesengine_install(){
    shell_log "=====Start st2rulesengine======"
    docker run -d --restart=always --name opsany-st2-rulesengine \
    -v ${INSTALL_PATH}/st2-volume/files/st2.docker.conf:/etc/st2/st2.docker.conf:ro \
    -v ${INSTALL_PATH}/st2-volume/files/st2.user.conf:/etc/st2/st2.user.conf:ro \
    ${PAAS_DOCKER_REG}/st2rulesengine:${ST2_VERSION}
}

# 启动 st2sensorcontainer 服务
st2sensorcontainer_install(){
    shell_log "=====Start st2sensorcontainer======"
    docker run -d --restart=always --name opsany-st2-sensorcontainer \
    -v ${INSTALL_PATH}/st2-volume/files/st2.docker.conf:/etc/st2/st2.docker.conf:ro \
    -v ${INSTALL_PATH}/st2-volume/files/st2.user.conf:/etc/st2/st2.user.conf:ro \
    -v ${INSTALL_PATH}/st2-volume/virtualenvs:/opt/stackstorm/virtualenvs:ro \
    -v ${INSTALL_PATH}/st2-volume/packs:/opt/stackstorm/packs:ro \
    -v ${INSTALL_PATH}/st2-volume/packs-configs:/opt/stackstorm/configs:ro \
    -v ${INSTALL_PATH}/st2-volume/packs.dev:/opt/stackstorm/packs.dev:ro \
    ${PAAS_DOCKER_REG}/st2sensorcontainer:${ST2_VERSION}
}

# 启动 st2timersengine 服务
st2timersengine_install(){
    shell_log "=====Start st2timersengine======"
    docker run -d --restart=always --name opsany-st2-timersengine \
    -v ${INSTALL_PATH}/st2-volume/files/st2.docker.conf:/etc/st2/st2.docker.conf:ro \
    ${PAAS_DOCKER_REG}/st2timersengine:${ST2_VERSION}
}

st2client_install(){
# 启动 st2client 服务
    shell_log "=====Start st2client======"
    docker run -d --restart=always --name opsany-st2-client \
    -e ST2CLIENT=1 \
    -e ST2_AUTH_URL="http://${LOCAL_IP}:8017/" \
    -e ST2_API_URL="http://${LOCAL_IP}:8018/" \
    -e ST2_STREAM_URL="http://${LOCAL_IP}:8019/" \
    -e TZ=${TZ:-Asia/Shanghai} \
    -v ${INSTALL_PATH}/st2-volume/files/st2.docker.conf:/etc/st2/st2.docker.conf:ro \
    -v ${INSTALL_PATH}/st2-volume/files/st2.user.conf:/etc/st2/st2.user.conf:ro \
    -v ${INSTALL_PATH}/st2-volume/keys:/etc/st2/keys:ro \
    -v ${INSTALL_PATH}/st2-volume/packs-configs:/opt/stackstorm/configs:rw \
    -v ${INSTALL_PATH}/st2-volume/packs:/opt/stackstorm/packs:rw \
    -v ${INSTALL_PATH}/st2-volume/files/rbac:/opt/stackstorm/rbac:rw \
    -v ${INSTALL_PATH}/st2-volume/packs.dev:/opt/stackstorm/packs.dev:rw \
    -v ${INSTALL_PATH}/st2-volume/files/st2-cli.conf:/root/.st2/config \
    -v ${INSTALL_PATH}/st2-volume/scripts/st2client-startup.sh:/st2client-startup.sh \
    ${PAAS_DOCKER_REG}/st2actionrunner:${ST2_VERSION} /st2client-startup.sh
}

# 启动 st2web 服务
st2web_install(){
    shell_log "=====Start st2web======"
    docker run -d --restart=always --name opsany-st2-web \
    -e ST2_AUTH_URL="http://${LOCAL_IP}:8017/" \
    -e ST2_API_URL="http://${LOCAL_IP}:8018/" \
    -e ST2_STREAM_URL="http://${LOCAL_IP}:8019/" \
    -e ST2WEB_HTTPS=${ST2WEB_HTTPS:-0} \
    -p "${ST2_EXPOSE_HTTP:-0.0.0.0:8005}:80" \
    ${PAAS_DOCKER_REG}/st2web:${ST2_VERSION}
}

st2_uninstall(){
    shell_log "=====Uninstall StackStorm======"
    docker stop opsany-st2-stream
    docker stop opsany-st2-client
    docker stop opsany-st2-timersengine
    docker stop opsany-st2-sensorcontainer
    docker stop opsany-st2-rulesengine
    docker stop opsany-st2-notifier
    docker stop opsany-st2-garbagecollector
    docker stop opsany-st2-actionrunner
    docker stop opsany-st2-workflowengine
    docker stop opsany-st2-scheduler
    docker stop opsany-st2-auth
    docker stop opsany-st2-api
    docker stop opsany-st2-web
    docker stop opsany-st2-mongodb
    docker stop opsany-st2-redis
    docker stop opsany-st2-rabbitmq
    docker rm opsany-st2-stream
    docker rm opsany-st2-client
    docker rm opsany-st2-timersengine
    docker rm opsany-st2-sensorcontainer
    docker rm opsany-st2-rulesengine
    docker rm opsany-st2-notifier
    docker rm opsany-st2-garbagecollector
    docker rm opsany-st2-actionrunner
    docker rm opsany-st2-workflowengine
    docker rm opsany-st2-scheduler
    docker rm opsany-st2-auth
    docker rm opsany-st2-api
    docker rm opsany-st2-web
    docker rm opsany-st2-mongodb
    docker rm opsany-st2-redis
    docker rm opsany-st2-rabbitmq
    docker rm opsany-st2-makesecrets
    rm -rf ${INSTALL_PATH}/st2-redis-volume
    rm -rf ${INSTALL_PATH}/st2-mongodb-volume
    rm -rf ${INSTALL_PATH}/st2-volume
}

# Main
main(){
    case "$1" in
    st2)
        install_init
        rabbitmq_install
        st2makesecrets_install
        st2api_install
        st2stream_install
        st2auth_install
        st2scheduler_install
        st2workflowengine_install
        st2garbagecollector_install
        st2actionrunner_install
        st2notifier_install
        st2rulesengine_install
        st2sensorcontainer_install
        st2timersengine_install
        st2client_install
        st2web_install
        ;;
    all)
        install_init
        rabbitmq_install
        redis_install
        mongodb_install
        st2makesecrets_install
        st2api_install
        st2stream_install
        st2auth_install
        st2scheduler_install
        st2workflowengine_install
        st2garbagecollector_install
        st2actionrunner_install
        st2notifier_install
        st2rulesengine_install
        st2sensorcontainer_install
        st2timersengine_install
        st2client_install
        st2web_install
        ;;
    uninstall)
        st2_uninstall
        ;;
    help|*)
        echo $"Usage: $0 {st2|all|uninstall|help}"
        ;;
    esac
}

main $1
