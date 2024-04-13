# 安装目录介绍

install是OpsAny社区版的安装脚本存放目录，安装脚本会进行系统初始化，并使用Docker启动所有服务。

## 安装脚本介绍

- paas-install.sh：用来安装PaaS平台，注意，仅安装PaaS平台，没有任何运维应用平台。

- saas-base-install.sh：用来安装OpsAny社区版，除了监控外的所有平台。

- saas-monitor-install.sh：用来安装OpsAny社区版的监控平台，因为监控平台依赖ElasticSearch等服务，需要部署主机至少具有8G内存。

- uninstall.sh：卸载脚本，注意：会删除掉本机的所有容器，所以OpsAny部署需要一个干净的独立的主机。

## 目录介绍

- conf：部署需要的配置文件存放位置

- init：部署时需要的初始化数据目录。

- uploads：此目录存放离线官方文档，和平台图片和图标等，部署时会移动到安装目录下，存放用户上传的数据。

- opsany-xxx：所有以“opsany-”开头的目录是各个服务Docker镜像的构建目录，官方使用的镜像，均使用目录下的Dockerfile进行构建。如果需要部署在ARM CPU的主机上，需要重新构建镜像。

## 国产信创支持

如果您需要部署在国产化的主机和操作系统上，请联系我们进行商业支持。
