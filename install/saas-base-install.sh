#!/bin/bash
#******************************************
# Author:       Jason Zhao
# Email:        zhaoshundong@opsany.com
# Organization: OpsAny https://www.opsany.com/
# Description:  OpsAny SAAS Base Install Script
#******************************************

# Data/Time
CTIME=$(date "+%Y-%m-%d-%H-%M")

# Shell Envionment Variables
CDIR=$(pwd)
SHELL_NAME="saas-base-install.sh"
SHELL_LOG="${SHELL_NAME}.log"
ADMIN_PASSWORD="admin"

# Check SAAS Package
if [ ! -d ../../opsany-saas ];then
    echo "======Download the SAAS package first======"
    exit;
fi

# Install Inspection
if [ ! -f ./install.config ];then
      echo "Please Change Directory to ${INSTALL_PATH}/install"
      exit
else
    grep '^[A-Z]' install.config > install.env
    source ./install.env && rm -f install.env
fi

install_init(){
    # Add ENV For SaaS
    cd ../saas/
    python3 add_env.py
    cp invscript_proxy.py ${INSTALL_PATH}/conf/proxy/
    sed -i "s/LOCALHOST/${MYSQL_SERVER_IP}/g" ${INSTALL_PATH}/conf/proxy/invscript_proxy.py
    sed -i "s/PROXY_PASSWORD/${MYSQL_OPSANY_PASSWORD}/g" ${INSTALL_PATH}/conf/proxy/invscript_proxy.py
    chmod +x ${INSTALL_PATH}/conf/proxy/invscript_proxy.py
}

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

# Start Proxy
proxy_install(){
    # Proxy
    shell_log "======Start Proxy======"
    docker run --restart=always --name opsany-proxy -d \
        -p 4505:4505 -p 4506:4506 -p 8010:8010 \
        -v ${INSTALL_PATH}/logs:${INSTALL_PATH}/logs \
        -v ${INSTALL_PATH}/proxy-volume/certs/:/etc/pki/tls/certs/ \
        -v ${INSTALL_PATH}/proxy-volume/etc/salt/:/etc/salt/ \
        -v ${INSTALL_PATH}/proxy-volume/cache/:/var/cache/salt/ \
        -v ${INSTALL_PATH}/proxy-volume/srv/salt:/srv/salt/ \
        -v ${INSTALL_PATH}/proxy-volume/srv/pillar:/srv/pillar/ \
        -v ${INSTALL_PATH}/proxy-volume/srv/playbook:/srv/playbook/ \
        -v ${INSTALL_PATH}/uploads:/opt/opsany/uploads \
        -v ${INSTALL_PATH}/conf/proxy/settings_production.py.proxy:/opt/opsany-proxy/config/prod.py \
        -v ${INSTALL_PATH}/conf/proxy/invscript_proxy.py:/opt/opsany-proxy/invscript_proxy.py \
        -v ${INSTALL_PATH}/proxy-volume/pki:/opt/opsany/pki \
        -v /etc/localtime:/etc/localtime:ro \
        ${PAAS_DOCKER_REG}/opsany-proxy:1.2.12
}

