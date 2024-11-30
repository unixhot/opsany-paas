#!/bin/bash
#******************************************
# Author:       Jason Zhao
# Email:        zhaoshundong@opsany.com
# Organization: OpsAny https://www.opsany.com/
# Description:  OpsAny Elastic Stack Install Script
#******************************************

# Data/Time
CTIME=$(date "+%Y-%m-%d-%H-%M")

# Shell Envionment Variables
CDIR=$(pwd)
SHELL_NAME="elastic-install.sh"
SHELL_LOG="${SHELL_NAME}.log"

# Install Inspection
if [ ! -f ../install.config ];then
      echo "Please Change Directory to ${INSTALL_PATH}/install"
      exit
else
    source ../install.config
    source ./ee-install.config 
fi

# Shell Log Record
shell_log(){
    LOG_INFO=$1
    echo "----------------$CTIME ${SHELL_NAME} : ${LOG_INFO}----------------"
    echo "$CTIME ${SHELL_NAME} : ${LOG_INFO}" >> ${SHELL_LOG}
}

# Check Install requirement
install_init(){
    # Configuration file write to DB
    mkdir -p ${INSTALL_PATH}/conf
    /bin/cp -r ../conf/elastic ${INSTALL_PATH}/conf/
    mkdir -p ${INSTALL_PATH}/es-volume
    mkdir -p ${INSTALL_PATH}/uploads/monitor/heartbeat-monitors.d
    chmod -R 777 ${INSTALL_PATH}/es-volume
}

es_install(){
    # Elasticsearch
    shell_log "====Start Elasticsearch"
    docker run -d --restart=always --name opsany-elastic-elasticsearch \
    -e "discovery.type=single-node" \
    -e "ELASTIC_PASSWORD=${ES_PASSWORD}" \
    -e "xpack.license.self_generated.type=basic" \
    -e "xpack.security.enabled=true" \
    -e "bootstrap.memory_lock=true" \
    -e "ES_JAVA_OPTS=-Xms2048m -Xmx2048m" \
    -v /etc/localtime:/etc/localtime:ro \
    -v ${INSTALL_PATH}/es-volume:/usr/share/elasticsearch/data/ \
    -v ${INSTALL_PATH}/conf/elastic/elasticsearch.yml:/usr/share/elasticsearch/config/elasticsearch.yml \
    -p 9200:9200 -p 9300:9300 \
    ${PAAS_DOCKER_REG}/elasticsearch:8.11.1

    # useradd
    docker exec opsany-elastic-elasticsearch /usr/share/elasticsearch/bin/elasticsearch-users useradd \
    ${ES_USER} -p ${ES_PASSWORD} -r  superuser,kibana_system
}

heartbeat_install(){
    # Heartbeat
    sed -i "s/ES_SERVER_IP/${ES_SERVER_IP}/g" ${INSTALL_PATH}/conf/elastic/heartbeat.yml
    sed -i "s/ES_PASSWORD/${ES_PASSWORD}/g" ${INSTALL_PATH}/conf/elastic/heartbeat.yml
    
    shell_log "====Start Heartbeat===="
    docker run -d --restart=always --name opsany-elastic-heartbeat \
    -v ${INSTALL_PATH}/conf/elastic/heartbeat.yml:/usr/share/heartbeat/heartbeat.yml \
    -v ${INSTALL_PATH}/uploads/monitor/heartbeat-monitors.d:/usr/share/heartbeat/monitors.d \
    -v ${INSTALL_PATH}/logs:/var/log/heartbeat \
    -v /etc/localtime:/etc/localtime:ro \
    ${PAAS_DOCKER_REG}/heartbeat:8.11.1
}

kibana_install(){
    # kibana
    shell_log "====Start Kibana"
    # Modify configuration
    sed -i "s/ES_SERVER_IP/${ES_SERVER_IP}/g" ${INSTALL_PATH}/conf/elastic/kibana.yml
    sed -i "s/ELASTIC_PORT/${ELASTIC_PORT}/g" ${INSTALL_PATH}/conf/elastic/kibana.yml
    sed -i "s/ES_USER/${ES_USER}/g" ${INSTALL_PATH}/conf/elastic/kibana.yml
    sed -i "s/ES_PASSWORD/${ES_PASSWORD}/g" ${INSTALL_PATH}/conf/elastic/kibana.yml
    
    # Starter container
    docker run -d --restart=always --name opsany-elastic-kibana \
    -v /etc/localtime:/etc/localtime:ro \
    -v ${INSTALL_PATH}/conf/elastic/kibana.yml:/usr/share/kibana/config/kibana.yml \
    -p 5601:5601 \
    ${PAAS_DOCKER_REG}/kibana:8.11.1
}

