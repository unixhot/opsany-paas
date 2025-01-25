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
ADMIN_PASSWORD=""

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
    mkdir -p ${INSTALL_PATH}/{uploads,conf,logs,prometheus-volume/conf,prometheus-volume/data,consul-volume/data,consul-volume/config,uploads/prometheus-config/rules,prometheus-volume/template,prometheus-volume/alertmanager}
    cd $CDIR
    /bin/cp -r ./conf/prometheus/* ${INSTALL_PATH}/prometheus-volume/conf/
    /bin/cp conf/consul.hcl ${INSTALL_PATH}/consul-volume/config/
    chmod -R 777 ${INSTALL_PATH}/prometheus-volume/
    pip3 install requests==2.25.1 grafana-api==1.0.3 mysql-connector==2.2.9 SQLAlchemy==1.4.22 bcrypt==3.2.2 \
             -i http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com
    shell_log "End: Install Init"
}

consul_install(){
    shell_log "Start: Consul Install..."
    CONSUL_TOKEN=$(uuid -v4)
    echo $CONSUL_TOKEN > ${INSTALL_PATH}/conf/.consul_token
    sed -i "s#PROM_CONSUL_SERVER#$PROXY_LOCAL_IP#g" ${INSTALL_PATH}/prometheus-volume/conf/prometheus.yml
    sed -i "s#CONSUL_TOKEN#$CONSUL_TOKEN#g" ${INSTALL_PATH}/prometheus-volume/conf/prometheus.yml
    sed -i "s#CONSUL_TOKEN#$CONSUL_TOKEN#g" ${INSTALL_PATH}/consul-volume/config/consul.hcl
    docker run --name opsany-base-consul -d --restart=always --privileged \
           -p 8500:8500 \
           -v ${INSTALL_PATH}/consul-volume/config:/consul/config \
           -v ${INSTALL_PATH}/consul-volume/data:/consul/data \
           ${PAAS_DOCKER_REG}/consul:1.12.3
    shell_log "======Consul Token: ${CONSUL_TOKEN}======"
}

prometheus_install(){
    # Prometheus Server Basic Auth
    PROM_SERVER_HASH=$(python3 ../saas/prom-pass.py $PROM_SERVER_PASSWD)
    sed -i "s#PROM_SERVER_HASH#$PROM_SERVER_HASH#g" ${INSTALL_PATH}/prometheus-volume/conf/web.yml
    sed -i "s#LOCAL_IP#$PROXY_LOCAL_IP#g" ${INSTALL_PATH}/prometheus-volume/conf/prometheus.yml
    sed -i "s#PROM_SERVER_PASSWD#$PROM_SERVER_PASSWD#g" ${INSTALL_PATH}/prometheus-volume/conf/prometheus.yml

    # Prometheus Release Date: 2022-04-21 https://hub.docker.com/u/prom
    shell_log "======Start Prometheus Server======"
    docker run -d --restart=always --name opsany-base-prometheus-server \
    -p 9090:9090 \
    -v ${INSTALL_PATH}/prometheus-volume/data/:/prometheus \
    -v ${INSTALL_PATH}/uploads/prometheus-config/rules/:/var/lib/prometheus-config/rules \
    -v ${INSTALL_PATH}/prometheus-volume/conf/prometheus.yml:/etc/prometheus/prometheus.yml \
    -v ${INSTALL_PATH}/prometheus-volume/conf/web.yml:/etc/prometheus/web.yml \
    -v /etc/localtime:/etc/localtime:ro \
    ${PAAS_DOCKER_REG}/prometheus:v2.35.0 --config.file=/etc/prometheus/prometheus.yml --storage.tsdb.path=/prometheus --web.console.libraries=/usr/share/prometheus/console_libraries --web.console.templates=/usr/share/prometheus/consoles --web.config.file=/etc/prometheus/web.yml --web.enable-lifecycle

    # Prometheus Node Exporter Release Date: 2021-12-01 https://hub.docker.com/u/prom
    #shell_log "======Start Prometheus Node_Exporter======"
    #docker run -d --restart=always --name opsany-prometheus-node_exporter \
    #-p 9100:9100 \
    #-v /etc/localtime:/etc/localtime:ro \
    #${PAAS_DOCKER_REG}/node-exporter:v1.3.1
}

alertmanager_install(){
    # Determine if there is a configuration file
    if [ ! -d "${INSTALL_PATH}/prometheus-volume/alertmanager/" ]; then
    mkdir -p "${INSTALL_PATH}/prometheus-volume/alertmanager/"
        echo "Directory created: ${INSTALL_PATH}/prometheus-volume/alertmanager/"
    else
        echo "Directory already exists: ${INSTALL_PATH}/prometheus-volume/alertmanager/"
    fi
    if [ ! -d "${INSTALL_PATH}/prometheus-volume/template/" ]; then
    mkdir -p "${INSTALL_PATH}/prometheus-volume/template/"
        echo "Directory created: ${INSTALL_PATH}/prometheus-volume/template/"
    else
        echo "Directory already exists: ${INSTALL_PATH}/prometheus-volume/template/"
    fi
    if [ ! -f "${INSTALL_PATH}/prometheus-volume/conf/alertmanager.yml" ]; then
    /bin/cp  ./conf/prometheus/alertmanager.yml "${INSTALL_PATH}/prometheus-volume/conf/alertmanager.yml"
        echo "Configuration file created: ${INSTALL_PATH}/prometheus-volume/conf/alertmanager.yml"
    else
        echo "The configuration file already exists: ${INSTALL_PATH}/prometheus-volume/conf/alertmanager.yml"
    fi
    /bin/cp  ./conf/prometheus/prometheus.yml "${INSTALL_PATH}/prometheus-volume/conf/prometheus.yml"    
    # Alertmanager Server Basic Auth
    CONSUL_TOKEN=`cat ${INSTALL_PATH}/conf/.consul_token`
    sed -i "s#PROM_CONSUL_SERVER#$PROXY_LOCAL_IP#g" ${INSTALL_PATH}/prometheus-volume/conf/prometheus.yml
    sed -i "s#CONSUL_TOKEN#$CONSUL_TOKEN#g" ${INSTALL_PATH}/prometheus-volume/conf/prometheus.yml
    sed -i "s#LOCAL_IP#$PROXY_LOCAL_IP#g" ${INSTALL_PATH}/prometheus-volume/conf/prometheus.yml
    sed -i "s#PROM_SERVER_PASSWD#$PROM_SERVER_PASSWD#g" ${INSTALL_PATH}/prometheus-volume/conf/prometheus.yml

    # restart opsany-base-prometheus-server
    docker restart opsany-base-prometheus-server

    # Alertmanager Release Date: 2024-03-21 https://hub.docker.com/r/prom/alertmanager
    shell_log "======Start Alertmanager Server======"
    docker run -d --restart=always --name opsany-base-alertmanager-server \
    -p 9093:9093 \
    -v ${INSTALL_PATH}/prometheus-volume/template/:/etc/alertmanager/template \
    -v ${INSTALL_PATH}/prometheus-volume/conf/alertmanager.yml:/etc/alertmanager/alertmanager.yml \
    -v ${INSTALL_PATH}/prometheus-volume/conf/web.yml:/etc/alertmanager/web.yml \
    -v ${INSTALL_PATH}/prometheus-volume/alertmanager/:/alertmanager \
    -v /etc/localtime:/etc/localtime:ro \
    -d ${PAAS_DOCKER_REG}/alertmanager:v0.27.0 --config.file=/etc/alertmanager/alertmanager.yml --storage.path=/alertmanager --web.config.file=/etc/alertmanager/web.yml
}

blackbox-exporter_install(){
    # Determine if there is a configuration file
    if [ ! -f "${INSTALL_PATH}/prometheus-volume/conf/blackbox.yml" ]; then
    /bin/cp  ./conf/prometheus/blackbox.yml "${INSTALL_PATH}/prometheus-volume/conf/blackbox.yml"
        echo "Configuration file created: ${INSTALL_PATH}/prometheus-volume/conf/blackbox.yml"
    else
        echo "The configuration file already exists: ${INSTALL_PATH}/prometheus-volume/conf/blackbox.yml"
    fi
    /bin/cp  ./conf/prometheus/prometheus.yml "${INSTALL_PATH}/prometheus-volume/conf/prometheus.yml"     
    # Alertmanager Server Basic Auth
    CONSUL_TOKEN=`cat ${INSTALL_PATH}/conf/.consul_token`
    sed -i "s#PROM_CONSUL_SERVER#$PROXY_LOCAL_IP#g" ${INSTALL_PATH}/prometheus-volume/conf/prometheus.yml
    sed -i "s#CONSUL_TOKEN#$CONSUL_TOKEN#g" ${INSTALL_PATH}/prometheus-volume/conf/prometheus.yml
    sed -i "s#LOCAL_IP#$PROXY_LOCAL_IP#g" ${INSTALL_PATH}/prometheus-volume/conf/prometheus.yml
    sed -i "s#PROM_SERVER_PASSWD#$PROM_SERVER_PASSWD#g" ${INSTALL_PATH}/prometheus-volume/conf/prometheus.yml

    # restart opsany-base-prometheus-server
    docker restart opsany-base-prometheus-server

    shell_log "======Start blackbox-exporter======"
    docker run -itd \
    -p 9115:9115 \
    --name opsany-base-blackbox-exporter \
    -v ${INSTALL_PATH}/prometheus-volume/conf/blackbox.yml:/config/blackbox.yml \
    ${PAAS_DOCKER_REG}/blackbox-exporter:v0.25.0 --config.file=/config/blackbox.yml
}

prometheus_uninstall(){
    docker stop opsany-base-prometheus-server
    docker rm opsany-base-prometheus-server
    docker stop opsany-base-consul
    docker rm opsany-base-consul
    docker stop opsany-base-alertmanager-server
    docker rm opsany-base-alertmanager-server
    docker stop opsany-base-blackbox-exporter
    docker rm opsany-base-blackbox-exporter
    rm -rf ${INSTALL_PATH}/prometheus-volume/*
    rm -rf ${INSTALL_PATH}/consul-volume/*
}

prom_init(){
  # DOMAIN_NAME LOCAL_IP ADMIN_PASSWORD PROM_SERVER_PASSWD CONSUL_TOKEN
  if [ -z "$ADMIN_PASSWORD" ];then
        source ${INSTALL_PATH}/conf/.passwd_env
  fi
  python3 ../saas/init-ee-prometheus.py --domain $DOMAIN_NAME --local_ip $LOCAL_IP --username admin --password $ADMIN_PASSWORD \
  --prom_username  admin --prom_password $PROM_SERVER_PASSWD --consul_token $CONSUL_TOKEN \
  --alertmanager_username admin --alertmanager_password $PROM_SERVER_PASSWD
}


# Main
main(){
    case "$1" in
	all)
            install_check
            install_init
            consul_install
            prometheus_install
            alertmanager_install
            blackbox-exporter_install
            prom_init
		;;
    base)
            install_check
            install_init
            consul_install
            prometheus_install
            prom_init
        ;;
    alertmanager)
            alertmanager_install
        ;;
    blackbox-exporter)
            blackbox-exporter_install
        ;;
    uninstall)
            prometheus_uninstall
        ;;
	help|*)
		echo $"Usage: $0 {all|base|alertmanager|blackbox-exporter|uninstall|help}"
	    ;;
    esac
}

main $1
