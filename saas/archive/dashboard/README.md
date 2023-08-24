# OpsAny可视化平台

OpsAny可视化平台为在原有的大屏展示的基础上，将Grafana的页面进行了嵌入，方便用户可以直接使用Grafana来进行自定义大屏，内置的大屏为定制开发，不能自动生成。

本文档适合1.6.0之前版本的用户一键部署和添加可视化平台。

1. 引用PaaS配置文件

```
cd /opt/opsany-paas/install
grep '^[A-Z]' install.config > install.env
source ./install.env && rm -f install.env
```

2. 部署Dashboard

> 执行前请修改dashboard-install.sh 设置PaaS平台的Admin密码，默认从安装路径获取自动生成的密码，数据库密码根据情况修改。

```
cd /opt/opsany-paas/saas/dashboard
sed -i "s/MYSQL_HOST_SED/${MYSQL_SERVER_IP}/g" dashboard.config
./dashboard-install.sh install
```