apm_install(){
    # Apm server
    shell_log "====Start APM Server"
    # Modify configuration
    sed -i "s/ES_SERVER_IP/${ES_SERVER_IP}/g" ${INSTALL_PATH}/conf/elastic/apm-server.yml
    sed -i "s/ELASTIC_PORT/${ELASTIC_PORT}/g" ${INSTALL_PATH}/conf/elastic/apm-server.yml
    sed -i "s/ES_USER/${ES_USER}/g" ${INSTALL_PATH}/conf/elastic/apm-server.yml
    sed -i "s/ES_PASSWORD/${ES_PASSWORD}/g" ${INSTALL_PATH}/conf/elastic/apm-server.yml
    sed -i "s/APM_SECRET_TOKEN/${APM_SECRET_TOKEN}/g" ${INSTALL_PATH}/conf/elastic/apm-server.yml

    # Starter container
    docker run -d --restart=always --name opsany-elastic-apm-server \
    -v /etc/localtime:/etc/localtime:ro \
    -v ${INSTALL_PATH}/conf/elastic/apm-server.yml:/usr/share/apm-server/apm-server.yml \
    -p 8200:8200 \
    ${PAAS_DOCKER_REG}/apm-server:8.11.1
}

apm_enable(){
    # Enable APM
    #workbench
    sed -i "s/APM_SERVER_HOST/${APM_SERVER_HOST}/g" ${INSTALL_PATH}/conf/opsany-saas/workbench/workbench-prod.py
    sed -i "s/APM_SECRET_TOKEN/${APM_SECRET_TOKEN}/g" ${INSTALL_PATH}/conf/opsany-saas/workbench/workbench-prod.py
    sed -i '/ENABLED/s/false/true/g' ${INSTALL_PATH}/conf/opsany-saas/workbench/workbench-prod.py
    docker restart opsany-saas-ce-workbench
    #rbac
    sed -i "s/APM_SERVER_HOST/${APM_SERVER_HOST}/g" ${INSTALL_PATH}/conf/opsany-saas/rbac/rbac-prod.py
    sed -i "s/APM_SECRET_TOKEN/${APM_SECRET_TOKEN}/g" ${INSTALL_PATH}/conf/opsany-saas/rbac/rbac-prod.py
    sed -i '/ENABLED/s/false/true/g' ${INSTALL_PATH}/conf/opsany-saas/rbac/rbac-prod.py
    docker restart opsany-saas-ce-rbac
    #cmdb
    sed -i "s/APM_SERVER_HOST/${APM_SERVER_HOST}/g" ${INSTALL_PATH}/conf/opsany-saas/cmdb/cmdb-prod.py
    sed -i "s/APM_SECRET_TOKEN/${APM_SECRET_TOKEN}/g" ${INSTALL_PATH}/conf/opsany-saas/cmdb/cmdb-prod.py
    sed -i '/ENABLED/s/false/true/g' ${INSTALL_PATH}/conf/opsany-saas/cmdb/cmdb-prod.py
    docker restart opsany-saas-ce-cmdb
    #control
    sed -i "s/APM_SERVER_HOST/${APM_SERVER_HOST}/g" ${INSTALL_PATH}/conf/opsany-saas/control/control-prod.py
    sed -i "s/APM_SECRET_TOKEN/${APM_SECRET_TOKEN}/g" ${INSTALL_PATH}/conf/opsany-saas/control/control-prod.py
    sed -i '/ENABLED/s/false/true/g' ${INSTALL_PATH}/conf/opsany-saas/control/control-prod.py
    docker restart opsany-saas-ce-control
    #job
    sed -i "s/APM_SERVER_HOST/${APM_SERVER_HOST}/g" ${INSTALL_PATH}/conf/opsany-saas/job/job-prod.py
    sed -i "s/APM_SECRET_TOKEN/${APM_SECRET_TOKEN}/g" ${INSTALL_PATH}/conf/opsany-saas/job/job-prod.py
    sed -i '/ENABLED/s/false/true/g' ${INSTALL_PATH}/conf/opsany-saas/job/job-prod.py
    docker restart opsany-saas-ce-job
    #monitor
    sed -i "s/APM_SERVER_HOST/${APM_SERVER_HOST}/g" ${INSTALL_PATH}/conf/opsany-saas/monitor/monitor-prod.py
    sed -i "s/APM_SECRET_TOKEN/${APM_SECRET_TOKEN}/g" ${INSTALL_PATH}/conf/opsany-saas/monitor/monitor-prod.py
    sed -i '/ENABLED/s/false/true/g' ${INSTALL_PATH}/conf/opsany-saas/monitor/monitor-prod.py
    docker restart opsany-saas-ce-monitor
    #bastion
    sed -i "s/APM_SERVER_HOST/${APM_SERVER_HOST}/g" ${INSTALL_PATH}/conf/opsany-saas/bastion/bastion-prod.py
    sed -i "s/APM_SECRET_TOKEN/${APM_SECRET_TOKEN}/g" ${INSTALL_PATH}/conf/opsany-saas/bastion/bastion-prod.py
    sed -i '/ENABLED/s/false/true/g' ${INSTALL_PATH}/conf/opsany-saas/bastion/bastion-prod.py
    docker restart opsany-saas-ce-bastion
    #cmp
    sed -i "s/APM_SERVER_HOST/${APM_SERVER_HOST}/g" ${INSTALL_PATH}/conf/opsany-saas/cmp/cmp-prod.py
    sed -i "s/APM_SECRET_TOKEN/${APM_SECRET_TOKEN}/g" ${INSTALL_PATH}/conf/opsany-saas/cmp/cmp-prod.py
    sed -i '/ENABLED/s/false/true/g' ${INSTALL_PATH}/conf/opsany-saas/cmp/cmp-prod.py
    docker restart opsany-saas-ce-cmp
    #devops
    sed -i "s/APM_SERVER_HOST/${APM_SERVER_HOST}/g" ${INSTALL_PATH}/conf/opsany-saas/devops/devops-prod.py
    sed -i "s/APM_SECRET_TOKEN/${APM_SECRET_TOKEN}/g" ${INSTALL_PATH}/conf/opsany-saas/devops/devops-prod.py
    sed -i '/ENABLED/s/false/true/g' ${INSTALL_PATH}/conf/opsany-saas/devops/devops-prod.py
    docker restart opsany-saas-ce-devops
    #event
    sed -i "s/APM_SERVER_HOST/${APM_SERVER_HOST}/g" ${INSTALL_PATH}/conf/opsany-saas/event/event-prod.py
    sed -i "s/APM_SECRET_TOKEN/${APM_SECRET_TOKEN}/g" ${INSTALL_PATH}/conf/opsany-saas/event/event-prod.py
    sed -i '/ENABLED/s/false/true/g' ${INSTALL_PATH}/conf/opsany-saas/event/event-prod.py
    docker restart opsany-saas-ee-event
    #prom
    sed -i "s/APM_SERVER_HOST/${APM_SERVER_HOST}/g" ${INSTALL_PATH}/conf/opsany-saas/prom/prom-prod.py
    sed -i "s/APM_SECRET_TOKEN/${APM_SECRET_TOKEN}/g" ${INSTALL_PATH}/conf/opsany-saas/prom/prom-prod.py
    sed -i '/ENABLED/s/false/true/g' ${INSTALL_PATH}/conf/opsany-saas/prom/prom-prod.py
    docker restart opsany-saas-ee-prom
    #k8s
    sed -i "s/APM_SERVER_HOST/${APM_SERVER_HOST}/g" ${INSTALL_PATH}/conf/opsany-saas/k8s/k8s-prod.py
    sed -i "s/APM_SECRET_TOKEN/${APM_SECRET_TOKEN}/g" ${INSTALL_PATH}/conf/opsany-saas/k8s/k8s-prod.py
    sed -i '/ENABLED/s/false/true/g' ${INSTALL_PATH}/conf/opsany-saas/k8s/k8s-prod.py
    docker restart opsany-saas-ee-k8s
    #auto
    sed -i "s/APM_SERVER_HOST/${APM_SERVER_HOST}/g" ${INSTALL_PATH}/conf/opsany-saas/auto/auto-prod.py
    sed -i "s/APM_SECRET_TOKEN/${APM_SECRET_TOKEN}/g" ${INSTALL_PATH}/conf/opsany-saas/auto/auto-prod.py
    sed -i '/ENABLED/s/false/true/g' ${INSTALL_PATH}/conf/opsany-saas/auto/auto-prod.py
    docker restart opsany-saas-ee-auto
    #kbase
    sed -i "s/APM_SERVER_HOST/${APM_SERVER_HOST}/g" ${INSTALL_PATH}/conf/opsany-saas/kbase/kbase-prod.py
    sed -i "s/APM_SECRET_TOKEN/${APM_SECRET_TOKEN}/g" ${INSTALL_PATH}/conf/opsany-saas/kbase/kbase-prod.py
    sed -i '/ENABLED/s/false/true/g' ${INSTALL_PATH}/conf/opsany-saas/kbase/kbase-prod.py
    docker restart opsany-saas-ee-kbase
    #log
    sed -i "s/APM_SERVER_HOST/${APM_SERVER_HOST}/g" ${INSTALL_PATH}/conf/opsany-saas/log/log-prod.py
    sed -i "s/APM_SECRET_TOKEN/${APM_SECRET_TOKEN}/g" ${INSTALL_PATH}/conf/opsany-saas/log/log-prod.py
    sed -i '/ENABLED/s/false/true/g' ${INSTALL_PATH}/conf/opsany-saas/log/log-prod.py
    docker restart opsany-saas-ee-log
    #pipeline
    sed -i "s/APM_SERVER_HOST/${APM_SERVER_HOST}/g" ${INSTALL_PATH}/conf/opsany-saas/pipeline/pipeline-prod.py
    sed -i "s/APM_SECRET_TOKEN/${APM_SECRET_TOKEN}/g" ${INSTALL_PATH}/conf/opsany-saas/pipeline/pipeline-prod.py
    sed -i '/ENABLED/s/false/true/g' ${INSTALL_PATH}/conf/opsany-saas/pipeline/pipeline-prod.py
    docker restart opsany-saas-ce-pipeline
    #deploy
    sed -i "s/APM_SERVER_HOST/${APM_SERVER_HOST}/g" ${INSTALL_PATH}/conf/opsany-saas/deploy/deploy-prod.py
    sed -i "s/APM_SECRET_TOKEN/${APM_SECRET_TOKEN}/g" ${INSTALL_PATH}/conf/opsany-saas/deploy/deploy-prod.py
    sed -i '/ENABLED/s/false/true/g' ${INSTALL_PATH}/conf/opsany-saas/deploy/deploy-prod.py
    docker restart opsany-saas-ce-deploy
    #apm
    sed -i "s/APM_SERVER_HOST/${APM_SERVER_HOST}/g" ${INSTALL_PATH}/conf/opsany-saas/apm/apm-prod.py
    sed -i "s/APM_SECRET_TOKEN/${APM_SECRET_TOKEN}/g" ${INSTALL_PATH}/conf/opsany-saas/apm/apm-prod.py
    sed -i '/ENABLED/s/false/true/g' ${INSTALL_PATH}/conf/opsany-saas/apm/apm-prod.py
    docker restart opsany-saas-ee-apm
    #repo
    sed -i "s/APM_SERVER_HOST/${APM_SERVER_HOST}/g" ${INSTALL_PATH}/conf/opsany-saas/repo/repo-prod.py
    sed -i "s/APM_SECRET_TOKEN/${APM_SECRET_TOKEN}/g" ${INSTALL_PATH}/conf/opsany-saas/repo/repo-prod.py
    sed -i '/ENABLED/s/false/true/g' ${INSTALL_PATH}/conf/opsany-saas/repo/repo-prod.py
    docker restart opsany-saas-ce-repo
}


elastic_uninstall(){
    docker stop opsany-elastic-elasticsearch && docker rm opsany-elastic-elasticsearch
    docker stop opsany-elastic-heartbeat && docker rm opsany-elastic-heartbeat
    docker stop opsany-elastic-kibana && docker rm opsany-elastic-kibana
    docker stop opsany-elastic-apm-server && docker rm opsany-elastic-apm-server
    cd ${INSTALL_PATH}
    rm -rf es-volume/*
}

# Main
main(){
    case "$1" in
    all)
        install_init
        es_install
        kibana_install
        heartbeat_install
        apm_install
        #apm_enable
        ;;
    apm)
        apm_install
        apm_enable
        ;;
    es)
        es_install
        ;;
    kibana)
        kibana_install
        ;;
    heartbeat)
        heartbeat_install
        ;;
    uninstall)
        elastic_uninstall
        ;;
    enable)
        apm_enable
        ;;
	help|*)
		echo $"Usage: $0 {all|enable|es|kibana|heartbeat|apm|help|uninstall}"
	    ;;
esac
}

main $1
