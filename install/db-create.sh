#!/bin/bash
#******************************************
# Author:       Jason Zhao
# Email:        zhaoshundong@opsany.com
# Organization: OpsAny https://www.opsany.com/
# Description:  OpsAny Database Update Script
#******************************************

# Get Data/Time
CTIME=$(date "+%Y-%m-%d-%H-%M")

# Shell Envionment Variables
CDIR=$(pwd)
SHELL_NAME="db-create.sh"
SHELL_LOG="${CDIR}/${SHELL_NAME}.log"

# Shell Log Record
shell_log(){
    LOG_INFO=$1
    echo -e "<------>  $CTIME ${SHELL_NAME} : ${LOG_INFO}  <------>"
    echo "$CTIME ${SHELL_NAME} : ${LOG_INFO}" >> ${SHELL_LOG}
}

# Install Inspection
if [ ! -f ./install.config ];then
      shell_error_log "======Error: Please Change Directory to ${INSTALL_PATH}/install======"
      exit
else
    grep '^[A-Z]' install.config > install.env
    source ./install.env && rm -f install.env
    export MYSQL_PWD=${MYSQL_ROOT_PASSWORD}
    export MYSQL_SERVER_PORT="8031"
fi

paas_db(){    
    # PaaS
    export MYSQL_PWD=${MYSQL_ROOT_PASSWORD}
    mysql -h "${MYSQL_SERVER_IP}" -P ${MYSQL_SERVER_PORT} -u root -e "CREATE DATABASE IF NOT EXISTS opsany_paas DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;"
    mysql -h "${MYSQL_SERVER_IP}" -P ${MYSQL_SERVER_PORT} -u root -e "CREATE DATABASE IF NOT EXISTS opsany_proxy DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;"
    mysql -h "${MYSQL_SERVER_IP}" -P ${MYSQL_SERVER_PORT} -u root -e "CREATE USER opsany@'%' identified by "\"${MYSQL_OPSANY_PASSWORD}\"";"
    mysql -h "${MYSQL_SERVER_IP}" -P ${MYSQL_SERVER_PORT} -u root -e "grant all on opsany_paas.* to opsany@'%';"
    mysql -h "${MYSQL_SERVER_IP}" -P ${MYSQL_SERVER_PORT} -u root -e "grant all on opsany_proxy.* to opsany@'%';"
    mysql -h "${MYSQL_SERVER_IP}" -P ${MYSQL_SERVER_PORT} -u root opsany_paas < ${INSTALL_PATH}/dbbackup/opsany-paas.sql
    mysql -h "${MYSQL_SERVER_IP}" -P ${MYSQL_SERVER_PORT} -u root opsany_proxy < ${INSTALL_PATH}/dbbackup/opsany-proxy.sql
}

rbac_db(){
    # rbac
    export MYSQL_PWD=${MYSQL_ROOT_PASSWORD}
    mysql -h "${MYSQL_SERVER_IP}" -P ${MYSQL_SERVER_PORT} -u root -e "create database rbac DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;"
    mysql -h "${MYSQL_SERVER_IP}" -P ${MYSQL_SERVER_PORT} -u root -e "CREATE USER 'rbac'@'%' identified by "\"${MYSQL_OPSANY_RBAC_PASSWORD}\"";"
    mysql -h "${MYSQL_SERVER_IP}" -P ${MYSQL_SERVER_PORT} -u root -e "grant all on rbac.* to rbac@'%';"
    mysql -h "${MYSQL_SERVER_IP}" -P ${MYSQL_SERVER_PORT} -u root rbac < ${INSTALL_PATH}/dbbackup/rbac.sql
}

