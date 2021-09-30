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
grep '^[A-Z]' install.config > install.env
source ./install.env && rm -f install.env

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
    /bin/cp rbac-opsany-*.tar.gz ../opsany-paas/saas/
    cd $CDIR
    python3 ../saas/deploy.py --domain $DOMAIN_NAME --username admin --password $ADMIN_PASSWORD --file_name ../saas/rbac-opsany-*.tar.gz
}

workbench_update(){
    #workbench
    cd $CDIR
    cd ../../opsany-saas/
    /bin/cp workbench-opsany-*.tar.gz ../opsany-paas/saas/
    cd $CDIR
    python3 ../saas/deploy.py --domain $DOMAIN_NAME --username admin --password $ADMIN_PASSWORD --file_name ../saas/workbench-opsany-*.tar.gz
}
    
cmdb_update(){
    #cmdb
    cd $CDIR
    cd ../../opsany-saas/
    /bin/cp cmdb-opsany-*.tar.gz ../opsany-paas/saas/
    cd $CDIR
    python3 ../saas/deploy.py --domain $DOMAIN_NAME --username admin --password $ADMIN_PASSWORD --file_name ../saas/cmdb-opsany-*.tar.gz
}

control_update(){
    #control
    cd $CDIR
    cd ../../opsany-saas/
    /bin/cp control-opsany-*.tar.gz ../opsany-paas/saas/
    cd $CDIR
    python3 ../saas/deploy.py --domain $DOMAIN_NAME --username admin --password $ADMIN_PASSWORD --file_name ../saas/control-opsany-*.tar.gz
}

job_update(){
    #job
    cd $CDIR
    cd ../../opsany-saas/
    /bin/cp mv -f job-opsany-*.tar.gz ../opsany-paas/saas/
    cd $CDIR
    python3 ../saas/deploy.py --domain $DOMAIN_NAME --username admin --password $ADMIN_PASSWORD --file_name ../saas/job-opsany-*.tar.gz
}

monitor_update(){
    #monitor
    cd $CDIR
    cd ../../opsany-saas/
    /bin/cp monitor-opsany-*.tar.gz ../opsany-paas/saas/
    cd $CDIR
    python3 ../saas/deploy.py --domain $DOMAIN_NAME --username admin --password $ADMIN_PASSWORD --file_name ../saas/monitor-opsany-*.tar.gz
}

cmp_update(){
    #cmp
    cd $CDIR
    cd ../../opsany-saas/
    /bin/cp cmp-opsany-*.tar.gz ../opsany-paas/saas/
    rm -rf cmp
    cd $CDIR
    python3 ../saas/deploy.py --domain $DOMAIN_NAME --username admin --password $ADMIN_PASSWORD --file_name ../saas/cmp-opsany-*.tar.gz
}

devops_update(){
    #devops
    cd $CDIR
    cd ../../opsany-saas/
    /bin/cp devops-opsany-*.tar.gz ../opsany-paas/saas/
    cd $CDIR
    python3 ../saas/deploy.py --domain $DOMAIN_NAME --username admin --password $ADMIN_PASSWORD --file_name ../saas/devops-opsany-*.tar.gz
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
