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
SHELL_NAME="database-backup.sh"
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

mysql_backup(){
    shell_log "Start: MySQL Backup..."
    export MYSQL_PWD=${MYSQL_ROOT_PASSWORD}
    mysqldump -h "${MYSQL_SERVER_IP}" -u root --all-databases > /opt/opsany_mysql_backup_${CTIME}.sql
    ls -lh /opt/opsany_mysql_backup_${CTIME}.sql
}

mongodb_backup(){
    shell_log "Start: MongoDB Backup..."
    docker exec -e MONGO_INITDB_ROOT_USERNAME=$MONGO_INITDB_ROOT_USERNAME \
                -e MONGO_INITDB_ROOT_PASSWORD=$MONGO_INITDB_ROOT_PASSWORD \
                opsany-base-mongodb /bin/bash -c "mongodump -u $MONGO_INITDB_ROOT_USERNAME -p $MONGO_INITDB_ROOT_PASSWORD -o /opt/mongodb-backup-${CTIME}"
    docker cp opsany-base-mongodb:/opt/mongodb-backup-${CTIME} /opt/ 
    ls -d /opt/mongodb-backup-${CTIME}

}

# Main
main(){
    case "$1" in
	all)
            mysql_backup
	    mongodb_backup
		;;
        mysql)
            mysql_backup
        ;;
        mongodb)
            mongodb_backup
        ;;
	help|*)
		echo $"Usage: $0 {all|mysql|mongodb|help}"
	    ;;
    esac
}

main $1