workbench_db(){
    # workbench
    export MYSQL_PWD=${MYSQL_ROOT_PASSWORD}
    mysql -h "${MYSQL_SERVER_IP}" -P ${MYSQL_SERVER_PORT} -u root -e "create database workbench DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;"
    mysql -h "${MYSQL_SERVER_IP}" -P ${MYSQL_SERVER_PORT} -u root -e "CREATE USER 'workbench'@'%' IDENTIFIED BY "\"${MYSQL_OPSANY_WORKBENCH_PASSWORD}\"";"
    mysql -h "${MYSQL_SERVER_IP}" -P ${MYSQL_SERVER_PORT} -u root -e "grant all on workbench.* to workbench@'%';"
    mysql -h "${MYSQL_SERVER_IP}" -P ${MYSQL_SERVER_PORT} -u root workbench < ${INSTALL_PATH}/dbbackup/workbench.sql
}

cmdb_db(){
    # cmdb
    export MYSQL_PWD=${MYSQL_ROOT_PASSWORD}
    mysql -h "${MYSQL_SERVER_IP}" -P ${MYSQL_SERVER_PORT} -u root -e "create database cmdb DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;"
    mysql -h "${MYSQL_SERVER_IP}" -P ${MYSQL_SERVER_PORT} -u root -e "CREATE USER 'cmdb'@'%' IDENTIFIED BY "\"${MYSQL_OPSANY_CMDB_PASSWORD}\"";"
    mysql -h "${MYSQL_SERVER_IP}" -P ${MYSQL_SERVER_PORT} -u root -e "grant all on cmdb.* to cmdb@'%';"
    mysql -h "${MYSQL_SERVER_IP}" -P ${MYSQL_SERVER_PORT} -u root cmdb < ${INSTALL_PATH}/dbbackup/cmdb.sql
}

control_db(){
    # control
    export MYSQL_PWD=${MYSQL_ROOT_PASSWORD}
    mysql -h "${MYSQL_SERVER_IP}" -P ${MYSQL_SERVER_PORT} -u root -e "create database control DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;"
    mysql -h "${MYSQL_SERVER_IP}" -P ${MYSQL_SERVER_PORT} -u root -e "CREATE USER 'control'@'%' identified by "\"${MYSQL_OPSANY_CONTROL_PASSWORD}\"";"
    mysql -h "${MYSQL_SERVER_IP}" -P ${MYSQL_SERVER_PORT} -u root -e "grant all on control.* to control@'%';"
    mysql -h "${MYSQL_SERVER_IP}" -P ${MYSQL_SERVER_PORT} -u root control < ${INSTALL_PATH}/dbbackup/control.sql
}

job_db(){
    # job
    export MYSQL_PWD=${MYSQL_ROOT_PASSWORD}
    mysql -h "${MYSQL_SERVER_IP}" -P ${MYSQL_SERVER_PORT} -u root -e "create database job DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;"
    mysql -h "${MYSQL_SERVER_IP}" -P ${MYSQL_SERVER_PORT} -u root -e "CREATE USER 'job'@'%' identified by "\"${MYSQL_OPSANY_JOB_PASSWORD}\"";"
    mysql -h "${MYSQL_SERVER_IP}" -P ${MYSQL_SERVER_PORT} -u root -e "grant all on job.* to job@'%';"
    mysql -h "${MYSQL_SERVER_IP}" -P ${MYSQL_SERVER_PORT} -u root job < ${INSTALL_PATH}/dbbackup/job.sql
}  

monitor_db(){
    # monitor
    export MYSQL_PWD=${MYSQL_ROOT_PASSWORD}
    mysql -h "${MYSQL_SERVER_IP}" -P ${MYSQL_SERVER_PORT} -u root -e "create database monitor DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;"
    mysql -h "${MYSQL_SERVER_IP}" -P ${MYSQL_SERVER_PORT} -u root -e "CREATE USER 'monitor'@'%' identified by "\"${MYSQL_OPSANY_MONITOR_PASSWORD}\"";"
    mysql -h "${MYSQL_SERVER_IP}" -P ${MYSQL_SERVER_PORT} -u root -e "grant all on monitor.* to monitor@'%';" 
    mysql -h "${MYSQL_SERVER_IP}" -P ${MYSQL_SERVER_PORT} -u root monitor < ${INSTALL_PATH}/dbbackup/monitor.sql
}
    