# SaaS DB Initialize
mysql_init(){
    shell_log "======MySQL Initialize======"
    cd ${CDIR}
    #esb
    mysql -h "${MYSQL_SERVER_IP}" -u root -p"${MYSQL_ROOT_PASSWORD}" opsany_paas < ./init/esb-init/esb_api_doc.sql
    mysql -h "${MYSQL_SERVER_IP}" -u root -p"${MYSQL_ROOT_PASSWORD}" opsany_paas < ./init/esb-init/esb_channel.sql
    mysql -h "${MYSQL_SERVER_IP}" -u root -p"${MYSQL_ROOT_PASSWORD}" opsany_paas < ./init/esb-init/esb_component_system.sql
    
    #rbac
    mysql -h "${MYSQL_SERVER_IP}" -u root -p"${MYSQL_ROOT_PASSWORD}" -e "create database rbac DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;"
    mysql -h "${MYSQL_SERVER_IP}" -u root -p"${MYSQL_ROOT_PASSWORD}" -e "grant all on rbac.* to rbac@'%' identified by "\"${MYSQL_OPSANY_RBAC_PASSWORD}\"";"
    mysql -h "${MYSQL_SERVER_IP}" -u root -p"${MYSQL_ROOT_PASSWORD}" -e "grant all on rbac.* to opsany@'%' identified by "\"${MYSQL_OPSANY_PASSWORD}\"";"
    
    #workbench
    mysql -h "${MYSQL_SERVER_IP}" -u root -p"${MYSQL_ROOT_PASSWORD}" -e "create database workbench DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;"
    mysql -h "${MYSQL_SERVER_IP}" -u root -p"${MYSQL_ROOT_PASSWORD}" -e "grant all on workbench.* to workbench@'%' identified by "\"${MYSQL_OPSANY_WORKBENCH_PASSWORD}\"";"
    mysql -h "${MYSQL_SERVER_IP}" -u root -p"${MYSQL_ROOT_PASSWORD}" -e "grant all on workbench.* to opsany@'%' identified by "\"${MYSQL_OPSANY_PASSWORD}\"";"
    
    #cmdb
    mysql -h "${MYSQL_SERVER_IP}" -u root -p"${MYSQL_ROOT_PASSWORD}" -e "create database cmdb DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;"
    mysql -h "${MYSQL_SERVER_IP}" -u root -p"${MYSQL_ROOT_PASSWORD}" -e "grant all on cmdb.* to cmdb@'%' identified by "\"${MYSQL_OPSANY_CMDB_PASSWORD}\"";"
    mysql -h "${MYSQL_SERVER_IP}" -u root -p"${MYSQL_ROOT_PASSWORD}" -e "grant all on cmdb.* to opsany@'%' identified by "\"${MYSQL_OPSANY_PASSWORD}\"";"
    
    #control
    mysql -h "${MYSQL_SERVER_IP}" -u root -p"${MYSQL_ROOT_PASSWORD}" -e "create database control DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;"
    mysql -h "${MYSQL_SERVER_IP}" -u root -p"${MYSQL_ROOT_PASSWORD}" -e "grant all on control.* to control@'%' identified by "\"${MYSQL_OPSANY_CONTROL_PASSWORD}\"";"
    mysql -h "${MYSQL_SERVER_IP}" -u root -p"${MYSQL_ROOT_PASSWORD}" -e "grant all on control.* to opsany@'%' identified by "\"${MYSQL_OPSANY_PASSWORD}\"";"
    
    #job
    mysql -h "${MYSQL_SERVER_IP}" -u root -p"${MYSQL_ROOT_PASSWORD}" -e "create database job DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;"
    mysql -h "${MYSQL_SERVER_IP}" -u root -p"${MYSQL_ROOT_PASSWORD}" -e "grant all on job.* to job@'%' identified by "\"${MYSQL_OPSANY_JOB_PASSWORD}\"";"
    mysql -h "${MYSQL_SERVER_IP}" -u root -p"${MYSQL_ROOT_PASSWORD}" -e "grant all on job.* to opsany@'%' identified by "\"${MYSQL_OPSANY_PASSWORD}\"";"
    
    #cmp
    mysql -h "${MYSQL_SERVER_IP}" -u root -p"${MYSQL_ROOT_PASSWORD}" -e "create database cmp DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;"
    mysql -h "${MYSQL_SERVER_IP}" -u root -p"${MYSQL_ROOT_PASSWORD}" -e "grant all on cmp.* to cmp@'%' identified by "\"${MYSQL_OPSANY_CMP_PASSWORD}\"";"
    mysql -h "${MYSQL_SERVER_IP}" -u root -p"${MYSQL_ROOT_PASSWORD}" -e "grant all on cmp.* to opsany@'%' identified by "\"${MYSQL_OPSANY_PASSWORD}\"";" 
    
    #bastion
    mysql -h "${MYSQL_SERVER_IP}" -u root -p"${MYSQL_ROOT_PASSWORD}" -e "create database bastion DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;"
    mysql -h "${MYSQL_SERVER_IP}" -u root -p"${MYSQL_ROOT_PASSWORD}" -e "grant all on bastion.* to bastion@'%' identified by "\"${MYSQL_OPSANY_BASTION_PASSWORD}\"";"
    mysql -h "${MYSQL_SERVER_IP}" -u root -p"${MYSQL_ROOT_PASSWORD}" -e "grant all on bastion.* to opsany@'%' identified by "\"${MYSQL_OPSANY_PASSWORD}\"";" 

    #dashboard
    mysql -h "${MYSQL_SERVER_IP}" -u root -p"${MYSQL_ROOT_PASSWORD}" -e "create database dashboard DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;"
    mysql -h "${MYSQL_SERVER_IP}" -u root -p"${MYSQL_ROOT_PASSWORD}" -e "grant all on dashboard.* to dashboard@'%' identified by "\"${MYSQL_OPSANY_DASHBOARD_PASSWORD}\"";"
    mysql -h "${MYSQL_SERVER_IP}" -u root -p"${MYSQL_ROOT_PASSWORD}" -e "grant all on dashboard.* to opsany@'%' identified by "\"${MYSQL_OPSANY_PASSWORD}\"";" 
}

