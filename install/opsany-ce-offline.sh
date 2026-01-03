#!/bin/bash
#******************************************
# Author:       Jason Zhao
# Email:        zhaoshundong@opsany.com
# Organization: OpsAny https://www.opsany.com/
# Description:  OpsAny SAAS Community Edition Offline Script
#******************************************

# Data/Time Variables
CTIME=$(date "+%Y-%m-%d-%H-%M")
SAAS_VERSION="2.3.1"
mkdir -p /opt/opsany-v${SAAS_VERSION}-x86_64/images

base_save(){
    # 基础镜像
	docker pull registry.cn-beijing.aliyuncs.com/opsany/mysql:8.0.30
	docker pull registry.cn-beijing.aliyuncs.com/opsany/zabbix-web-nginx-mysql:7.0.3-ubuntu
	docker pull registry.cn-beijing.aliyuncs.com/opsany/zabbix-server-mysql:7.0.3-ubuntu
	docker pull registry.cn-beijing.aliyuncs.com/opsany/zabbix-agent2:7.0.3-ubuntu
	docker pull registry.cn-beijing.aliyuncs.com/opsany/jenkins:2.452.2-lts
	docker pull registry.cn-beijing.aliyuncs.com/opsany/nexus3:3.37.0
	docker pull registry.cn-beijing.aliyuncs.com/opsany/redis:6.2.19-alpine
	docker pull registry.cn-beijing.aliyuncs.com/opsany/mongo:4.4.1-bionic
	docker pull  registry.cn-beijing.aliyuncs.com/opsany/openresty:1.17.8.2-alpine
	docker pull registry.cn-beijing.aliyuncs.com/opsany/guacd:1.2.0
	docker pull registry.cn-beijing.aliyuncs.com/opsany/opsany-grafana:9.0.3
	cd /opt/opsany-v${SAAS_VERSION}-x86_64/images
	docker save -o mysql-8.0.30-x86.tar registry.cn-beijing.aliyuncs.com/opsany/mysql:8.0.30
	docker save -o zabbix-web-nginx-mysql.tar registry.cn-beijing.aliyuncs.com/opsany/zabbix-web-nginx-mysql:7.0.3-ubuntu
	docker save -o zabbix-server-mysql.tar registry.cn-beijing.aliyuncs.com/opsany/zabbix-server-mysql:7.0.3-ubuntu
	docker save -o redis-6.2.19-x86.tar registry.cn-beijing.aliyuncs.com/opsany/redis:6.2.19-alpine
	docker save -o mongo-4.4.1-x86.tar registry.cn-beijing.aliyuncs.com/opsany/mongo:4.4.1-bionic
	docker save -o openresty-1.17.8.2-x86.tar  registry.cn-beijing.aliyuncs.com/opsany/openresty:1.17.8.2-alpine
	docker save -o guacd-1.2.0-x86.tar registry.cn-beijing.aliyuncs.com/opsany/guacd:1.2.0
	docker save -o grafana-9.0.3-x86.tar registry.cn-beijing.aliyuncs.com/opsany/opsany-grafana:9.0.3
	docker save -o zabbix-web-nginx-mysql-7.0.3-ubuntu-x86.tar registry.cn-beijing.aliyuncs.com/opsany/zabbix-web-nginx-mysql:7.0.3-ubuntu
	docker save -o zabbix-server-mysql-7.0.3-ubuntu-x86.tar registry.cn-beijing.aliyuncs.com/opsany/zabbix-server-mysql:7.0.3-ubuntu
	docker save -o zabbix-agent2-7.0.3-ubuntu-x86.tar registry.cn-beijing.aliyuncs.com/opsany/zabbix-agent2:7.0.3-ubuntu
	docker save -o jenkins-2.452.2-lts-x86.tar registry.cn-beijing.aliyuncs.com/opsany/jenkins:2.452.2-lts
	docker save -o nexus3-3.37.0-x86.tar registry.cn-beijing.aliyuncs.com/opsany/nexus3:3.37.0
}

paas_save(){
	# 导出PaaS镜像
	docker pull registry.cn-beijing.aliyuncs.com/opsany/opsany-paas-proxy:2.3.1
	docker pull registry.cn-beijing.aliyuncs.com/opsany/opsany-paas-websocket:4.0.0
	docker pull registry.cn-beijing.aliyuncs.com/opsany/opsany-paas-appengine:4.0.0
	docker pull registry.cn-beijing.aliyuncs.com/opsany/opsany-paas-login:4.0.3
	docker pull registry.cn-beijing.aliyuncs.com/opsany/opsany-paas-esb:4.0.0
	docker pull registry.cn-beijing.aliyuncs.com/opsany/opsany-paas-paas:4.0.0
	cd /opt/opsany-v${SAAS_VERSION}-x86_64/images
	docker save -o opsany-paas-proxy-2.3.1-x86.tar registry.cn-beijing.aliyuncs.com/opsany/opsany-paas-proxy:2.3.1
	docker save -o opsany-paas-websocket-4.0.0-x86.tar registry.cn-beijing.aliyuncs.com/opsany/opsany-paas-websocket:4.0.0
	docker save -o opsany-paas-appengine-4.0.0-x86.tar registry.cn-beijing.aliyuncs.com/opsany/opsany-paas-appengine:4.0.0
	docker save -o opsany-paas-login-4.0.3-x86.tar registry.cn-beijing.aliyuncs.com/opsany/opsany-paas-login:4.0.3
	docker save -o opsany-paas-esb-4.0.0-x86.tar registry.cn-beijing.aliyuncs.com/opsany/opsany-paas-esb:4.0.0
	docker save -o opsany-paas-paas-4.0.0-x86.tar registry.cn-beijing.aliyuncs.com/opsany/opsany-paas-paas:4.0.0
}

