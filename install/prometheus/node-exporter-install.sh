#!/bin/bash
#******************************************
# Author:       Jason Zhao
# Email:        zhaoshundong@opsany.com
# Organization: https://www.opsany.com/
# Description:  Node Exporter Install Script
#******************************************
#Data/Time
CTIME=$(date "+%Y-%m-%d-%H-%M")

#Shell ENV
SHELL_NAME="node-exporter.sh"
SHELL_LOG="/usr/local/node-exporter.install.log"

#Log Record
shell_log(){
  LOG_INFO=$1
  echo "----------------$CTIME ${SHELL_NAME} : ${LOG_INFO}----------------"
  echo "$CTIME ${SHELL_NAME} : ${LOG_INFO}" >> ${SHELL_LOG}
}

# OS Type
OS_ARCH=$(LANG=C && lscpu | grep Architecture | awk -F ' ' '{print $2}')

if [ -f /etc/redhat-release ];then
    OS_TYPE="CENTOS"
    CENTOS6=$(cat /proc/version | grep 'el6')
    CENTOS7=$(cat /proc/version | grep 'el7')
    CENTOS8=$(cat /proc/version | grep 'el8')
    if [ -n "$CENTOS6" ];then
        OS_VER=6
    elif [ -n "$CENTOS7" ];then
        OS_VER=7
    elif [ -n "$CENTOS8" ];then
        OS_VER=8
    fi
elif [ -f /etc/lsb-release ];then
    OS_TYPE=$(grep "DISTRIB_ID=" /etc/lsb-release | awk -F'=' '{print $2}')
    OS_VER=$(grep "DISTRIB_RELEASE" /etc/lsb-release | awk -F'=' {'print$2'})
    OS=${OS_TYPE}_${OS_VER}

elif [ -f /etc/os-release ];then
    OS_TYPE=$(grep -E "^NAME=" /etc/os-release | awk -F'=' '{print $2}')
    OS_VER=$(grep -E "^VERSION_ID=" /etc/os-release | awk -F'=' '{print $2}')
    OS=${OS_TYPE}_${OS_VER}
else
    shell_log "This OS is not supported!"
fi

SUPPORT_OS_VER=("Ubuntu_14.04" \
                "Ubuntu_16.04" \
                "Ubuntu_18.04" \
                "Ubuntu_20.04" \
                "CentOS_6" \
                "CentOS_7" \
                "CentOS_8" \
                   )

shell_log "OS: $OS_TYPE $OS_VER"

node_exporter_install(){
    shell_log "Begin Install Node Exporter"
    # Install Node Exporter

    cd /usr/local/src
    curl --insecure -o /usr/local/node_exporter-1.1.2.linux-amd64.tar.gz  ${PAAS_URL}/uploads/agent/node-exporter/node_exporter-1.1.2.linux-amd64.tar.gz
    #wget https://github.com/prometheus/node_exporter/releases/download/v1.1.2/node_exporter-1.1.2.linux-amd64.tar.gz
    cd /usr/local/ && tar zxf node_exporter-1.1.2.linux-amd64.tar.gz
    ln -s /usr/local/node_exporter-1.1.2.linux-amd64/ /usr/local/node_exporter

    if id -u "prometheus" >/dev/null 2>&1; then
      echo "user exists, continue..."
    else
      echo "user does not exist, add prometheus..."
      useradd prometheus
    fi

    if [ "$OS_TYPE" == "CENTOS" -a "$OS_VER" -eq 6 -o "$OS" == "Ubuntu_14.04" ];then

      curl --insecure -o /etc/init.d/node_exporter  ${PAAS_URL}/uploads/agent/node-exporter/node_exporter.init.d.script
      chmod +x /etc/init.d/node_exporter
      /etc/init.d/node_exporter start
      if [ $? -eq 0 ];then
          shell_log "Node Exporter Install Succeed"
          chkconfig --add node_exporter
          return 0
      else
          shell_log "Node Exporter Install Failure"
      fi

    elif [ "$OS_TYPE" == "CENTOS" -o "$OS" == "Ubuntu_16.04" -o "$OS" == "Ubuntu_18.04" -o "$OS" == "Ubuntu_20.04" ];then

      cat > /usr/lib/systemd/system/node_exporter.service<<EOF
[Unit]
Description=node_exporter
After=network.target
[Service]
Type=simple
User=prometheus
ExecStart=/usr/local/node_exporter/node_exporter
Restart=on-failure
[Install]
WantedBy=multi-user.target
EOF

      systemctl enable --now node_exporter

      systemctl restart node_exporter
      if [ $? -eq 0 ];then
          shell_log "Node Exporter Install Succeed"
          return 0
      else
          shell_log "Node Exporter Install Failure"
      fi
   fi

}

node_exporter_remove(){
    if [ "$OS_TYPE" == "CENTOS" -a "$OS_VER" -eq 6 ];then
        service node_exporter stop
        rm -f /usr/local/node_exporter
    elif [ "$OS_TYPE" == "CENTOS" -a "$OS_VER" -eq 7 ];then
        systemctl stop node_exporter
        rm -f /usr/local/node_exporter
        rm -f /usr/lib/systemd/system/node_exporter.service
    elif [ "$OS_TYPE" == "CENTOS" -a "$OS_VER" -eq 8 ];then
        systemctl stop node_exporter
        rm -f /usr/local/node_exporter
        rm -f /usr/lib/systemd/system/node_exporter.service
    elif [ "$OS" == "Ubuntu_14.04" ];then
        /etc/init.d/node_exporter stop
        rm -f /usr/local/node_exporter
        rm -f /usr/lib/systemd/system/node_exporter.service
    elif [ "$OS" == "Ubuntu_16.04" ];then
        systemctl stop node_exporter
        rm -f /usr/local/node_exporter
        rm -f /usr/lib/systemd/system/node_exporter.service
    elif [ "$OS" == "Ubuntu_18.04" -o "$OS" == "Ubuntu_20.04" ];then
        systemctl stop node-exporter
        rm -f /usr/local/node_exporter
        rm -f /usr/lib/systemd/system/node_exporter.service
    fi
}

#Usage
usage(){
    echo "Usage: $0 [install|restart|start|stop|remove]  paas_url"
}

main(){
    PAAS_URL=$2
    case $1 in
        install)
            node_exporter_install;
           # install_clean;
            ;;
        update)
            node_exporter_update;
            ;;
        remove)
            node_exporter_remove;
            ;;
        *)
            usage;
    esac
}

#Main $1: command, $2: Control Server IP, $3: Minion ID $4: PAAS_URL
main $1 $2