cmp_db(){
    # cmp
    export MYSQL_PWD=${MYSQL_ROOT_PASSWORD}
    mysql -h "${MYSQL_SERVER_IP}" -P ${MYSQL_SERVER_PORT} -u root -e "create database cmp DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;"
    mysql -h "${MYSQL_SERVER_IP}" -P ${MYSQL_SERVER_PORT} -u root -e "CREATE USER 'cmp'@'%' identified by "\"${MYSQL_OPSANY_CMP_PASSWORD}\"";"
    mysql -h "${MYSQL_SERVER_IP}" -P ${MYSQL_SERVER_PORT} -u root -e "grant all on cmp.* to cmp@'%';" 
    mysql -h "${MYSQL_SERVER_IP}" -P ${MYSQL_SERVER_PORT} -u root cmp < ${INSTALL_PATH}/dbbackup/cmp.sql
}

bastion_db(){
    # bastion
    export MYSQL_PWD=${MYSQL_ROOT_PASSWORD}
    mysql -h "${MYSQL_SERVER_IP}" -P ${MYSQL_SERVER_PORT} -u root -e "create database bastion DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;"
    mysql -h "${MYSQL_SERVER_IP}" -P ${MYSQL_SERVER_PORT} -u root -e "CREATE USER 'bastion'@'%' identified by "\"${MYSQL_OPSANY_BASTION_PASSWORD}\"";"
    mysql -h "${MYSQL_SERVER_IP}" -P ${MYSQL_SERVER_PORT} -u root -e "grant all on bastion.* to bastion@'%';" 
    mysql -h "${MYSQL_SERVER_IP}" -P ${MYSQL_SERVER_PORT} -u root bastion < ${INSTALL_PATH}/dbbackup/bastion.sql
}
    
devops_db(){
    # devops
    export MYSQL_PWD=${MYSQL_ROOT_PASSWORD}
    mysql -h "${MYSQL_SERVER_IP}" -P ${MYSQL_SERVER_PORT} -u root -e "create database devops DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;"
    mysql -h "${MYSQL_SERVER_IP}" -P ${MYSQL_SERVER_PORT} -u root -e "CREATE USER 'devops'@'%' identified by "\"${MYSQL_OPSANY_DEVOPS_PASSWORD}\"";"
    mysql -h "${MYSQL_SERVER_IP}" -P ${MYSQL_SERVER_PORT} -u root -e "grant all on devops.* to devops@'%';" 
    mysql -h "${MYSQL_SERVER_IP}" -P ${MYSQL_SERVER_PORT} -u root devops < ${INSTALL_PATH}/dbbackup/devops.sql
} 

repo_db(){
    # repo
    export MYSQL_PWD=${MYSQL_ROOT_PASSWORD}
    mysql -h "${MYSQL_SERVER_IP}" -P ${MYSQL_SERVER_PORT} -u root -e "create database repo DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;"
    mysql -h "${MYSQL_SERVER_IP}" -P ${MYSQL_SERVER_PORT} -u root -e "CREATE USER 'repo'@'%' identified by "\"${MYSQL_OPSANY_REPO_PASSWORD}\"";"
    mysql -h "${MYSQL_SERVER_IP}" -P ${MYSQL_SERVER_PORT} -u root -e "grant all on repo.* to repo@'%';" 
    mysql -h "${MYSQL_SERVER_IP}" -P ${MYSQL_SERVER_PORT} -u root repo < ${INSTALL_PATH}/dbbackup/repo.sql
} 

