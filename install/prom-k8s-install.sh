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
if [ ! -f ./install-k8s.config ];then
      shell_error_log "Please Copy install-k8s.config and Change: cp install-k8s.config.example install-k8s.config"
      exit
else
    grep '^[A-Z]' install-k8s.config > install.env
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
    mkdir -p /data/k8s-nfs/{prometheus-volume/data,consul-volume/data,opsany-uploads/prometheus-config/rules}
    mkdir -p ${INSTALL_PATH}/{uploads,conf,logs,prometheus-volume/conf,prometheus-volume/data,consul-volume/data,consul-volume/config,uploads/prometheus-config/rules}
    /bin/cp -r ../kubernetes ${INSTALL_PATH}/
    cd $CDIR
    /bin/cp -r ./conf/prometheus/* ${INSTALL_PATH}/kubernetes/helm/opsany-base/prometheus/
    /bin/cp conf/consul.hcl ${INSTALL_PATH}/kubernetes/helm/opsany-base/consul/
    /bin/cp ../kubernetes/helm/opsany-base/prometheus ${INSTALL_PATH}/kubernetes/helm/opsany-base/
    /bin/cp ../kubernetes/helm/opsany-base/consul ${INSTALL_PATH}/kubernetes/helm/opsany-base/
    pip3 install requests==2.25.1 grafana-api==1.0.3 mysql-connector==2.2.9 SQLAlchemy==1.4.22 bcrypt==3.2.2 \
             -i http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com
    shell_log "End: Install Init"
}

consul_install(){
    shell_log "Start: Consul Install..."
    CONSUL_TOKEN=$(uuid -v4)
    echo $CONSUL_TOKEN > ${INSTALL_PATH}/conf/.consul_token
    sed -i "s#PROM_CONSUL_SERVER#$CONSUL_SERVER_IP#g" ${INSTALL_PATH}/kubernetes/helm/opsany-base/prometheus/prometheus.yml
    sed -i "s#CONSUL_TOKEN#$CONSUL_TOKEN#g" ${INSTALL_PATH}/kubernetes/helm/opsany-base/prometheus/prometheus.yml
    sed -i "s#CONSUL_TOKEN#$CONSUL_TOKEN#g" ${INSTALL_PATH}/kubernetes/helm/opsany-base/consul/consul.hcl
    shell_log "======Consul Token: ${CONSUL_TOKEN}======"
}

prometheus_install(){
    # Prometheus Server Basic Auth
    PROM_SERVER_HASH=$(python3 ./prom-pass.py $PROM_SERVER_PASSWD)
    sed -i "s#PROM_SERVER_HASH#$PROM_SERVER_HASH#g" ${INSTALL_PATH}/kubernetes/helm/opsany-base/prometheus/web.yml
    sed -i "s#LOCAL_IP#$PROXY_LOCAL_IP#g" ${INSTALL_PATH}/kubernetes/helm/opsany-base/prometheus/prometheus.yml
    sed -i "s#PROM_SERVER_PASSWD#$PROM_SERVER_PASSWD#g" ${INSTALL_PATH}/kubernetes/helm/opsany-base/prometheus/prometheus.yml

    # Prometheus Release Date: 2022-04-21 https://hub.docker.com/u/prom
    # Prometheus Node Exporter Release Date: 2021-12-01 https://hub.docker.com/u/prom
    #shell_log "======Start Prometheus Node_Exporter======"
    #docker run -d --restart=always --name opsany-prometheus-node_exporter \
    #-p 9100:9100 \
    #-v /etc/localtime:/etc/localtime:ro \
    #${PAAS_DOCKER_REG}/node-exporter:v1.3.1
}


# Main
main(){
    case "$1" in
	install)
            install_check
            install_init
            consul_install
            prometheus_install
		;;
	help|*)
		echo $"Usage: $0 {install|help}"
	        ;;
    esac
}

main $1
