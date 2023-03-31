#!/bin/bash
#******************************************
# Author:       Jason Zhao
# Email:        zhaoshundong@opsany.com
# Organization: OpsAny https://www.opsany.com/
# Description:  OpsAny PaaSAgent for Develop Install Script
#******************************************

# Get Data/Time
CTIME=$(date "+%Y-%m-%d-%H-%M")

# Shell Envionment Variables
CDIR=$(pwd)
SHELL_NAME="dev-install.sh"
SHELL_LOG="${CDIR}/${SHELL_NAME}.log"
ADMIN_PASSWORD=""

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
    echo -e "\033[31m---------------- $CTIME ${SHELL_NAME} : ${LOG_INFO} ----------------\033[0m"
    echo "$CTIME ${SHELL_NAME} : ${LOG_INFO}" >> ${SHELL_LOG}
}

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

# Check Install requirement
install_check(){
  shell_warning_log "The beginning is the first step to success"
  if [ -f /etc/redhat-release ];then
      setenforce 0
  fi
  DOCKER_PID=$(ps aux | grep '/usr/bin/containerd' | grep -v 'grep' | wc -l)
  if [ ${DOCKER_PID} -lt 1 ];then
      shell_error_log "Please install and start docker first!!!"
      exit
  fi
}

paas_agent_add(){
    shell_log "Register paas-agent Service"
    cd $CDIR && cd ../saas/
    resp=$(python3 engine-server-script.py --domain https://${DOMAIN_NAME} --paas_username admin --paas_password ${ADMIN_PASSWORD} --server_ip $LOCAL_IP  --server_port 4244 --app_port 8084 --server_cate tapp --type add)
    token=$(jq -r .data.token <<<"$resp" 2>/dev/null)
    sid=$(jq -r .data.s_id <<<"$resp" 2>/dev/null)
    server_id=$(jq -r .data.server_id <<<"$resp" 2>/dev/null)
    if [[ -z "$token" || -z "$sid" ]]; then
        shell_log "Register Faild：$resp"
    else
        shell_log "Register Succeed"
    fi
}

# Start PaasAgent
paas_agent_start(){
    # 修改PaasAgent配置文件
    cd $CDIR
    mkdir -p ${INSTALL_PATH}/paas_agent_test
    /bin/cp -r ../install/conf/paas_agent/paasagent.conf ${INSTALL_PATH}/paas_agent_test/paasagent.conf
    /bin/cp -r ../install/conf/paas_agent/paas_agent_config.yaml ${INSTALL_PATH}/paas_agent_test/paas_agent_config.yaml
    sed -i "s/BK_PAASAGENT_SID/$sid/g" ${INSTALL_PATH}/paas_agent_test/paas_agent_config.yaml
    sed -i "s/BK_PAASAGENT_TOKEN/$token/g" ${INSTALL_PATH}/paas_agent_test/paas_agent_config.yaml
    sed -i "s/LOCAL_IP/${LOCAL_IP}/g" ${INSTALL_PATH}/paas_agent_test/paas_agent_config.yaml
    
    shell_log "Start paas-agent Test"
    docker run -d --restart=always --name opsany-paas-paasagent-test \
    -p 4244:4245 -p 8084:8085 \
    -v ${INSTALL_PATH}/logs:/opt/opsany/logs/ \
    -v ${INSTALL_PATH}/paas_agent_test/paas_agent_config.yaml:/opt/opsany/paas-agent/etc/paas_agent_config.yaml \
    -v ${INSTALL_PATH}/paas_agent_test/paasagent.conf:/etc/nginx/conf.d/paasagent.conf \
    -v ${INSTALL_PATH}/uploads:/opt/opsany/uploads \
    -v ${INSTALL_PATH}/paas_agent_test/apps:/opt/opsany/paas-agent/apps \
    -v ${INSTALL_PATH}/paas_agent_test/saasapp:/opt/opsany/paas-agent/saasapp \
    -v /etc/localtime:/etc/localtime:ro \
    ${PAAS_DOCKER_REG}/opsany-paas-paasagent:v3.2.7
    
    sleep 10
    
    # PaasAgent healthz
    BIND_ADDR=${LOCAL_IP}
    PAASAGENT_SERVER_PORT=4244
    code=$(curl -s -o /dev/null -w "%{http_code}" http://$BIND_ADDR:$PAASAGENT_SERVER_PORT/healthz )
    if [[ $code != 200 ]]; then
        shell_error_log "paasagent test Start Faild，Check (http://$BIND_ADDR:$PAASAGENT_SERVER_PORT/healthz) Error" >&2
        exit 1
    fi
    
     shell_log "Activate paas-agent"
    # Activate PaasAgent
     cd $CDIR && cd ../saas/
     python3 engine-server-script.py --domain https://${DOMAIN_NAME} --paas_username admin --paas_password ${ADMIN_PASSWORD} --server_id $server_id --type active
}
    

# Main
main(){
    case "$1" in
	install)
          install_check
          paas_agent_add
          paas_agent_start
	  ;;
	help|*)
		echo $"Usage: $0 {install|help}"
	        ;;
    esac
}

main $1
