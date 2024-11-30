#!/bin/bash
#******************************************
# Author:       Jason Zhao
# Email:        zhaoshundong@opsany.com
# Organization: https://www.opsany.com/
# Description:  Zabbix Agent Install Script
#******************************************
#Data/Time
CTIME=$(date "+%Y-%m-%d-%H-%M")

#Shell ENV
SHELL_NAME="zabbix-agent.sh"
SHELL_LOG="/var/log/zabbix-agent.log"

#Log Record
shell_log(){
  LOG_INFO=$1
  echo "----------------$CTIME ${SHELL_NAME} : ${LOG_INFO}----------------"
  echo "$CTIME ${SHELL_NAME} : ${LOG_INFO}" >> ${SHELL_LOG}
}

# OS Suprrort
os_support(){
    declare -A linux_distros=(
        ["Ubuntu"]="18.04, 20.04, 22.04, 24.04 )"
        ["Debian"]="10 (Buster), 11 (Bullseye), 12 (Bookworm)"
        ["CentOS"]="7, 8, 9"
        ["Rocky Linux"]="8, 9"
        ["Alma Linux"]="8, 9"
        ["openSUSE"]="15.3, 15.4"
        ["RHEL"]="7, 8, 9"
    )

    echo "OS Support："
    for distro in "${!linux_distros[@]}"; do
        echo "$distro: ${linux_distros[$distro]}"
    done
}


# OS ARCH
OS_ARCH=$(LANG=C && lscpu | grep Architecture | awk -F ' ' '{print $2}')

# OS Type
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS_VERSION=$VERSION_ID
    OS_ID=$ID
    OS="${OS_ID}"_"${OS_VERSION}"
else
    OS_VERSION=$(uname -r)
    OS_ID="Unknown"
    shell_log "This OS is not supported!"
    os_supprort
fi