pipeline_db(){
    # pipeline
    export MYSQL_PWD=${MYSQL_ROOT_PASSWORD}
    mysql -h "${MYSQL_SERVER_IP}" -P ${MYSQL_SERVER_PORT} -u root -e "create database pipeline DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;"
    mysql -h "${MYSQL_SERVER_IP}" -P ${MYSQL_SERVER_PORT} -u root -e "CREATE USER 'pipeline'@'%' identified by "\"${MYSQL_OPSANY_PIPELINE_PASSWORD}\"";"
    mysql -h "${MYSQL_SERVER_IP}" -P ${MYSQL_SERVER_PORT} -u root -e "grant all on pipeline.* to pipeline@'%';" 
    mysql -h "${MYSQL_SERVER_IP}" -P ${MYSQL_SERVER_PORT} -u root pipeline < ${INSTALL_PATH}/dbbackup/pipeline.sql
}
    
deploy_db(){
    # deploy
    export MYSQL_PWD=${MYSQL_ROOT_PASSWORD}
    mysql -h "${MYSQL_SERVER_IP}" -P ${MYSQL_SERVER_PORT} -u root -e "create database deploy DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;"
    mysql -h "${MYSQL_SERVER_IP}" -P ${MYSQL_SERVER_PORT} -u root -e "CREATE USER 'deploy'@'%' identified by "\"${MYSQL_OPSANY_DEPLOY_PASSWORD}\"";"
    mysql -h "${MYSQL_SERVER_IP}" -P ${MYSQL_SERVER_PORT} -u root -e "grant all on deploy.* to deploy@'%';" 
    mysql -h "${MYSQL_SERVER_IP}" -P ${MYSQL_SERVER_PORT} -u root deploy < ${INSTALL_PATH}/dbbackup/deploy.sql
}
    
code_db(){
    # code
    export MYSQL_PWD=${MYSQL_ROOT_PASSWORD}
    mysql -h "${MYSQL_SERVER_IP}" -P ${MYSQL_SERVER_PORT} -u root -e "create database code DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;"
    mysql -h "${MYSQL_SERVER_IP}" -P ${MYSQL_SERVER_PORT} -u root -e "CREATE USER 'code'@'%' identified by "\"${MYSQL_OPSANY_CODE_PASSWORD}\"";"
    mysql -h "${MYSQL_SERVER_IP}" -P ${MYSQL_SERVER_PORT} -u root -e "grant all on code.* to code@'%';"
    mysql -h "${MYSQL_SERVER_IP}" -P ${MYSQL_SERVER_PORT} -u root code < ${INSTALL_PATH}/dbbackup/code.sql
}

# Main
main(){
    case "$1" in
        paas)
            paas_db
            ;;
        rbac)
            rbac_db
            ;;
        workbench)
            workbench_db
            ;;
        cmdb)
            cmdb_db
            ;;
        control)
            control_db
            ;;
        job)
            job_db
            ;;
        monitor)
            monitor_db
            ;;
        cmp)
            cmp_db
            ;;
        bastion)
            bastion_db
            ;;
        devops)
            devops_db
            ;;
        pipeline)
            pipeline_db
            ;;
        deploy)
            deploy_db
            ;;
        repo)
            repo_db
            ;;
        code)
            code_db
            ;;
        all)
            paas_db;
            rbac_db;
            workbench_db;
            cmdb_db;
            control_db;
            job_db;
            monitor_db;
            cmp_db;
            bastion_db;
            devops_db;
            pipeline_db;
            deploy_db;
            repo_db;
            #code_db;
            ;;
        ops)
            paas_db;
            rbac_db;
            workbench_db;
            cmdb_db;
            control_db;
            job_db;
            monitor_db;
            cmp_db;
            bastion_db;
            ;;
        dev)
            devops_db;
            pipeline_db;
            deploy_db;
            repo_db;
            #code_db;
            ;;
        help|*)
	        echo $"Usage: $0 {ops|dev|all|help}"
	        ;;
    esac
}

main $1 
    


