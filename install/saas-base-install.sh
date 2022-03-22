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

# Add ENV For SaaS
pip3 install requests==2.25.1 grafana-api==1.0.3 mysql-connector==2.2.9 SQLAlchemy==1.4.22 \
             -i http://mirrors.aliyun.com/pypi/simple/ \
             --trusted-host mirrors.aliyun.com
cd ../saas/
python3 add_env.py
cp invscript.py ${INSTALL_PATH}/uploads/
sed -i "s/LOCALHOST/${MYSQL_SERVER_IP}/g" ${INSTALL_PATH}/uploads/invscript.py
sed -i "s/CONTROL_PASSWORD/${MYSQL_OPSANY_CONTROL_PASSWORD}/g" ${INSTALL_PATH}/uploads/invscript.py
chmod +x ${INSTALL_PATH}/uploads/invscript.py

# Shell Log Record
shell_log(){
    LOG_INFO=$1
    echo "----------------$CTIME ${SHELL_NAME} : ${LOG_INFO}----------------"
    echo "$CTIME ${SHELL_NAME} : ${LOG_INFO}" >> ${SHELL_LOG}
}

# Start SaltStack 
saltstack_install(){
    shell_log "======Start SaltStack======"
    docker run --restart=always --name opsany-saltstack -d \
        -p 4505:4505 -p 4506:4506 -p 8005:8005 \
        -v ${INSTALL_PATH}/logs:${INSTALL_PATH}/logs \
        -v ${INSTALL_PATH}/salt-volume/certs/:/etc/pki/tls/certs/ \
        -v ${INSTALL_PATH}/salt-volume/etc/salt/:/etc/salt/ \
        -v ${INSTALL_PATH}/salt-volume/etc/salt/master.d:/etc/salt/master.d \
        -v ${INSTALL_PATH}/salt-volume/cache/:/var/cache/salt/ \
        -v ${INSTALL_PATH}/salt-volume/srv/salt:/srv/salt/ \
        -v ${INSTALL_PATH}/salt-volume/srv/pillar:/srv/pillar/ \
        -v ${INSTALL_PATH}/uploads:/opt/opsany/uploads \
        -v /etc/localtime:/etc/localtime:ro \
        ${PAAS_DOCKER_REG}/opsany-saltstack:v3.2.6
    shell_log "======Waiting for SaltStack ...======"
    sleep 20
    docker exec opsany-saltstack salt-key -A -y
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
}

# MonogDB Initialize
mongodb_init(){
    shell_log "======MongoDB Initialize======"
    sed -i "s/MONGO_WORKBENCH_PASSWORD/${MONGO_WORKBENCH_PASSWORD}/g" ./init/mongodb-init/mongodb_init.js
    sed -i "s/MONGO_CMDB_PASSWORD/${MONGO_CMDB_PASSWORD}/g" ./init/mongodb-init/mongodb_init.js
    sed -i "s/MONGO_JOB_PASSWORD/${MONGO_JOB_PASSWORD}/g" ./init/mongodb-init/mongodb_init.js
    sed -i "s/MONGO_DEVOPS_PASSWORD/${MONGO_DEVOPS_PASSWORD}/g" ./init/mongodb-init/mongodb_init.js
    sed -i "s/MONGO_CMP_PASSWORD/${MONGO_CMP_PASSWORD}/g" ./init/mongodb-init/mongodb_init.js
    sed -i "s/MONGO_MONITOR_PASSWORD/${MONGO_MONITOR_PASSWORD}/g" ./init/mongodb-init/mongodb_init.js
    sed -i "s/MONGO_AUTO_PASSWORD/${MONGO_AUTO_PASSWORD}/g" ./init/mongodb-init/mongodb_init.js
    sed -i "s/MONGO_EVENT_PASSWORD/${MONGO_EVENT_PASSWORD}/g" ./init/mongodb-init/mongodb_init.js
    
    docker cp init/mongodb-init/mongodb_init.js opsany-mongodb:/opt/
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
    python3 deploy.py --domain $DOMAIN_NAME --username admin --password admin --file_name rbac-opsany-*.tar.gz
    python3 deploy.py --domain $DOMAIN_NAME --username admin --password admin --file_name workbench-opsany-*.tar.gz
    python3 deploy.py --domain $DOMAIN_NAME --username admin --password admin --file_name cmdb-opsany-*.tar.gz
    python3 deploy.py --domain $DOMAIN_NAME --username admin --password admin --file_name control-opsany-*.tar.gz
    python3 deploy.py --domain $DOMAIN_NAME --username admin --password admin --file_name job-opsany-*.tar.gz
    python3 deploy.py --domain $DOMAIN_NAME --username admin --password admin --file_name cmp-opsany-*.tar.gz
    #python3 deploy.py --domain $DOMAIN_NAME --username admin --password admin --file_name devops-opsany-*.tar.gz
    python3 deploy.py --domain $DOMAIN_NAME --username admin --password admin --file_name bastion-opsany-*.tar.gz
    shell_log "======OpsAny Data Initialize======"
    python3 init-ce-base.py --domain $DOMAIN_NAME --private_ip $LOCAL_IP --paas_username admin --paas_password admin --zabbix_api_password $ZABBIX_API_PASSWORD
    chmod +x /etc/rc.d/rc.local
    echo "sleep 60 && /bin/bash ${INSTALL_PATH}/saas-restart.sh" >> /etc/rc.d/rc.local
    shell_log "======OpsAny: Make Ops Perfect======"

}

# Main
main(){
    mysql_init
    mongodb_init
    saltstack_install
    saas_deploy
}

main