# Install Zabbix Agent
zabbix_agent_install(){
    #ubuntu 18.04
    if [ "$OS" == "ubuntu_18.04" ];then
        shell_log "Begin Install Agent OS: $OS_ID $OS_VERSION"
	    if [ "$OS_ARCH" == "x86_64" ];then 
	        curl --insecure -o /usr/local/zabbix-agent_5.0.44-1+bionic_amd64.deb ${PROXY_URL}/uploads/agent/zabbix-agent/ubuntu/zabbix-agent_5.0.44-1+bionic_amd64.deb
            dpkg -i /usr/local/zabbix-agent_5.0.44-1+bionic_amd64.deb
        elif [ "$OS_ARCH" == "x86" ];then
            curl --insecure -o /usr/local/zabbix-agent_5.0.44-1+bionic_i386.deb ${PROXY_URL}/uploads/agent/zabbix-agent/ubuntu/zabbix-agent_5.0.44-1+bionic_i386.deb
            dpkg -i /usr/local/zabbix-agent_5.0.44-1+bionic_i386.deb
        else
            shell_log "This OS Arch "$OS_ARCH" is not supported!"
        fi  
        sed -i "s#Server=127.0.0.1#Server=$ZABBIX_SERVER,172.17.0.0/16#g" /etc/zabbix/zabbix_agentd.conf
        sed -i "s#ServerActive=127.0.0.1#ServerActive=$ZABBIX_SERVER#g" /etc/zabbix/zabbix_agentd.conf
        sed -i "s#Hostname=Zabbix server#Hostname=$AGENT_HOSTNAME#g" /etc/zabbix/zabbix_agentd.conf
        systemctl enable zabbix-agent
        systemctl restart zabbix-agent
        if [ $? -eq 0 ];then
            shell_log "Zabbix Agent Install Succeed"
            return 0
        else
            shell_log "Zabbix Agent Install Failure"
        fi
    
    #ubuntu 20.04
    elif [ "$OS" == "ubuntu_20.04" ];then
        shell_log "Begin Install Agent OS: $OS_ID $OS_VERSION"
	    if [ "$OS_ARCH" == "x86_64" ];then
            curl --insecure -o /usr/local/zabbix-agent_5.0.44-1+focal_amd64.deb ${PROXY_URL}/uploads/agent/zabbix-agent/ubuntu/zabbix-agent_5.0.44-1+focal_amd64.deb
            dpkg -i /usr/local/zabbix-agent_5.0.44-1+focal_amd64.deb
        elif [ "$OS_ARCH" == "aarch64" ];then
            curl --insecure -o /usr/local/zabbix-agent_5.0.44-1+ubuntu20.04_arm64.deb ${PROXY_URL}/uploads/agent/zabbix-agent/ubuntu/zabbix-agent_5.0.44-1+ubuntu20.04_arm64.deb
            dpkg -i /usr/local/zabbix-agent_5.0.44-1+ubuntu20.04_arm64.deb
        else
            shell_log "This OS Arch "$OS_ARCH" is not supported!"
	    fi
        sed -i "s#Server=127.0.0.1#Server=$ZABBIX_SERVER,172.17.0.0/16#g" /etc/zabbix/zabbix_agentd.conf
        sed -i "s#ServerActive=127.0.0.1#ServerActive=$ZABBIX_SERVER#g" /etc/zabbix/zabbix_agentd.conf
        sed -i "s/Hostname=Zabbix server/Hostname=$AGENT_HOSTNAME/g" /etc/zabbix/zabbix_agentd.conf
        systemctl enable zabbix-agent
        systemctl restart zabbix-agent
        if [ $? -eq 0 ];then
            shell_log "Zabbix Agent Install Succeed"
            return 0
        else
            shell_log "Zabbix Agent Install Failure"
        fi

    # ubutnu 22.04
    elif [ "$OS" == "ubuntu_22.04" ];then
        shell_log "Begin Install Agent OS: $OS_ID $OS_VERSION"
	    if [ "$OS_ARCH" == "x86_64" ];then
            curl --insecure -o /usr/local/zabbix-agent_6.0.35-1+ubuntu22.04_amd64.deb ${PROXY_URL}/uploads/agent/zabbix-agent/ubuntu/zabbix-agent_6.0.35-1+ubuntu22.04_amd64.deb
            dpkg -i /usr/local/zabbix-agent_6.0.35-1+ubuntu22.04_amd64.deb
        elif [ "$OS_ARCH" == "aarch64" ];then
            curl --insecure -o /usr/local/zabbix-agent_6.0.35-1+ubuntu22.04_arm64.deb ${PROXY_URL}/uploads/agent/zabbix-agent/ubuntu/zabbix-agent_6.0.35-1+ubuntu22.04_arm64.deb
            dpkg -i /usr/local/zabbix-agent_6.0.35-1+ubuntu22.04_arm64.deb
        else
            shell_log "This OS Arch "$OS_ARCH" is not supported!"
        fi
        sed -i "s#Server=127.0.0.1#Server=$ZABBIX_SERVER,172.17.0.0/16#g" /etc/zabbix/zabbix_agentd.conf
        sed -i "s#ServerActive=127.0.0.1#ServerActive=$ZABBIX_SERVER#g" /etc/zabbix/zabbix_agentd.conf
        sed -i "s/Hostname=Zabbix server/Hostname=$AGENT_HOSTNAME/g" /etc/zabbix/zabbix_agentd.conf
        systemctl enable zabbix-agent
        systemctl restart zabbix-agent
        if [ $? -eq 0 ];then
            shell_log "Zabbix Agent2 Install Succeed"
            return 0
        else
            shell_log "Zabbix Agent2 Install Failure"
        fi
    
    # ubuntu 24.04
    elif [ "$OS" == "ubuntu_24.04" ];then
        shell_log "Begin Install Agent OS: $OS_ID $OS_VERSION"
	    if [ "$OS_ARCH" == "x86_64" ];then
            curl --insecure -o /usr/local/zabbix-agent_6.0.35-1+ubuntu24.04_amd64.deb ${PROXY_URL}/uploads/agent/zabbix-agent/ubuntu/zabbix-agent_6.0.35-1+ubuntu24.04_amd64.deb
            dpkg -i /usr/local/zabbix-agent_6.0.35-1+ubuntu24.04_amd64.deb
        elif [ "$OS_ARCH" == "aarch64" ];then
            curl --insecure -o /usr/local/zabbix-agent_6.0.35-1+ubuntu24.04_arm64.deb ${PROXY_URL}/uploads/agent/zabbix-agent/ubuntu/zabbix-agent_6.0.35-1+ubuntu24.04_arm64.deb
            dpkg -i /usr/local/zabbix-agent_6.0.35-1+ubuntu24.04_arm64.deb
        else
            shell_log "This OS Arch "$OS_ARCH" is not supported!"
        fi
        sed -i "s#Server=127.0.0.1#Server=$ZABBIX_SERVER,172.17.0.0/16#g" /etc/zabbix/zabbix_agentd.conf
        sed -i "s#ServerActive=127.0.0.1#ServerActive=$ZABBIX_SERVER#g" /etc/zabbix/zabbix_agentd.conf
        sed -i "s/Hostname=Zabbix server/Hostname=$AGENT_HOSTNAME/g" /etc/zabbix/zabbix_agentd.conf
        systemctl enable zabbix-agent
        systemctl restart zabbix-agent
        if [ $? -eq 0 ];then
            shell_log "Zabbix Agent2 Install Succeed"
            return 0
        else
            shell_log "Zabbix Agent2 Install Failure"
        fi
    
    # rocky 8
    elif [ "$OS" == "rocky_8.4" -o "$OS" == "rocky_8.5" ];then
        shell_log "Begin Install Agent OS: $OS_ID $OS_VERSION"
	    if [ "$OS_ARCH" == "x86_64" ];then
            curl --insecure -o /usr/local/zabbix-agent-7.0.5-release1.el8.x86_64.rpm ${PROXY_URL}/uploads/agent/zabbix-agent/rocky/zabbix-agent-7.0.5-release1.el8.x86_64.rpm
            rpm -ivh /usr/local/zabbix-agent-7.0.5-release1.el8.x86_64.rpm
        elif [ "$OS_ARCH" == "aarch64" ];then
            curl --insecure -o /usr/local/zabbix-agent-7.0.5-release1.el8.aarch64.rpm ${PROXY_URL}/uploads/agent/zabbix-agent/rocky/zabbix-agent-7.0.5-release1.el8.aarch64.rpm
            rpm -ivh /usr/local/zabbix-agent-7.0.5-release1.el8.aarch64.rpm
        else
            shell_log "This OS Arch "$OS_ARCH" is not supported!"
        fi
        sed -i "s#Server=127.0.0.1#Server=$ZABBIX_SERVER,172.17.0.0/16#g" /etc/zabbix/zabbix_agentd.conf
        sed -i "s#ServerActive=127.0.0.1#ServerActive=$ZABBIX_SERVER#g" /etc/zabbix/zabbix_agentd.conf
        sed -i "s/Hostname=Zabbix server/Hostname=$AGENT_HOSTNAME/g" /etc/zabbix/zabbix_agentd.conf
        systemctl enable zabbix-agent
        systemctl restart zabbix-agent
        if [ $? -eq 0 ];then
            shell_log "Zabbix Agent Install Succeed"
            return 0
        else
            shell_log "Zabbix Agent Install Failure"
        fi
    
    # rocky 9.0
    elif [ "$OS" == "rocky_9.0" ];then
        shell_log "Begin Install Agent OS: $OS_ID $OS_VERSION"
	    if [ "$OS_ARCH" == "x86_64" ];then
            curl --insecure -o /usr/local/zabbix-agent-7.0.5-release1.el9.x86_64.rpm ${PROXY_URL}/uploads/agent/zabbix-agent/rocky/zabbix-agent-7.0.5-release1.el9.x86_64.rpm
            rpm -ivh /usr/local/zabbix-agent-7.0.5-release1.el9.x86_64.rpm
        elif [ "$OS_ARCH" == "aarch64" ];then
            curl --insecure -o /usr/local/zabbix-agent-7.0.5-release1.el9.aarch64.rpm ${PROXY_URL}/uploads/agent/zabbix-agent/rocky/zabbix-agent-7.0.5-release1.el9.aarch64.rpm
            rpm -ivh /usr/local/zabbix-agent-7.0.5-release1.el9.aarch64.rpm
        else
            shell_log "This OS Arch "$OS_ARCH" is not supported!"
        fi
        sed -i "s#Server=127.0.0.1#Server=$ZABBIX_SERVER,172.17.0.0/16#g" /etc/zabbix/zabbix_agentd.conf
        sed -i "s#ServerActive=127.0.0.1#ServerActive=$ZABBIX_SERVER#g" /etc/zabbix/zabbix_agentd.conf
        sed -i "s/Hostname=Zabbix server/Hostname=$AGENT_HOSTNAME/g" /etc/zabbix/zabbix_agentd.conf
        systemctl enable zabbix-agent
        systemctl restart zabbix-agent
        if [ $? -eq 0 ];then
            shell_log "Zabbix Agent Install Succeed"
            return 0
        else
            shell_log "Zabbix Agent Install Failure"
        fi

    # almalinux 8
    elif [ "$OS" == "almalinux_8.3" -o "$OS" == "almalinux_8.4" ];then
        shell_log "Begin Install Agent OS: $OS_ID $OS_VERSION"
	    if [ "$OS_ARCH" == "x86_64" ];then
            curl --insecure -o /usr/local/zabbix-agent-7.0.5-release1.el8.x86_64.rpm ${PROXY_URL}/uploads/agent/zabbix-agent/almalinux/zabbix-agent-7.0.5-release1.el8.x86_64.rpm
            rpm -ivh /usr/local/zabbix-agent-7.0.5-release1.el8.x86_64.rpm
        elif [ "$OS_ARCH" == "aarch64" ];then
            curl --insecure -o /usr/local/zabbix-agent-7.0.5-release1.el8.aarch64.rpm ${PROXY_URL}/uploads/agent/zabbix-agent/almalinux/zabbix-agent-7.0.5-release1.el8.aarch64.rpm
            rpm -ivh /usr/local/zabbix-agent-7.0.5-release1.el8.aarch64.rpm
        else
            shell_log "This OS Arch "$OS_ARCH" is not supported!"
        fi
        sed -i "s#Server=127.0.0.1#Server=$ZABBIX_SERVER,172.17.0.0/16#g" /etc/zabbix/zabbix_agentd.conf
        sed -i "s#ServerActive=127.0.0.1#ServerActive=$ZABBIX_SERVER#g" /etc/zabbix/zabbix_agentd.conf
        sed -i "s/Hostname=Zabbix server/Hostname=$AGENT_HOSTNAME/g" /etc/zabbix/zabbix_agentd.conf
        systemctl enable zabbix-agent
        systemctl restart zabbix-agent
        if [ $? -eq 0 ];then
            shell_log "Zabbix Agent Install Succeed"
            return 0
        else
            shell_log "Zabbix Agent Install Failure"
        fi
    
    # alma 9.0
    elif [ "$OS" == "almalinux_9.0" ];then
        shell_log "Begin Install Agent OS: $OS_ID $OS_VERSION"
	    if [ "$OS_ARCH" == "x86_64" ];then
            curl --insecure -o /usr/local/zabbix-agent-7.0.5-release1.el9.x86_64.rpm ${PROXY_URL}/uploads/agent/zabbix-agent/almalinux/zabbix-agent-7.0.5-release1.el9.x86_64.rpm
            rpm -ivh /usr/local/zabbix-agent-7.0.5-release1.el9.x86_64.rpm
        elif [ "$OS_ARCH" == "aarch64" ];then
            curl --insecure -o /usr/local/zabbix-agent-7.0.5-release1.el9.aarch64.rpm ${PROXY_URL}/uploads/agent/zabbix-agent/almalinux/zabbix-agent-7.0.5-release1.el9.aarch64.rpm
            rpm -ivh /usr/local/zabbix-agent-7.0.5-release1.el9.aarch64.rpm
        else
            shell_log "This OS Arch "$OS_ARCH" is not supported!"
        fi
        sed -i "s#Server=127.0.0.1#Server=$ZABBIX_SERVER,172.17.0.0/16#g" /etc/zabbix/zabbix_agentd.conf
        sed -i "s#ServerActive=127.0.0.1#ServerActive=$ZABBIX_SERVER#g" /etc/zabbix/zabbix_agentd.conf
        sed -i "s/Hostname=Zabbix server/Hostname=$AGENT_HOSTNAME/g" /etc/zabbix/zabbix_agentd.conf
        systemctl enable zabbix-agent
        systemctl restart zabbix-agent
        if [ $? -eq 0 ];then
            shell_log "Zabbix Agent Install Succeed"
            return 0
        else
            shell_log "Zabbix Agent Install Failure"
        fi

    # debian 12
    elif [ "$OS" == "debian_12" ];then
        shell_log "Begin Install Agent OS: $OS_ID $OS_VERSION"
	curl --insecure -o /usr/local/zabbix-release_5.0-2+debian11_all.deb ${PROXY_URL}/uploads/agent/zabbix-agent/zabbix-release_5.0-2+debian11_all.deb
        dpkg -i /usr/local/zabbix-release_5.0-2+debian11_all.deb && apt install -y zabbix-agent2
        sed -i "s#Server=127.0.0.1#Server=$ZABBIX_SERVER,172.17.0.0/16#g" /etc/zabbix/zabbix_agentd.conf
        sed -i "s#ServerActive=127.0.0.1#ServerActive=$ZABBIX_SERVER#g" /etc/zabbix/zabbix_agentd.conf
        sed -i "s/Hostname=Zabbix server/Hostname=$AGENT_HOSTNAME/g" /etc/zabbix/zabbix_agentd.conf
        systemctl restart zabbix-agent2
        if [ $? -eq 0 ];then
            shell_log "Zabbix Agent2 Install Succeed"
            return 0
        else
            shell_log "Zabbix Agent2 Install Failure"
        fi
    
    # centos 6
    elif [ "$OS" == "CENTOS_6" ];then
        shell_log "Begin Install Agent OS: $OS_ID $OS_VERSION"
	rpm -ivh ${PROXY_URL}/uploads/agent/zabbix-agent/zabbix-agent2-5.0.42-1.el6.x86_64.rpm
        sed -i "s#Server=127.0.0.1#Server=$ZABBIX_SERVER,172.17.0.0/16#g" /etc/zabbix/zabbix_agent2.conf
        sed -i "s#ServerActive=127.0.0.1#ServerActive=$ZABBIX_SERVER#g" /etc/zabbix/zabbix_agent2.conf
        sed -i "s/Hostname=Zabbix server/Hostname=$AGENT_HOSTNAME/g" /etc/zabbix/zabbix_agent2.conf
	service zabbix-agent2 restart
        if [ $? -eq 0 ];then
            shell_log "Zabbix Agent2 Install Succeed"
            return 0
        else
            shell_log "Zabbix Agent2 Install Failure"
        fi    
    
    # centos 7
    elif [ "$OS" == "centos_7" -o "$OS" == "euleros_2.0" ];then
        shell_log "Begin Install Agent OS: $OS_ID $OS_VERSION"
	    if [ "$OS_ARCH" == "x86_64" ];then
            curl --insecure -o /usr/local/zabbix-agent-5.0.44-1.el7.x86_64.rpm ${PROXY_URL}/uploads/agent/zabbix-agent/centos/zabbix-agent-5.0.44-1.el7.x86_64.rpm
            rpm -ivh /usr/local/zabbix-agent-5.0.44-1.el7.x86_64.rpm
        else
            shell_log "This OS Arch "$OS_ARCH" is not supported!"
        fi
        sed -i "s#Server=127.0.0.1#Server=$ZABBIX_SERVER,172.17.0.0/16#g" /etc/zabbix/zabbix_agentd.conf
        sed -i "s#ServerActive=127.0.0.1#ServerActive=$ZABBIX_SERVER#g" /etc/zabbix/zabbix_agentd.conf
        sed -i "s/Hostname=Zabbix server/Hostname=$AGENT_HOSTNAME/g" /etc/zabbix/zabbix_agentd.conf
        systemctl enable zabbix-agent
        systemctl restart zabbix-agent
        if [ $? -eq 0 ];then
            shell_log "Zabbix Agent Install Succeed"
            return 0
        else
            shell_log "Zabbix Agent Install Failure"
        fi
    
    # centos 8
    elif [ "$OS" == "centos_8" ];then
        shell_log "Begin Install Agent OS: $OS_ID $OS_VERSION"
	    if [ "$OS_ARCH" == "x86_64" ];then
            curl --insecure -o /usr/local/zabbix-agent-6.0.35-release1.el8.x86_64.rpm ${PROXY_URL}/uploads/agent/zabbix-agent/centos/zabbix-agent-6.0.35-release1.el8.x86_64.rpm
            rpm -ivh /usr/local/zabbix-agent-6.0.35-release1.el8.x86_64.rpm
        elif [ "$OS_ARCH" == "aarch64" ];then
            curl --insecure -o /usr/local/zabbix-agent-6.0.35-release1.el8.aarch64.rpm ${PROXY_URL}/uploads/agent/zabbix-agent/centos/zabbix-agent-6.0.35-release1.el8.aarch64.rpm
            rpm -ivh /usr/local/zabbix-agent-6.0.35-release1.el8.aarch64.rpm
        else
            shell_log "This OS Arch "$OS_ARCH" is not supported!"
        fi
        sed -i "s#Server=127.0.0.1#Server=$ZABBIX_SERVER,172.17.0.0/16#g" /etc/zabbix/zabbix_agentd.conf
        sed -i "s#ServerActive=127.0.0.1#ServerActive=$ZABBIX_SERVER#g" /etc/zabbix/zabbix_agentd.conf
        sed -i "s/Hostname=Zabbix server/Hostname=$AGENT_HOSTNAME/g" /etc/zabbix/zabbix_agentd.conf
        systemctl enable zabbix-agent
        systemctl restart zabbix-agent
        if [ $? -eq 0 ];then
            shell_log "Zabbix Agent Install Succeed"
            return 0
        else
            shell_log "Zabbix Agent Install Failure"
        fi
    # centos9
    elif [ "$OS" == "centos_9" ];then
        shell_log "Begin Install Agent OS: $OS_ID $OS_VERSION"
	    if [ "$OS_ARCH" == "x86_64" ];then
            curl --insecure -o /usr/local/zabbix-agent-6.0.35-release1.el9.x86_64.rpm ${PROXY_URL}/uploads/agent/zabbix-agent/centos/zabbix-agent-6.0.35-release1.el9.x86_64.rpm
            rpm -ivh /usr/local/zabbix-agent-6.0.35-release1.el9.x86_64.rpm
        elif [ "$OS_ARCH" == "aarch64" ];then
            curl --insecure -o /usr/local/zabbix-agent-6.0.35-release1.el9.aarch64.rpm ${PROXY_URL}/uploads/agent/zabbix-agent/centos/zabbix-agent-6.0.35-release1.el9.aarch64.rpm
            rpm -ivh /usr/local/zabbix-agent-6.0.35-release1.el9.aarch64.rpm
        else
            shell_log "This OS Arch "$OS_ARCH" is not supported!"
        fi
        sed -i "s#Server=127.0.0.1#Server=$ZABBIX_SERVER,172.17.0.0/16#g" /etc/zabbix/zabbix_agentd.conf
        sed -i "s#ServerActive=127.0.0.1#ServerActive=$ZABBIX_SERVER#g" /etc/zabbix/zabbix_agentd.conf
        sed -i "s/Hostname=Zabbix server/Hostname=$AGENT_HOSTNAME/g" /etc/zabbix/zabbix_agentd.conf
        systemctl enable zabbix-agent
        systemctl restart zabbix-agent
        if [ $? -eq 0 ];then
            shell_log "Zabbix Agent Install Succeed"
            return 0
        else
            shell_log "Zabbix Agent Install Failure"
        fi

    # openEuler 20.03
    elif [ "$OS" == "openEuler_20.03" ];then
        shell_log "Begin Install Agent OS: $OS_ID $OS_VERSION"
	    if [ "$OS_ARCH" == "x86_64" ];then
            curl --insecure -o /usr/local/zabbix-agent-7.0.5-release1.el8.x86_64.rpm ${PROXY_URL}/uploads/agent/zabbix-agent/openEuler/zabbix-agent-7.0.5-release1.el8.x86_64.rpm
            rpm -ivh /usr/local/zabbix-agent-7.0.5-release1.el8.x86_64.rpm
        elif [ "$OS_ARCH" == "aarch64" ];then
            curl --insecure -o /usr/local/zabbix-agent-7.0.5-release1.el8.aarch64.rpm ${PROXY_URL}/uploads/agent/zabbix-agent/openEuler/zabbix-agent-7.0.5-release1.el8.aarch64.rpm
            rpm -ivh /usr/local/zabbix-agent-7.0.5-release1.el8.aarch64.rpm
        else
            shell_log "This OS Arch "$OS_ARCH" is not supported!"
        fi
        sed -i "s#Server=127.0.0.1#Server=$ZABBIX_SERVER,172.17.0.0/16#g" /etc/zabbix/zabbix_agentd.conf
        sed -i "s#ServerActive=127.0.0.1#ServerActive=$ZABBIX_SERVER#g" /etc/zabbix/zabbix_agentd.conf
        sed -i "s/Hostname=Zabbix server/Hostname=$AGENT_HOSTNAME/g" /etc/zabbix/zabbix_agentd.conf
        systemctl enable zabbix-agent
        systemctl restart zabbix-agent
        if [ $? -eq 0 ];then
            shell_log "Zabbix Agent Install Succeed"
            return 0
        else
            shell_log "Zabbix Agent Install Failure"
        fi
    # openEuler 22.03
    elif [ "$OS" == "openEuler_22.03" ];then
        shell_log "Begin Install Agent OS: $OS_ID $OS_VERSION"
	    if [ "$OS_ARCH" == "x86_64" ];then
            curl --insecure -o /usr/local/zabbix-agent-7.0.5-release1.el9.x86_64.rpm ${PROXY_URL}/uploads/agent/zabbix-agent/openEuler/zabbix-agent-7.0.5-release1.el9.x86_64.rpm
            rpm -ivh /usr/local/zabbix-agent-7.0.5-release1.el9.x86_64.rpm
        elif [ "$OS_ARCH" == "aarch64" ];then
            curl --insecure -o /usr/local/zabbix-agent-7.0.5-release1.el8.aarch64.rpm ${PROXY_URL}/uploads/agent/zabbix-agent/openEuler/zabbix-agent-7.0.5-release1.el8.aarch64.rpm
            rpm -ivh /usr/local/zabbix-agent-7.0.5-release1.el8.aarch64.rpm
        else
            shell_log "This OS Arch "$OS_ARCH" is not supported!"
        fi
        sed -i "s#Server=127.0.0.1#Server=$ZABBIX_SERVER,172.17.0.0/16#g" /etc/zabbix/zabbix_agentd.conf
        sed -i "s#ServerActive=127.0.0.1#ServerActive=$ZABBIX_SERVER#g" /etc/zabbix/zabbix_agentd.conf
        sed -i "s/Hostname=Zabbix server/Hostname=$AGENT_HOSTNAME/g" /etc/zabbix/zabbix_agentd.conf
        systemctl enable zabbix-agent
        systemctl restart zabbix-agent
        if [ $? -eq 0 ];then
            shell_log "Zabbix Agent Install Succeed"
            return 0
        else
            shell_log "Zabbix Agent Install Failure"
        fi
    else
	 shell_log "This OS -${OS}- is not support install"
    fi
}

