#!/bin/bash
grep '^[A-Z]' install.config > install.env
source ./install.env && rm -f install.env

uninstall_proxy(){
    # Stop Proxy
    docker stop opsany-proxy-mysql
    docker stop opsany-proxy-redis
    docker stop opsany-proxy-guacd
    docker stop opsany-proxy-openresty
    docker stop opsany-proxy

    # Remove Proxy
    docker rm -f opsany-proxy-mysql
    docker rm -f opsany-proxy-redis
    docker rm -f opsany-proxy-guacd
    docker rm -f opsany-proxy-openresty
    docker rm -f opsany-proxy

    # Remove Install Path
    #rm -rf ${INSTALL_PATH}
}

# Main
main(){
    case "$1" in
	uninstall)
            uninstall_proxy
		;;
	help|*)
		echo $"Usage: $0 {uninstall|help}"
	        ;;
    esac
}

main $1