ce_save(){
    # 导出社区版SaaS镜像
	docker pull registry.cn-beijing.aliyuncs.com/opsany/opsany-saas-ce-llmops:${SAAS_VERSION}
	docker pull registry.cn-beijing.aliyuncs.com/opsany/opsany-saas-ce-rbac:${SAAS_VERSION}
	docker pull registry.cn-beijing.aliyuncs.com/opsany/opsany-saas-ce-workbench:${SAAS_VERSION}
	docker pull registry.cn-beijing.aliyuncs.com/opsany/opsany-saas-ce-cmdb:${SAAS_VERSION}
	docker pull registry.cn-beijing.aliyuncs.com/opsany/opsany-saas-ce-control:${SAAS_VERSION}
	docker pull registry.cn-beijing.aliyuncs.com/opsany/opsany-saas-ce-job:${SAAS_VERSION}
	docker pull registry.cn-beijing.aliyuncs.com/opsany/opsany-saas-ce-monitor:${SAAS_VERSION}
	docker pull registry.cn-beijing.aliyuncs.com/opsany/opsany-saas-ce-cmp:${SAAS_VERSION}
	docker pull registry.cn-beijing.aliyuncs.com/opsany/opsany-saas-ce-bastion:${SAAS_VERSION}
	docker pull registry.cn-beijing.aliyuncs.com/opsany/opsany-saas-ce-devops:${SAAS_VERSION}
	docker pull registry.cn-beijing.aliyuncs.com/opsany/opsany-saas-ce-pipeline:${SAAS_VERSION}
	docker pull registry.cn-beijing.aliyuncs.com/opsany/opsany-saas-ce-deploy:${SAAS_VERSION}
	docker pull registry.cn-beijing.aliyuncs.com/opsany/opsany-saas-ce-repo:${SAAS_VERSION}
	cd /opt/opsany-v${SAAS_VERSION}-x86_64/images
	docker save -o opsany-saas-llmops-${SAAS_VERSION}.tar registry.cn-beijing.aliyuncs.com/opsany/opsany-saas-ce-llmops:${SAAS_VERSION}
	docker save -o opsany-saas-rbac-${SAAS_VERSION}.tar registry.cn-beijing.aliyuncs.com/opsany/opsany-saas-ce-rbac:${SAAS_VERSION}
	docker save -o opsany-saas-workbench-${SAAS_VERSION}.tar registry.cn-beijing.aliyuncs.com/opsany/opsany-saas-ce-workbench:${SAAS_VERSION}
	docker save -o opsany-saas-cmdb-${SAAS_VERSION}.tar registry.cn-beijing.aliyuncs.com/opsany/opsany-saas-ce-cmdb:${SAAS_VERSION}
	docker save -o opsany-saas-control-${SAAS_VERSION}.tar registry.cn-beijing.aliyuncs.com/opsany/opsany-saas-ce-control:${SAAS_VERSION}
	docker save -o opsany-saas-job-${SAAS_VERSION}.tar registry.cn-beijing.aliyuncs.com/opsany/opsany-saas-ce-job:${SAAS_VERSION}
	docker save -o opsany-saas-monitor-${SAAS_VERSION}.tar registry.cn-beijing.aliyuncs.com/opsany/opsany-saas-ce-monitor:${SAAS_VERSION}
	docker save -o opsany-saas-cmp-${SAAS_VERSION}.tar registry.cn-beijing.aliyuncs.com/opsany/opsany-saas-ce-cmp:${SAAS_VERSION}
	docker save -o opsany-saas-bastion-${SAAS_VERSION}.tar registry.cn-beijing.aliyuncs.com/opsany/opsany-saas-ce-bastion:${SAAS_VERSION}
	docker save -o opsany-saas-devops-${SAAS_VERSION}.tar registry.cn-beijing.aliyuncs.com/opsany/opsany-saas-ce-devops:${SAAS_VERSION}
	docker save -o opsany-saas-pipeline-${SAAS_VERSION}.tar registry.cn-beijing.aliyuncs.com/opsany/opsany-saas-ce-pipeline:${SAAS_VERSION}
	docker save -o opsany-saas-deploy-${SAAS_VERSION}.tar registry.cn-beijing.aliyuncs.com/opsany/opsany-saas-ce-deploy:${SAAS_VERSION}
	docker save -o opsany-saas-repo-${SAAS_VERSION}.tar registry.cn-beijing.aliyuncs.com/opsany/opsany-saas-ce-repo:${SAAS_VERSION}
	docker save -o opsany-saas-code-${SAAS_VERSION}.tar registry.cn-beijing.aliyuncs.com/opsany/opsany-saas-ce-code:${SAAS_VERSION}
}

# Main
main(){
    case "$1" in
    ce)
        ce_save
        ;;
    paas)
        paas_save
        ;;
    base)
        base_save
        ;;
    all)
        base_save
        ce_save
        paas_save
        ;;
	help|*)
	    echo $"Usage: $0 {base|paas|ce|all|help}"
	    ;;
    esac
}

main $1 
