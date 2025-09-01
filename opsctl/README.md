OpsAny's command-line tool

# 项目介绍

opsctl是OpsAny的命令行工具，用于操作OpsAny的资源。支持获取OpsAny的资源平台的资源。

## 1. 安装

```
cd /opt/opsany-paas/opsctl/
python3 -m pip install opsanyctl --break-system-packages
```

## 2. 配置

```
# 1. 获取配置模板
opsctl config

# 2. 在用户家目录创建文件
mkdir /root/.opsanyctl/

# 3. 创建配置文件
vim /root/.opsanyctl/config
apiVersion: v1
apiService:
  url: https://www.domian.com   #修改为平台地址
  bk_app_code: cmdb   #修改为cmdb
  bk_app_secret: bk_app_secret  #修改为cmdb的secret_key(开发中心获取https://DOMAIN/saas/cmdb/info/)
  bk_username: admin   #修改为平台用户名admin
config:
  resourceIdDefaultField: "code,VISIBLE_NAME,name"  # 默认搜索三个字段, 指定 code 或者 name 可以保证查询到的数据唯一
  resourceIdFieldSearch: false  # 默认关闭 RESOURCE_ID 字段 支持 fields=value方式精准字段获取资源
  resourceDefaultLimit: 20  # 资源默认每页数量
  apiResourcesDefaultLimit: 100  # 资源模型默认每页数量
resourceShort: # 可以根据配置修改指定模型的短名称，默认是模型的唯一标识。
  host: SERVER  # 物理机
  vs: VIRTUAL_SERVER  # 虚拟机
  cs: CLOUD_SERVER  # 云主机
  idc: IDC  # 机房
  reg: REGION  # 区域
  rack: RACK  # 机柜
  pub: PUBLIC_CLOUD  # 公有云账号
  pubreg: CLOUD_REGION  # 区域
  pubza: CLOUD_AZ  # 可用区
  buss: BUSINESS  # 业务
  app: APPLICATION  # 应用
  svc: SERVICE  # 服务
```

## 3. 使用
```
# 获取到当前支持的资源类型
opsctl api-resources
# 获取云主机数据
opsctl get CLOUD_SERVER
# 获取 云主机 第一页数据 每页5条
opsctl get CLOUD_SERVER -p 1 -l 5
```
