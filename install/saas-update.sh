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
ADMIN_PASSWORD=""

# Install Inspection
if [ ! -f ./install.config ];then
      echo "Please Change Directory to ${INSTALL_PATH}/install"
      exit
else
    grep '^[A-Z]' install.config > install.env
    source ./install.env && rm -f install.env
    if [ -z "$ADMIN_PASSWORD" ];then
        source ${INSTALL_PATH}/conf/.passwd_env
    fi
fi

rm -f ../saas/*.gz

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
    /bin/cp -f job-opsany-*.tar.gz ../opsany-paas/saas/
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

bastion_update(){
    #devops
    cd $CDIR
    cd ../../opsany-saas/
    /bin/cp bastion-opsany-*.tar.gz ../opsany-paas/saas/
    cd $CDIR
    python3 ../saas/deploy.py --domain $DOMAIN_NAME --username admin --password $ADMIN_PASSWORD --file_name ../saas/bastion-opsany-*.tar.gz
}

pipeline_update(){
    #pipeline
    cd $CDIR
    cd ../../opsany-saas/
    /bin/cp pipeline-opsany-*.tar.gz ../opsany-paas/saas/
    cd $CDIR
    python3 ../saas/deploy.py --domain $DOMAIN_NAME --username admin --password $ADMIN_PASSWORD --file_name ../saas/pipeline-opsany-*.tar.gz
}

deploy_update(){
    #deploy
    cd $CDIR
    cd ../../opsany-saas/
    /bin/cp deploy-opsany-*.tar.gz ../opsany-paas/saas/
    cd $CDIR
    python3 ../saas/deploy.py --domain $DOMAIN_NAME --username admin --password $ADMIN_PASSWORD --file_name ../saas/deploy-opsany-*.tar.gz
}

dashboard_update(){
    #dashboard
    cd $CDIR
    cd ../../opsany-saas/
    /bin/cp dashboard-opsany-*.tar.gz ../opsany-paas/saas/
    cd $CDIR
    python3 ../saas/deploy.py --domain $DOMAIN_NAME --username admin --password $ADMIN_PASSWORD --file_name ../saas/dashboard-opsany-*.tar.gz
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
    bastion)
        bastion_update
        ;;
    dashboard)
        dashboard_update
        ;;
	base)
		rbac_update
		workbench_update
		cmdb_update
		control_update
		job_update
        dashboard_update
		cmp_update
        bastion_update
		;;
    devops)
		devops_update
        #pipeline_update
        #deploy_update
		;;
    all)
        rbac_update
		workbench_update
		cmdb_update
		control_update
		job_update
        dashboard_update
		cmp_update
        bastion_update
        devops_update
        #pipeline_update
        #deploy_update
        monitor_update
        ;;
	help|*)
		echo $"Usage: $0 {[base|devops|monitor|all|rbac|workbench|cmdb|control|job|monitor|cmp|devops|bastion|dashboard|help}"
	        ;;
esac
}

main $1
