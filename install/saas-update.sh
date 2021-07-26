#!/bin/bash
#******************************************
# Author:       Jason Zhao
# Email:        zhaoshundong@opsany.com
# Organization: OpsAny https://www.opsany.com/
# Description:  OpsAny SAAS Install Script
#******************************************

# Data/Time
CTIME=$(date "+%Y-%m-%d-%H-%M")

# Shell Envionment Variables
CDIR=$(pwd)
SHELL_NAME="saas-install.sh"
SHELL_LOG="${SHELL_NAME}.log"
ADMIN_PASSWORD=admin

# Import Config 
source ./install.config

# Shell Log Record
shell_log(){
    LOG_INFO=$1
    echo "----------------$CTIME ${SHELL_NAME} : ${LOG_INFO}----------------"
    echo "$CTIME ${SHELL_NAME} : ${LOG_INFO}" >> ${SHELL_LOG}
}

rbac_update(){
    #rbac
    cd $CDIR
    cd ../../opsany-saas/
    tar zxf rbac-www.opsany.com-${SAAS_VERSION}.tar.gz
    sed -i "s/www.opsany.com/${DOMAIN_NAME}/g" ./rbac/src/config/__init__.py
    sed -i "s/192.168.56.11/${MYSQL_SERVER_IP}/g" ./rbac/src/config/prod.py
    sed -i "s/OpsAny@2020/${MYSQL_OPSANY_RBAC_PASSWORD}/g" ./rbac/src/config/prod.py
    tar czf rbac-${DOMAIN_NAME}-${SAAS_VERSION}.tar.gz rbac && mv -f rbac-${DOMAIN_NAME}-${SAAS_VERSION}.tar.gz ../opsany-paas/saas/
    rm -rf rbac
    cd $CDIR
    python3 ../saas/deploy.py --domain $DOMAIN_NAME --username admin --password $ADMIN_PASSWORD --file_name ../saas/rbac-${DOMAIN_NAME}-${SAAS_VERSION}.tar.gz
}

workbench_update(){
    #workbench
    cd $CDIR
    cd ../../opsany-saas/
    tar zxf workbench-www.opsany.com-${SAAS_VERSION}.tar.gz
    sed -i "s/www.opsany.com/${DOMAIN_NAME}/g" ./workbench/src/config/__init__.py
    sed -i "s/192.168.56.11/${MYSQL_SERVER_IP}/g" ./workbench/src/config/prod.py
    sed -i "s/OpsAny@2020/${MYSQL_OPSANY_RBAC_PASSWORD}/g" ./workbench/src/config/prod.py
    tar czf workbench-${DOMAIN_NAME}-${SAAS_VERSION}.tar.gz workbench && mv -f workbench-${DOMAIN_NAME}-${SAAS_VERSION}.tar.gz ../opsany-paas/saas/
    rm -rf workbench
    cd $CDIR
    python3 ../saas/deploy.py --domain $DOMAIN_NAME --username admin --password $ADMIN_PASSWORD --file_name ../saas/workbench-${DOMAIN_NAME}-${SAAS_VERSION}.tar.gz
}
    
cmdb_update(){
    #cmdb
    cd $CDIR
    cd ../../opsany-saas/
    tar zxf cmdb-www.opsany.com-${SAAS_VERSION}.tar.gz
    sed -i "s/www.opsany.com/${DOMAIN_NAME}/g" ./cmdb/src/config/__init__.py
    sed -i "s/192.168.56.11/${MYSQL_SERVER_IP}/g" ./cmdb/src/config/prod.py
    sed -i "s/OpsAny@2020/${MYSQL_OPSANY_RBAC_PASSWORD}/g" ./cmdb/src/config/prod.py
    tar czf cmdb-${DOMAIN_NAME}-${SAAS_VERSION}.tar.gz cmdb && mv -f cmdb-${DOMAIN_NAME}-${SAAS_VERSION}.tar.gz ../opsany-paas/saas/
    rm -rf cmdb
    cd $CDIR
    python3 ../saas/deploy.py --domain $DOMAIN_NAME --username admin --password $ADMIN_PASSWORD --file_name ../saas/cmdb-${DOMAIN_NAME}-${SAAS_VERSION}.tar.gz
}

control_update(){
    #control
    cd $CDIR
    cd ../../opsany-saas/
    tar zxf control-www.opsany.com-${SAAS_VERSION}.tar.gz
    sed -i "s/www.opsany.com/${DOMAIN_NAME}/g" ./control/src/config/__init__.py
    sed -i "s/192.168.56.11/${MYSQL_SERVER_IP}/g" ./control/src/config/prod.py
    sed -i "s/OpsAny@2020/${MYSQL_OPSANY_RBAC_PASSWORD}/g" ./control/src/config/prod.py
    tar czf control-${DOMAIN_NAME}-${SAAS_VERSION}.tar.gz control && mv -f control-${DOMAIN_NAME}-${SAAS_VERSION}.tar.gz ../opsany-paas/saas/
    rm -rf control
    cd $CDIR
    python3 ../saas/deploy.py --domain $DOMAIN_NAME --username admin --password $ADMIN_PASSWORD --file_name ../saas/control-${DOMAIN_NAME}-${SAAS_VERSION}.tar.gz
}