# MonogDB Initialize
mongodb_init(){
    shell_log "======MongoDB Initialize======"
    sed -i "s/MONGO_WORKBENCH_PASSWORD/${MONGO_WORKBENCH_PASSWORD}/g" ${INSTALL_PATH}/init/mongodb-init/mongodb_init.js
    sed -i "s/MONGO_CMDB_PASSWORD/${MONGO_CMDB_PASSWORD}/g" ${INSTALL_PATH}/init/mongodb-init/mongodb_init.js
    sed -i "s/MONGO_JOB_PASSWORD/${MONGO_JOB_PASSWORD}/g" ${INSTALL_PATH}/init/mongodb-init/mongodb_init.js
    sed -i "s/MONGO_DEVOPS_PASSWORD/${MONGO_DEVOPS_PASSWORD}/g" ${INSTALL_PATH}/init/mongodb-init/mongodb_init.js
    sed -i "s/MONGO_CMP_PASSWORD/${MONGO_CMP_PASSWORD}/g" ${INSTALL_PATH}/init/mongodb-init/mongodb_init.js
    sed -i "s/MONGO_MONITOR_PASSWORD/${MONGO_MONITOR_PASSWORD}/g" ${INSTALL_PATH}/init/mongodb-init/mongodb_init.js
    sed -i "s/MONGO_AUTO_PASSWORD/${MONGO_AUTO_PASSWORD}/g" ${INSTALL_PATH}/init/mongodb-init/mongodb_init.js
    sed -i "s/MONGO_EVENT_PASSWORD/${MONGO_EVENT_PASSWORD}/g" ${INSTALL_PATH}/init/mongodb-init/mongodb_init.js
    sed -i "s/MONGO_PROM_PASSWORD/${MONGO_PROM_PASSWORD}/g" ${INSTALL_PATH}/init/mongodb-init/mongodb_init.js

    docker cp ${INSTALL_PATH}/init/mongodb-init/mongodb_init.js opsany-mongodb:/opt/
    docker exec -e MONGO_INITDB_ROOT_USERNAME=$MONGO_INITDB_ROOT_USERNAME \
                -e MONGO_INITDB_ROOT_PASSWORD=$MONGO_INITDB_ROOT_PASSWORD \
                opsany-mongodb /bin/bash -c "/usr/bin/mongo -u $MONGO_INITDB_ROOT_USERNAME -p $MONGO_INITDB_ROOT_PASSWORD /opt/mongodb_init.js"

    docker cp -a init/cmdb-init opsany-mongodb:/opt/
    docker exec -e MONGO_CMDB_PASSWORD=${MONGO_CMDB_PASSWORD} \
                opsany-mongodb /bin/bash -c "mongoimport -u cmdb -p ${MONGO_CMDB_PASSWORD} --db cmdb --drop --collection field_group < /opt/cmdb-init/field_group.json"
    docker exec -e MONGO_CMDB_PASSWORD=${MONGO_CMDB_PASSWORD} \
                opsany-mongodb /bin/bash -c "mongoimport -u cmdb -p ${MONGO_CMDB_PASSWORD} --db cmdb --drop --collection icon_model < /opt/cmdb-init/icon_model.json"
    docker exec -e MONGO_CMDB_PASSWORD=${MONGO_CMDB_PASSWORD} \
                opsany-mongodb /bin/bash -c "mongoimport -u cmdb -p ${MONGO_CMDB_PASSWORD} --db cmdb --drop --collection link_relationship_model < /opt/cmdb-init/link_relationship_model.json"
        docker exec -e MONGO_CMDB_PASSWORD=${MONGO_CMDB_PASSWORD} \
                opsany-mongodb /bin/bash -c "mongoimport -u cmdb -p ${MONGO_CMDB_PASSWORD} --db cmdb --drop --collection model_group < /opt/cmdb-init/model_group.json"
    docker exec -e MONGO_CMDB_PASSWORD=${MONGO_CMDB_PASSWORD} \
                opsany-mongodb /bin/bash -c "mongoimport -u cmdb -p ${MONGO_CMDB_PASSWORD} --db cmdb --drop --collection model_field < /opt/cmdb-init/model_field.json"
    docker exec -e MONGO_CMDB_PASSWORD=${MONGO_CMDB_PASSWORD} \
                opsany-mongodb /bin/bash -c "mongoimport -u cmdb -p ${MONGO_CMDB_PASSWORD} --db cmdb --drop --collection model_info < /opt/cmdb-init/model_info.json"

    shell_log "======MongoDB Initialize End======"
}

