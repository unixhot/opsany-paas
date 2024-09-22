# StackStorm in Docker Compose

1. 准备安装包 

```
cd /opt/opsany-paas/install/opsany-ce/
cp -r opsany-st2/ /opt/opsany/
cd /opt/opsany/opsany-st2/
```

2. 安装docker-compose
```
yum install -y docker-compose
```

3. 配置st2

可以使用OpsAny已经部署的RabbitMQ、Redis和MongoDB，请修改为正确的地址和用户名与密码。

```
vim files/st2.docker.conf

# 修改以下配置，可以配置为OpsAny的RabbitMQ
[messaging]
url = amqp://opsany:OpsAny@2020@127.0.0.1:5672/

# 修改以下配置，可以配置为OpsAny的Redis，注意Redis密码不要带@
[coordination]
url = redis://:123456.coM@127.0.0.1:6379

#增加下面配置，默认没有。
[database]
host = 127.0.0.1
port = 27017
db_name = event
username = event
password = OpsAny@2020
```

4. 启动ST2

```shell
export ST2_VERSION="3.8.0"
export ST2_IMAGE_REPO="registry.cn-beijing.aliyuncs.com/opsany/"
export ST2_EXPOSE_HTTP="0.0.0.0:8005"
docker-compose up -d
```

5. 测试st2

```shell
cd /opt/opsany/opsany-st2/
docker-compose exec st2client bash  # this gives you access to the st2 command line
```

6. 访问ST2
Open http://localhost:8005

默认帐号： st2admin/OpsAny@2023


### 进行初始化


1. 下载OpsAny核心st2的Pack。

> 需在安装stackstorm的服务器上面执行以下命令。切记。

```
mkdir -p /opt/stackstorm-packs && cd /opt/stackstorm-packs
git clone https://gitee.com/opsany/opsany_core.git
git clone https://gitee.com/opsany/opsany_workflow.git
```

2. 执行初始化
   
> 需在安装OpsAny的服务器上执行以下命令。请修改对应的地址和密码,用户名不要修改。

```
cd /opt/opsany-paas/saas/
INSTALL_PATH=/data/opsany/
DEVOPS_SECRET_KEY=$(cat ${INSTALL_PATH}/conf/.devops_secret_key)
python3 init-ce-st2.py --domain https://www.opsany.com --username admin  --password PASSWORD --st2_url https://www.opsany.com:8005  --st2_username st2admin --st2_password ST2_PASSWORD --app_code devops --app_secret ${DEVOPS_SECRET_KEY} --st2_core_pack_source gitee
[SUCCESS] init devops st2 success.
Downloading the OpsAny core package is expected to take 60 seconds...
[SUCCESS] init st2 pack success.
[SUCCESS] config core pack success.
```