job_update(){
    #job
    cd $CDIR
    cd ../../opsany-saas/
    tar zxf job-www.opsany.com-${SAAS_VERSION}.tar.gz
    sed -i "s/www.opsany.com/${DOMAIN_NAME}/g" ./job/src/config/__init__.py
    sed -i "s/192.168.56.11/${MYSQL_SERVER_IP}/g" ./job/src/config/prod.py
    sed -i "s/OpsAny@2020/${MYSQL_OPSANY_RBAC_PASSWORD}/g" ./job/src/config/prod.py
    tar czf job-${DOMAIN_NAME}-${SAAS_VERSION}.tar.gz job && mv -f job-${DOMAIN_NAME}-${SAAS_VERSION}.tar.gz ../opsany-paas/saas/
    rm -rf job
    cd $CDIR
    python3 ../saas/deploy.py --domain $DOMAIN_NAME --username admin --password $ADMIN_PASSWORD --file_name ../saas/job-${DOMAIN_NAME}-${SAAS_VERSION}.tar.gz
}

monitor_update(){
    #monitor
    cd $CDIR
    cd ../../opsany-saas/
    tar zxf monitor-www.opsany.com-${SAAS_VERSION}.tar.gz
    sed -i "s/www.opsany.com/${DOMAIN_NAME}/g" ./monitor/src/config/__init__.py
    sed -i "s/192.168.56.11/${MYSQL_SERVER_IP}/g" ./monitor/src/config/prod.py
    sed -i "s/OpsAny@2020/${MYSQL_OPSANY_RBAC_PASSWORD}/g" ./monitor/src/config/prod.py
    tar czf monitor-${DOMAIN_NAME}-${SAAS_VERSION}.tar.gz monitor && mv -f monitor-${DOMAIN_NAME}-${SAAS_VERSION}.tar.gz ../opsany-paas/saas/
    rm -rf monitor
    cd $CDIR
    python3 ../saas/deploy.py --domain $DOMAIN_NAME --username admin --password $ADMIN_PASSWORD --file_name ../saas/monitor-${DOMAIN_NAME}-${SAAS_VERSION}.tar.gz
}

cmp_update(){
    #cmp
    cd $CDIR
    cd ../../opsany-saas/
    tar zxf cmp-www.opsany.com-${SAAS_VERSION}.tar.gz
    sed -i "s/www.opsany.com/${DOMAIN_NAME}/g" ./cmp/src/config/__init__.py
    sed -i "s/192.168.56.11/${MYSQL_SERVER_IP}/g" ./cmp/src/config/prod.py
    sed -i "s/OpsAny@2020/${MYSQL_OPSANY_RBAC_PASSWORD}/g" ./cmp/src/config/prod.py
    tar czf cmp-${DOMAIN_NAME}-${SAAS_VERSION}.tar.gz cmp && mv -f cmp-${DOMAIN_NAME}-${SAAS_VERSION}.tar.gz ../opsany-paas/saas/
    rm -rf cmp
    cd $CDIR
    python3 ../saas/deploy.py --domain $DOMAIN_NAME --username admin --password $ADMIN_PASSWORD --file_name ../saas/cmp-${DOMAIN_NAME}-${SAAS_VERSION}.tar.gz
}

devops_update(){
    #devops
    cd $CDIR
    cd ../../opsany-saas/
    tar zxf devops-www.opsany.com-${SAAS_VERSION}.tar.gz
    sed -i "s/www.opsany.com/${DOMAIN_NAME}/g" ./devops/src/config/__init__.py
    sed -i "s/192.168.56.11/${MYSQL_SERVER_IP}/g" ./devops/src/config/prod.py
    sed -i "s/OpsAny@2020/${MYSQL_OPSANY_RBAC_PASSWORD}/g" ./devops/src/config/prod.py
    tar czf devops-${DOMAIN_NAME}-${SAAS_VERSION}.tar.gz devops && mv -f devops-${DOMAIN_NAME}-${SAAS_VERSION}.tar.gz ../opsany-paas/saas/
    rm -rf devops
    cd $CDIR
    python3 ../saas/deploy.py --domain $DOMAIN_NAME --username admin --password $ADMIN_PASSWORD --file_name ../saas/devops-${DOMAIN_NAME}-${SAAS_VERSION}.tar.gz
}

# Main
main(){
    case "$1" in
	rbac)
		rbac_update
		;;
	workbench)
		workbench_update
		;;
	cmdb)
		cmdb_update
		;;
	control)
		control_update
		;;
	job)
		job_update
		;;
	monitor)
		monitor_update
		;;
	cmp)
		cmp_update
		;;
	devops)
		devops_update
		;;
	all)
		rbac_update
		workbench_update
		cmdb_update
		control_update
		job_update
		monitor_update
		cmp_update
		devops_update
		;;
	help|*)
		echo $"Usage: $0 {all|rbac|workbench|cmdb|control|job|monitor|cmp|devops|help}"
	        ;;
esac
}

main $1