# SaaS Deploy
saas_deploy(){
    cd $CDIR
    cd ../../opsany-saas/
    /bin/cp *.tar.gz ../opsany-paas/saas/
    cd $CDIR
    cd ../saas/ && ls *.tar.gz
    if [ $? -ne 0 ];then
        echo "Please Download SAAS first" && exit
    fi
    python3 deploy.py --domain $DOMAIN_NAME --username admin --password ${ADMIN_PASSWORD} --file_name rbac-opsany-*.tar.gz
    python3 deploy.py --domain $DOMAIN_NAME --username admin --password ${ADMIN_PASSWORD} --file_name workbench-opsany-*.tar.gz
    python3 deploy.py --domain $DOMAIN_NAME --username admin --password ${ADMIN_PASSWORD} --file_name cmdb-opsany-*.tar.gz
    python3 deploy.py --domain $DOMAIN_NAME --username admin --password ${ADMIN_PASSWORD} --file_name control-opsany-*.tar.gz
    python3 deploy.py --domain $DOMAIN_NAME --username admin --password ${ADMIN_PASSWORD} --file_name job-opsany-*.tar.gz
    python3 deploy.py --domain $DOMAIN_NAME --username admin --password ${ADMIN_PASSWORD} --file_name cmp-opsany-*.tar.gz
    python3 deploy.py --domain $DOMAIN_NAME --username admin --password ${ADMIN_PASSWORD} --file_name bastion-opsany-*.tar.gz
    python3 deploy.py --domain $DOMAIN_NAME --username admin --password ${ADMIN_PASSWORD} --file_name dashboard-opsany-*.tar.gz
    
    python3 sync-user-script.py --domain https://${DOMAIN_NAME} --paas_username admin --paas_password ${ADMIN_PASSWORD} --app_code workbench cmdb control job cmp bastion dashboard
    shell_log "======OpsAny Data Initialize======"

    # OpsAny Database Init
    docker exec -e OPS_ANY_ENV=production \
        opsany-proxy /bin/sh -c "/usr/local/bin/python3 /opt/opsany-proxy/manage.py makemigrations && /usr/local/bin/python3 /opt/opsany-proxy/manage.py migrate"

    # Create Proxy Token
    PROXY_TOKEN=$(docker exec -e OPS_ANY_ENV=production \
            opsany-proxy /bin/sh -c " /usr/local/bin/python3 /opt/opsany-proxy/manage.py create_access" | grep 'Access' | awk -F ': ' '{print $2}' | awk -F '.' '{print $1}')

    python3 init-ce-base.py --domain $DOMAIN_NAME --private_ip $LOCAL_IP --paas_username admin --paas_password ${ADMIN_PASSWORD} --grafana_password admin --grafana_change_password $GRAFANA_ADMIN_PASSWORD --proxy_url https://${PROXY_LOCAL_IP}:8011 --proxy_public_url https://${PROXY_PUBLIC_IP}:8011 --proxy_token $PROXY_TOKEN

    # Init Script Job
    cd $CDIR/init/
    python3 import_script.py --domain https://${DOMAIN_NAME} --paas_username admin --paas_password ${ADMIN_PASSWORD} \
--target_type script --target_path ./job-script

    python3 import_script.py --domain https://$DOMAIN_NAME --paas_username admin --paas_password ${ADMIN_PASSWORD} \
--target_type task --target_path ./job-task

    

    chmod +x /etc/rc.d/rc.local
    echo "sleep 60 && /bin/bash ${INSTALL_PATH}/saas-restart.sh" >> /etc/rc.d/rc.local
    shell_warning_log "======OpsAny: Make Ops Perfect======"

    
}

admin_password_init(){
    PRESTR='Ops'
    STR=`head /dev/urandom | tr -dc A-Za-z0-9 | head -c 5`
    NUM=`echo $RANDOM`
    ADMIN_PASSWORD=$PRESTR$STR$NUM
    echo "ADMIN_PASSWORD=$ADMIN_PASSWORD" > ${INSTALL_PATH}/conf/.passwd_env
    cd ${CDIR}
    python3 password-init.py --paas_domain https://$DOMAIN_NAME --username admin --password admin --new_password $ADMIN_PASSWORD
    shell_warning_log "Login admin password: $ADMIN_PASSWORD"

   
}

# Main
main(){
    case "$1" in
	install)
        install_init
        mysql_init
        mongodb_init
        proxy_install
        saas_deploy
        admin_password_init
		;;
	help|*)
		echo $"Usage: $0 {install|help}"
	        ;;
    esac
}

main $1
