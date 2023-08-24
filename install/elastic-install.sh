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
    mkdir -p ${INSTALL_PATH}/{uploads,conf,logs,prometheus-volume/conf,prometheus-volume/data,consul-volume/data,consul-volume/config,uploads/prometheus-config/rules}
    cd $CDIR
    /bin/cp -r ./conf/prometheus/* ${INSTALL_PATH}/prometheus-volume/conf/
    /bin/cp conf/consul.hcl ${INSTALL_PATH}/consul-volume/config/
    pip3 install requests==2.25.1 grafana-api==1.0.3 mysql-connector==2.2.9 SQLAlchemy==1.4.22 bcrypt==3.2.2 \
             -i http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com
    shell_log "End: Install Init"
}

es_install(){
    #Elasticsearch
    shell_log "======Start Elasticsearch======"
    docker run -d --restart=always --name opsany-base-elasticsearch \
    -e "discovery.type=single-node" \
    -e "ELASTIC_PASSWORD=${ES_PASSWORD}" \
    -e "xpack.license.self_generated.type=basic" \
    -e "xpack.security.enabled=true" \
    -e "xpack.security.enrollment.enabled=true" \
    -e "bootstrap.memory_lock=true" \
    -e "ES_JAVA_OPTS=-Xms1024m -Xmx1024m" \
    -v /etc/localtime:/etc/localtime:ro \
    -v ${INSTALL_PATH}/es-volume:/usr/share/elasticsearch/data/ \
    -p 9200:9200 -p 9300:9300 \
    docker.elastic.co/elasticsearch/elasticsearch:8.9.0
}


kibana_install(){
    #Kibana
    shell_log "======Start Kibana======"
    docker run -d --restart=always --name opsany-base-kibana \
    -e "ELASTICSEARCH_HOSTS: '["http://172.16.16.84:9200"]'" \
    -v /etc/localtime:/etc/localtime:ro \
    -p 5601:5601 \
    docker.elastic.co/kibana/kibana:8.9.0
}
 
heartbeat_install(){
    #heartbeat
    shell_log "====Start Heartbeat===="
    docker run -d --restart=always --name opsany-heartbeat \
    -v ${INSTALL_PATH}/conf/heartbeat.yml:/etc/heartbeat/heartbeat.yml \
    -v ${INSTALL_PATH}/uploads/monitor/heartbeat-monitors.d:/etc/heartbeat/monitors.d \
    -v ${INSTALL_PATH}/logs:/var/log/heartbeat \
    -v /etc/localtime:/etc/localtime:ro \
    ${PAAS_DOCKER_REG}/opsany-heartbeat:7.13.2
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
        uninstall)
            prometheus_uninstall
                ;;
	help|*)
		echo $"Usage: $0 {install|uninstall|help}"
	        ;;
    esac
}

main $1


