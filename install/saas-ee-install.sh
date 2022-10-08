#!/bin/bash
#******************************************
# Author:       Jason Zhao
# Email:        zhaoshundong@opsany.com
# Organization: OpsAny https://www.opsany.com/
# Description:  OpsAny Enterprise edition SAAS Install Script
#******************************************

# Data/Time
CTIME=$(date "+%Y-%m-%d-%H-%M")

# Shell Envionment Variables
CDIR=$(pwd)
SHELL_NAME="saas-ee-install.sh"
SHELL_LOG="${SHELL_NAME}.log"
ADMIN_PASSWORD=""

# Check SAAS Package
if [ ! -d ../../opsany-saas-ee ];then
    echo "======Download the Enterprise SAAS package first======"
    exit;
fi

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

#Configuration file write to DB
cd $CDIR 
cd ../saas/
python3 add_ee_env.py

# Shell Log Record
shell_log(){
    LOG_INFO=$1
    echo "----------------$CTIME ${SHELL_NAME} : ${LOG_INFO}----------------"
    echo "$CTIME ${SHELL_NAME} : ${LOG_INFO}" >> ${SHELL_LOG}
}

# SaaS DB Initialize
saas_db_init(){
    shell_log "======MySQL Initialize======"
    #event
    mysql -h "${MYSQL_SERVER_IP}" -u root -p"${MYSQL_ROOT_PASSWORD}" -e "create database event DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;"
    mysql -h "${MYSQL_SERVER_IP}" -u root -p"${MYSQL_ROOT_PASSWORD}" -e "grant all on event.* to event@'%' identified by "\"${MYSQL_OPSANY_EVENT_PASSWORD}\"";"
    mysql -h "${MYSQL_SERVER_IP}" -u root -p"${MYSQL_ROOT_PASSWORD}" -e "grant all on event.* to opsany@'%' identified by "\"${MYSQL_OPSANY_PASSWORD}\"";" 
    
    #auto
    mysql -h "${MYSQL_SERVER_IP}" -u root -p"${MYSQL_ROOT_PASSWORD}" -e "create database auto DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;"
    mysql -h "${MYSQL_SERVER_IP}" -u root -p"${MYSQL_ROOT_PASSWORD}" -e "grant all on auto.* to auto@'%' identified by "\"${MYSQL_OPSANY_AUTO_PASSWORD}\"";"
    mysql -h "${MYSQL_SERVER_IP}" -u root -p"${MYSQL_ROOT_PASSWORD}" -e "grant all on auto.* to opsany@'%' identified by "\"${MYSQL_OPSANY_PASSWORD}\"";" 

    #k8s
    mysql -h "${MYSQL_SERVER_IP}" -u root -p"${MYSQL_ROOT_PASSWORD}" -e "create database k8s DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;"
    mysql -h "${MYSQL_SERVER_IP}" -u root -p"${MYSQL_ROOT_PASSWORD}" -e "grant all on k8s.* to k8s@'%' identified by "\"${MYSQL_OPSANY_K8S_PASSWORD}\"";"
    mysql -h "${MYSQL_SERVER_IP}" -u root -p"${MYSQL_ROOT_PASSWORD}" -e "grant all on k8s.* to opsany@'%' identified by "\"${MYSQL_OPSANY_PASSWORD}\"";" 

    #prom
    mysql -h "${MYSQL_SERVER_IP}" -u root -p"${MYSQL_ROOT_PASSWORD}" -e "create database prom DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;"
    mysql -h "${MYSQL_SERVER_IP}" -u root -p"${MYSQL_ROOT_PASSWORD}" -e "grant all on prom.* to prom@'%' identified by "\"${MYSQL_OPSANY_PROM_PASSWORD}\"";"
    mysql -h "${MYSQL_SERVER_IP}" -u root -p"${MYSQL_ROOT_PASSWORD}" -e "grant all on prom.* to opsany@'%' identified by "\"${MYSQL_OPSANY_PASSWORD}\"";" 
}

# MonogDB Initialize
mongodb_init(){
    shell_log "======Enterprise SAAS MongoDB Initialize======"
    mongo --host $MONGO_SERVER_IP -u $MONGO_INITDB_ROOT_USERNAME -p$MONGO_INITDB_ROOT_PASSWORD <<END
    use auto;
    db.createUser( {user: "auto",pwd: "$MONGO_AUTO_PASSWORD",roles: [ { role: "readWrite", db: "auto" } ]});
    use event;
    db.createUser( {user: "event",pwd: "$MONGO_EVENT_PASSWORD",roles: [ { role: "readWrite", db: "event" } ]});
    exit;
END
    shell_log "======Enterprise SAAS MongoDB Initialize End======"
}

# SaaS Deploy
saas_deploy(){
    cd $CDIR
    cd ../../opsany-saas-ee/
    /bin/cp *.tar.gz ../opsany-paas/saas/
    cd $CDIR
    cd ../saas/ && ls *.tar.gz
    if [ $? -ne 0 ];then
        echo "Please Download SAAS first" && exit
    fi
    python3 deploy.py --domain $DOMAIN_NAME --username admin --password $ADMIN_PASSWORD --file_name auto-opsany-*.tar.gz
    python3 deploy.py --domain $DOMAIN_NAME --username admin --password $ADMIN_PASSWORD --file_name event-opsany-*.tar.gz
    python3 deploy.py --domain $DOMAIN_NAME --username admin --password $ADMIN_PASSWORD --file_name k8s-opsany-*.tar.gz
    python3 deploy.py --domain $DOMAIN_NAME --username admin --password $ADMIN_PASSWORD --file_name prom-opsany-*.tar.gz
    #python3 deploy.py --domain $DOMAIN_NAME --username admin --password $ADMIN_PASSWORD --file_name hostsec-opsany-*.tar.gz
    #python3 deploy.py --domain $DOMAIN_NAME --username admin --password $ADMIN_PASSWORD --file_name redis-opsany-*.tar.gz
    #python3 deploy.py --domain $DOMAIN_NAME --username admin --password $ADMIN_PASSWORD --file_name mysql-opsany-*.tar.gz
    #python3 deploy.py --domain $DOMAIN_NAME --username admin --password $ADMIN_PASSWORD --file_name mongodb-opsany-*.tar.gz
    #python3 deploy.py --domain $DOMAIN_NAME --username admin --password $ADMIN_PASSWORD --file_name host-opsany-*.tar.gz
    shell_log "======OpsAny: Make Ops Perfect======"

}


ee_saas_init(){
    #cd $CDIR && cd ../saas/ 
    #python3 saas-ee-init.py --domain https://www.opsany_url.cn --username opsany_username  --password opsany_password --st2_url https://st2_url/  --st2_username st2admin --st2_password st2_password  
    echo 'hehe'
}

# Main
main(){
    saas_db_init
    mongodb_init
    saas_deploy
}

main