zabbix_agent_remove(){
    if [ "$OS_ID" == "CENTOS" -a "$OS_VERSION" -eq 6 ];then
        service zabbix-agent2 stop
        yum remove -y zabbix-agent2
    elif [ "$OS_ID" == "CENTOS" -a "$OS_VERSION" -eq 7 ];then
        service zabbix-agent2 stop
        yum remove -y zabbix-agent2
    elif [ "$OS_ID" == "CENTOS" -a "$OS_VERSION" -eq 8 ];then
        service zabbix-agent2 stop
        yum remove -y zabbix-agent2
    elif [ "$OS" == "Ubuntu_14.04" ];then
        /etc/init.d/zabbix-agent stop
        apt-get remove zabbix-agent -y
    elif [ "$OS" == "Ubuntu_16.04" ];then
        systemctl stop zabbix-agent
        apt-get remove zabbix-agent -y 
    elif [ "$OS" == "Ubuntu_18.04" -o "$OS" == "Ubuntu_20.04" ];then
        systemctl stop zabbix-agent2
        apt-get remove zabbix-agent2 -y
    fi
}

#Usage
usage(){
    echo "Usage: $0 [install|restart|start|stop|remove] zabbix_server_ip minionid paas_url"
}

main(){
    ZABBIX_SERVER=$2
    AGENT_HOSTNAME=$3
    PROXY_URL=$4
    case $1 in
        install)
            zabbix_agent_install;
           # install_clean;
            ;;
        update)
            zabbix_agent_update;
            ;;
        remove)
            zabbix_agent_remove;
            ;;
        *)
            usage;
    esac
}

#Main $1: Command, $2: Zabbix Server IP, $3: HOSTNAME $4: PROXY_URL
main $1 $2 $3 $4
