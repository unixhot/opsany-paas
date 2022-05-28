#!/bin/bash

uninstall_paas(){
    grep '^[A-Z]' install.config > install.env
    source ./install.env && rm -f install.env
    docker stop $(docker ps -qa)
    docker rm -f $(docker ps -qa)
    docker volume rm $(docker volume ls -q)
    rm -rf ${INSTALL_PATH}
    echo "===Manually remove the configuration content from /etc/rc.local======"
}


# Main
main(){
    case "$1" in
	uninstall)
        uninstall_paas
		;;
	help|*)
		echo $"Usage: $0 {uninstall|help}"
	        ;;
    esac
}

main $1

