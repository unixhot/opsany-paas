#!/bin/bash
#******************************************
# Author:       Jason Zhao
# Email:        zhaoshundong@opsany.com
# Organization: OpsAny https://www.opsany.com/
# Description:  OpsAny Database Backup Script
#******************************************

# Get Data/Time
CTIME=$(date "+%Y-%m-%d-%H-%M")

# Shell Envionment Variables
CDIR=$(pwd)
SHELL_NAME="db-backup.sh"
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
fi

mysql_ops_backup(){
    export MYSQL_PWD=${MYSQL_ROOT_PASSWORD}
    mkdir -p ${INSTALL_PATH}/dbbackup
    shell_log "mysql backup: opsany_paas"
    mysqldump -h "${MYSQL_SERVER_IP}" -u root opsany_paas --add-drop-database > ${INSTALL_PATH}/dbbackup/opsany-paas.sql
    shell_log "mysql backup: opsany_proxy"
    mysqldump -h "${MYSQL_SERVER_IP}" -u root opsany_proxy --add-drop-database > ${INSTALL_PATH}/dbbackup/opsany-proxy.sql
    shell_log "mysql backup: rbac"
    mysqldump -h "${MYSQL_SERVER_IP}" -u root rbac --add-drop-database > ${INSTALL_PATH}/dbbackup/rbac.sql
    shell_log "mysql backup: workbench"
    mysqldump -h "${MYSQL_SERVER_IP}" -u root workbench --add-drop-database > ${INSTALL_PATH}/dbbackup/workbench.sql
    shell_log "mysql backup: cmdb"
    mysqldump -h "${MYSQL_SERVER_IP}" -u root cmdb --add-drop-database > ${INSTALL_PATH}/dbbackup/cmdb.sql
    shell_log "mysql backup: control"
    mysqldump -h "${MYSQL_SERVER_IP}" -u root control --add-drop-database > ${INSTALL_PATH}/dbbackup/control.sql
    shell_log "mysql backup: job"
    mysqldump -h "${MYSQL_SERVER_IP}" -u root job --add-drop-database > ${INSTALL_PATH}/dbbackup/job.sql
    shell_log "mysql backup: monitor"
    mysqldump -h "${MYSQL_SERVER_IP}" -u root monitor --add-drop-database > ${INSTALL_PATH}/dbbackup/monitor.sql
    shell_log "mysql backup: cmp"
    mysqldump -h "${MYSQL_SERVER_IP}" -u root cmp --add-drop-database > ${INSTALL_PATH}/dbbackup/cmp.sql
    shell_log "mysql backup: bastion"
    mysqldump -h "${MYSQL_SERVER_IP}" -u root bastion --add-drop-database > ${INSTALL_PATH}/dbbackup/bastion.sql
}

mysql_dev_backup(){
    shell_log "mysql backup: devops"
    mysqldump -h "${MYSQL_SERVER_IP}" -u root devops --add-drop-database > ${INSTALL_PATH}/dbbackup/devops.sql
    shell_log "mysql backup: pipeline"
    mysqldump -h "${MYSQL_SERVER_IP}" -u root pipeline --add-drop-database > ${INSTALL_PATH}/dbbackup/pipeline.sql
    shell_log "mysql backup: deploy"
    mysqldump -h "${MYSQL_SERVER_IP}" -u root deploy --add-drop-database > ${INSTALL_PATH}/dbbackup/deploy.sql
    shell_log "mysql backup: repo"
    mysqldump -h "${MYSQL_SERVER_IP}" -u root repo --add-drop-database > ${INSTALL_PATH}/dbbackup/repo.sql
}

# Main
main(){
    case "$1" in
	all)
          mysql_ops_backup
          mysql_dev_backup
	      ;;
    ops)
          mysql_ops_backup
          ;;
    dev)
          mysql_dev_backup
          ;;
	help|*)
		echo $"Usage: $0 {all|ops|dev|help}"
	      ;;
    esac
}

main $1


