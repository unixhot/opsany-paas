# OpsAny企业版部署

企业版部署支持主机容器部署和Kubernetes部署两种：

主机部署：

通常最少准备两台主机： 8C 16G内存、100G系统盘、200G数据盘。
  - 主机1: 部署OpsAny平台所有功能和Prometheus。
  - 主机2: 部署Elastic套件、Jenkins、Nexus、StackStorm等。

OpsAny企业版部署之前需要提前部署OpsAny社区版。企业版是在社区版的基础上增加相关企业版的平台和功能。

## 使用脚本部署企业版

### 平台部署

0. 安装前初始化

请将两台主机先设置好主机名和hosts解析，opsany-node1.example.com，域名可以参考客户提供的域名。主机名要求是完整的FQDN名。

1. 安装企业版SaaS

企业版请使用公司Gitlab的opsany-paas进行clone，不要使用对外的社区版。

```
#执行安装
cd /opt && git clone --depth=1 http://git.opsany.cn/opsany/opsany-paas.git
cd /opt/opsany-paas/install/opsany-ee/
cp ee-install.config.example ee-install.config

#修改配置文件中Elastic相关的IP地址。
vim ee-install.conf

source ./ee-install.config
./saas-ee-install.sh all
```

2. 安装Prometheus

```
cd /opt/opsany-paas/install/
./prom-install.sh install
```

3. 管控平台添加Prometheus集成

管控平台-采控管理-Prometheus集成。根据文档进行集成。

4. 部署StackStorm，事件中心依赖StackStorm才能工作。

st2-install.sh有两个参数：

- st2：适用于把StackStorm和OpsAny平台部署在相同的主机，复用OpsAny的MongoDB、Redis。
- all：适用于单独的主机部署StackStorm又和OpsAny的MongoDB、Redis由于网络等原因，不方便访问时，本地启动新的MongoDB和Redis。

不管选择哪个参数都会额外的安装RabbitMQ，StackStorm依靠RabbitMQ消息队列进行事件的处理。

```
cd /opt/opsany-paas/install/
./st2-install.sh st2
```

5. 开启APM代理
cd /opt/opsany-paas/install/opsany-ee/
./elastic-install.sh enable

### APM部署

通常将APM部署在单独的主机上，如果主机在32G左右，也可以选择部署到和OpsAny相同的主机上。

#### 1. 部署APM Server并配置集成。

> 注意，如果是多Proxy的架构，APM是需要部署在Proxy的主机上。如果企业版部署APM建议是单独的主机，需要将在node1上修改后的配置复制到安装APM的主机上。需要install.config和ee-install.conf

- 1.1 内置部署

```
# 在安装APM的主机上clone代码
cd /opt && git clone --depth=1 http://git.opsany.cn/opsany/opsany-paas.git

# 从配置模板生成配置文件
cd /data/opsany-paas/install/opsany-ee && cp ee-install.config.example ee-install.config

# 修改配置文件
vim /data/opsany-paas/install/opsany-ee/ee-install.config
# 请修改为apm server所在的主机地址
APM_SERVER_HOST="192.168.56.11"
ES_SERVER_IP="192.168.56.11"
KIBANA_CLUSTER="https://192.168.56.11:5601"

# 安装apm、kibana、heartbeat
cd /opt/opsany-paas/install/opsany-ee/
./elastic-install.sh all
```

#### 2. 配置 SSL、TLS 以及 HTTPS 来确保 Elasticsearch、Kibana、APM的安全性

默认脚本安装完成的Elasticsearch、Kibana、APM Server均为http。生产使用需要配置自签名证书的HTTPS。

- 2.1 为Elasticsearch启用TLS

```
# 进入到elasticsearch容器内
$ docker exec -it opsany-elastic-elasticsearch bash

# 签发ca证书，过程中需按两次回车键
$ ./bin/elasticsearch-certutil ca

# 用ca证书签发节点证书，过程中需按三次回车键
$ ./bin/elasticsearch-certutil cert --ca elastic-stack-ca.p12
$ chmod 755 elastic-certificates.p12
$ mv elastic-certificates.p12 config/

# 生成elasticsearch-ca.pem文件，供kibana、apm、heartbeat使用
$ openssl pkcs12 -in elastic-stack-ca.p12 -out elasticsearch-ca.pem -clcerts -nokeys

# 修改权限
$ chmod 755 elasticsearch-ca.pem

# 退出容器
$ exit

# 修改主配置文件：
$ vim /data/opsany/conf/elastic/elasticsearch.yml
cluster.name: docker-cluster
network.host: 0.0.0.0
xpack.security.authc.api_key.enabled: true
xpack.security.http.ssl.enabled: true
xpack.security.http.ssl.keystore.path: elastic-certificates.p12
xpack.security.http.ssl.truststore.path: elastic-certificates.p12

# 重启elasticsearch容器
$ docker restart opsany-elastic-elasticsearch
```

> 从浏览器访问 https://localhost:9200。
>
> 因为配置了安全协议，所以使用 https 协议进行访问，但由于证书是自己生成的，并不可靠，所以会有安全提示，忽略即可。

- 2.2 为Kibana启用TLS

```
# 为kibana生成证书文件，直接回车
$ docker exec -it opsany-elastic-elasticsearch bash
$ ./bin/elasticsearch-certutil csr -name kibana -dns localhost

# 解压文件
$ unzip csr-bundle.zip

# 生成crt文件
$ cd kibana
$ openssl x509 -req -in kibana.csr -signkey kibana.key -out kibana.crt -days 3650

# 退出容器Elasticsearch容器
exit;

# 将解压后的文件复制到kibana容器的config目录中
docker cp opsany-elastic-elasticsearch:/usr/share/elasticsearch/kibana/kibana.crt ./
docker cp opsany-elastic-elasticsearch:/usr/share/elasticsearch/kibana/kibana.key ./
docker cp opsany-elastic-elasticsearch:/usr/share/elasticsearch/elasticsearch-ca.pem ./
docker cp kibana.crt opsany-elastic-kibana:/usr/share/kibana/config/
docker cp kibana.key opsany-elastic-kibana:/usr/share/kibana/config/
docker cp elasticsearch-ca.pem opsany-elastic-kibana:/usr/share/kibana/config/

# 修改配置文件，注意协议修改为https
$ vim /data/opsany/conf/elastic/kibana.yml
server.port: 5601
server.host: "0.0.0.0"
i18n.locale: "zh-CN"
elasticsearch.hosts: ["https://127.0.0.1:9200"]    # 修改协议为https
elasticsearch.username: "opsany"
elasticsearch.password: "OpsAny@2020"
monitoring.ui.container.elasticsearch.enabled: true

# 填写以下内容，上面内容不变。
xpack.actions.allowedHosts: ["*"]
xpack.encryptedSavedObjects.encryptionKey: 14fe84924d8030d8514af69e01b0a1f5
xpack.reporting.encryptionKey: 9de357bfcb231efcb8b070319dbb1dee
xpack.security.encryptionKey: def40ed18c138ea10181103a0ae91e0a
elasticsearch.ssl.verificationMode: certificate
elasticsearch.ssl.certificateAuthorities: [ "/usr/share/kibana/config/elasticsearch-ca.pem" ]
server.ssl.enabled: true
server.ssl.certificate: /usr/share/kibana/config/kibana.crt
server.ssl.key: /usr/share/kibana/config/kibana.key

# 重启kibana容器
$ docker restart opsany-elastic-kibana
```

> 从浏览器访问 https://localhost:5601。

- 2.3 为APM启用TLS并配置Secret token

> Secret token是 授权对 APM 服务器的请求。 这样可以确保只有你的 Agent 才能将数据发送到你的 APM 服务器。 代理和 APM 服务器都必须配置相同的 Secret token，并且 Scecret token 仅在与 SSL/TLS 结合使用时才提供安全性。
>
> 要使用 Secret token 保护 APM 代理与 APM 服务器之间的通信安全：
>
> - 在 APM 服务器中启用 SSL/TLS
> - 在 Agent 和服务器中设置 Secret token
> - 在 APM agent 中启用 HTTPS

```
# 为apm生成证书
$ docker exec -it opsany-elastic-elasticsearch bash
$ ./bin/elasticsearch-certutil csr -name apm -dns localhost -out apm-csr-bundle.zip

# 解压文件
$ unzip apm-csr-bundle.zip

# 生成crt文件
$ cd apm
$ openssl x509 -req -in apm.csr -signkey apm.key -out apm.crt -days 3650

# 退出容器Elasticsearch容器
$ exit

# 将解压后的文件移动到apm容器的config目录中
docker cp opsany-elastic-elasticsearch:/usr/share/elasticsearch/apm/apm.crt ./
docker cp opsany-elastic-elasticsearch:/usr/share/elasticsearch/apm/apm.key ./
docker cp opsany-elastic-elasticsearch:/usr/share/elasticsearch/elasticsearch-ca.pem ./
docker cp apm.crt opsany-elastic-apm-server:/usr/share/apm-server/
docker cp apm.key opsany-elastic-apm-server:/usr/share/apm-server/
docker cp elasticsearch-ca.pem opsany-elastic-apm-server:/usr/share/apm-server/

# 修改配置文件，注意协议修改为https
$ vim /data/opsany/conf/elastic/apm-server.yml
apm-server:
  host: "0.0.0.0:8200"
output.elasticsearch:
  hosts: ["https://127.0.0.1:9200"]   # 修改协议为https
  auth:
    secret_token: "OpsAny@2020"
  username: "opsany"
  password: "OpsAny@2020"

#填写以下内容：注意缩进。下面ssl.开头的两行，前面有两个空格。
  ssl.verification_mode: none
  ssl.certificate_authorities: ["/usr/share/apm-server/elasticsearch-ca.pem"]
apm-server.ssl.enabled: true 
apm-server.ssl.key: "/usr/share/apm-server/apm.key"
apm-server.ssl.certificate: "/usr/share/apm-server/apm.crt"

# 启用RUM监控。
apm-server.rum.enabled: true
apm-server.auth.anonymous.rate_limit.event_limit: 300
apm-server.auth.anonymous.rate_limit.ip_limit: 1000

# 开启APM的验证后，由于前端没有SECRET_TOKEN参数，需要采用下面方式，允许接收对应的服务名称。*代表所有，不安全，待解决。
apm-server.auth.anonymous.allow_service: ['*']
apm-server.rum.allow_origins: ['*']

apm-server.rum.library_pattern: "node_modules|bower_components|~"
apm-server.rum.exclude_from_grouping: "^/webpack"
apm-server.rum.source_mapping.enabled: true
apm-server.rum.source_mapping.cache.expiration: 5m

# 重启apm server容器和saas应用
docker restart opsany-elastic-apm-server
```

> 在上面，我们打开了SSL/TLS，并设置Secret token 为 OpsAny@2020。


- 2.4 Heartbeat设置TLS

```
# 将证书复制到heartbeat容器中
docker cp elasticsearch-ca.pem opsany-elastic-heartbeat:/usr/share/heartbeat

# 编辑配置文件：

vim /data/opsany/conf/elastic/heartbeat.yml +110 
output.elasticsearch:
  hosts: ["127.0.0.1:9200"]
  protocol: "https"    # 打开此行注释
  username: "opsany"
  password: "OpsAny@2020"
  index: "heartbeat-%{[agent.version]}-%{+yyyy.MM}"
  # 增加下面两行内容。其它内容不变
  ssl.certificate_authorities: ["/usr/share/heartbeat/elasticsearch-ca.pem"]
  ssl.verification_mode: none
  
# 重启heartbeat容器
docker restart opsany-elastic-heartbeat
```

#### 3.添加APM Server集成

  从浏览器访问 http://localhost:5601，找到左侧导航-Management-集成，在浏览集成里面安装APM集成，点击最下面的启动。


#### 4.前端RUM监控配置

- 4.1 修改Nginx配置

因为浏览器默认会扫描https证书问题，前端vue接入apm会在证书上面卡住400，所以修改opsany-base-openresty容器的配置文件，添加代理服务器

```
# 修改下面的配置文件 /data/opsany/conf/nginx-conf.d/opsany_paas.conf 在最后面添加
location ~ ^/rum/ {
        rewrite ^/rum(/.*)$ $1 break;  # 移除路径中的 /rum 前缀
        proxy_pass https://127.0.0.1:8200;
        proxy_ssl_verify off;  # 忽略后端服务的自签名证书
    }
docker restart opsany-base-openresty
```

- 4.2 前端配置实例

```
Vue.use(ApmVuePlugin, {
    router,
    config: {
        serviceName: "test", //当前应用程序的名称
        serverUrl: "https://opsany-domain/rum/", //opsany运维平台域名
        environment: "dev", //当前应用程序的环境
        distributedTracingOrigins: ['https://front-domain'],  // 设置允许进行分布式追踪的后端域名
        disableInstrumentations: [],  // 保持默认值，不禁用XHR和Fetch，以监控所有API请求
        transactionSampleRate: 1.0 // 强制捕获所有事务
    }
});
```

> 至此，已成功配置Elasticsearch、Kibana和APM的SSL、TLS以及HTTPS访问。


### 独立Proxy部署

在独立的Proxy上是需要部署APM Server和Heartbeat。 

- 1. 修改配置文件

```
# 独立Proxy部署可能需要手工修改配置文件，设置ES地址。
/bin/cp -r /opt/opsany-paas/conf/elastic/ /opt/opsany/conf/
vim /opt/opsany/conf/elastic/vim /opt/opsany/conf/elastic/apm-server.yml
apm-server:
  host: "0.0.0.0:8200"
output.elasticsearch:
  hosts: ["http://192.168.56.13:9200"]
  username: "修改为ES的用户，注意不能使用elastic"
  password: "修改为ES密码"

vim /opt/opsany/conf/elastic/vim /opt/opsany/conf/elastic/heartbeat.yml
# ---------------------------- Elasticsearch Output ----------------------------
output.elasticsearch:
  # Array of hosts to connect to.
  hosts: ["192.168.56.13:9200"]

  # Protocol - either `http` (default) or `https`.
  #protocol: "https"

  # Authentication credentials - either API key or username/password.
  #api_key: "id:api_key"
  username: "修改为ES的用户，注意不能使用elastic"
  password: "修改为ES密码"
  index: "heartbeat-%{[agent.version]}-%{+yyyy.MM}"
```

- 2. 执行脚本启动APM和Heartbeat

```
cd /opt/opsany-paas/install/opsany-ee/
# 安装APM Server
./elastic-install.sh apm
# 安装Heartbeat 
./elastic-install.sh heartbeat
```

## 使用Kubernetes部署企业版

先根据官方文档部署完毕Kubernetes社区版。

0.执行脚本，生成配置文件，如果执行失败，请不要继续做任何操作。支持重复执行。重复执行时会有类似这样的报错：【Register Online SAAS ERROR, error info: 该应用已存在【 可以忽略

```
# 为各个SaaS生成配置文件
cd /opt/opsany-paas/install/opsany-ee/
./saas-ee-k8s-install.sh install
source ../install-k8s.config
```

生成的Helm目录：

```
root@k8s-node1:/data/opsany/kubernetes/helm/opsany-ee# ls -l
total 28
drwxr-xr-x 3 root root 4096 Nov  4 07:20 opsany-saas-apm
drwxr-xr-x 3 root root 4096 Nov  4 07:20 opsany-saas-auto
drwxr-xr-x 3 root root 4096 Nov  4 07:20 opsany-saas-event
drwxr-xr-x 3 root root 4096 Nov  4 07:20 opsany-saas-k8s
drwxr-xr-x 3 root root 4096 Nov  4 07:20 opsany-saas-kbase
drwxr-xr-x 3 root root 4096 Nov  4 07:20 opsany-saas-log
drwxr-xr-x 3 root root 4096 Nov  4 07:20 opsany-saas-prom
```


1.部署事件中心-event

```
# Step1: 使用Helm部署cmp服务。
$ helm install opsany-saas-event ${INSTALL_PATH}/kubernetes/helm/opsany-ee/opsany-saas-event/ -n opsany

# Step2: 等待到30-60秒后，查看event服务Pod状态是否为Running。
$ kubectl get pod -n opsany | grep "opsany-saas-event-"

# Step3: 执行数据库创建
EVENT_POD=$(kubectl get pod -n opsany | grep opsany-saas-event | awk '{print $1}')
kubectl exec $EVENT_POD -n opsany -- sh -c   "export BK_ENV="production" && python /opt/opsany/event/manage.py migrate --noinput && python /opt/opsany/event/manage.py createcachetable django_cache"

# Step4: 修改Openresty配置，开启cmp访问
cd ${INSTALL_PATH}/kubernetes/helm/opsany-paas/opsany-paas-openresty/
sed -i 's/127.0.0.1:7011/opsany-saas-event:7011/g' opsany_paas.conf
helm upgrade opsany-paas-openresty . -n opsany
OPENRESTY_POD=$(kubectl get pod -n opsany | grep opsany-paas-openresty | awk '{print $1}')
kubectl delete pod ${OPENRESTY_POD} -n opsany
kubectl get pod -n opsany | grep opsany-paas-openresty

# Step5: 从RBAC同步用户
cd /opt/opsany-paas/saas/
source ${INSTALL_PATH}/conf/.passwd_env
python3 sync-user-script.py --domain https://${DOMAIN_NAME} --paas_username admin --paas_password ${ADMIN_PASSWORD} --app_code event

# Step6: 测试访问，返回【HTTP/1.1 200 OK】为正常，其它状态码为异常。
EVENT_SVC=$(kubectl get svc -n opsany | grep 'opsany-saas-event' | awk -F ' ' '{print $3}')
curl --head http://${EVENT_SVC}:7011/o/event/healthz/
```

2.部署智能巡检-auto

```
# Step1: 使用Helm部署auto服务。
$ helm install opsany-saas-auto ${INSTALL_PATH}/kubernetes/helm/opsany-ee/opsany-saas-auto/ -n opsany

# Step2: 等待到30-60秒后，查看auto服务Pod状态是否为Running。
$ kubectl get pod -n opsany | grep "opsany-saas-auto-"

# Step3: 执行数据库创建
AUTO_POD=$(kubectl get pod -n opsany | grep opsany-saas-auto | awk '{print $1}')
kubectl exec $AUTO_POD -n opsany -- sh -c   "export BK_ENV="production" && python /opt/opsany/auto/manage.py migrate --noinput && python /opt/opsany/auto/manage.py createcachetable django_cache"

# Step4: 修改Openresty配置，开启auto访问
cd ${INSTALL_PATH}/kubernetes/helm/opsany-paas/opsany-paas-openresty/
sed -i 's/127.0.0.1:7012/opsany-saas-auto:7012/g' opsany_paas.conf
helm upgrade opsany-paas-openresty . -n opsany
OPENRESTY_POD=$(kubectl get pod -n opsany | grep opsany-paas-openresty | awk '{print $1}')
kubectl delete pod ${OPENRESTY_POD} -n opsany
kubectl get pod -n opsany | grep opsany-paas-openresty

# Step5: 从RBAC同步用户
cd /opt/opsany-paas/saas/
source ${INSTALL_PATH}/conf/.passwd_env
python3 sync-user-script.py --domain https://${DOMAIN_NAME} --paas_username admin --paas_password ${ADMIN_PASSWORD} --app_code auto

# Step6: 测试访问，返回【HTTP/1.1 200 OK】为正常，其它状态码为异常。
AUTO_SVC=$(kubectl get svc -n opsany | grep 'opsany-saas-auto' | awk -F ' ' '{print $3}')
curl --head http://${AUTO_SVC}:7012/o/auto/healthz/
```

3.部署知识库-kbase

```
# Step1: 使用Helm部署kbase服务。
$ helm install opsany-saas-kbase ${INSTALL_PATH}/kubernetes/helm/opsany-ee/opsany-saas-kbase/ -n opsany

# Step2: 等待到30-60秒后，查看kbase服务Pod状态是否为Running。
$ kubectl get pod -n opsany | grep "opsany-saas-kbase-"

# Step3: 执行数据库创建
KBASE_POD=$(kubectl get pod -n opsany | grep opsany-saas-kbase | awk '{print $1}')
kubectl exec $KBASE_POD -n opsany -- sh -c   "export BK_ENV="production" && python /opt/opsany/kbase/manage.py migrate --noinput && python /opt/opsany/kbase/manage.py createcachetable django_cache"

# Step4: 修改Openresty配置，开启kbase访问
cd ${INSTALL_PATH}/kubernetes/helm/opsany-paas/opsany-paas-openresty/
sed -i 's/127.0.0.1:7013/opsany-saas-kbase:7013/g' opsany_paas.conf
helm upgrade opsany-paas-openresty . -n opsany
OPENRESTY_POD=$(kubectl get pod -n opsany | grep opsany-paas-openresty | awk '{print $1}')
kubectl delete pod ${OPENRESTY_POD} -n opsany
kubectl get pod -n opsany | grep opsany-paas-openresty

# Step5: 从RBAC同步用户
cd /opt/opsany-paas/saas/
source ${INSTALL_PATH}/conf/.passwd_env
python3 sync-user-script.py --domain https://${DOMAIN_NAME} --paas_username admin --paas_password ${ADMIN_PASSWORD} --app_code kbase

# Step6: 测试访问，返回【HTTP/1.1 200 OK】为正常，其它状态码为异常。
KBASE_SVC=$(kubectl get svc -n opsany | grep 'opsany-saas-kbase' | awk -F ' ' '{print $3}')
curl --head http://${KBASE_SVC}:7013/o/kbase/healthz/
```

4.部署容器平台-k8s

```
# Step1: 使用Helm部署k8s服务。
$ helm install opsany-saas-k8s ${INSTALL_PATH}/kubernetes/helm/opsany-ee/opsany-saas-k8s/ -n opsany

# Step2: 等待到30-60秒后，查看k8s服务Pod状态是否为Running。
$ kubectl get pod -n opsany | grep "opsany-saas-k8s-"

# Step3: 执行数据库创建
K8S_POD=$(kubectl get pod -n opsany | grep opsany-saas-k8s | awk '{print $1}')
kubectl exec $K8S_POD -n opsany -- sh -c   "export BK_ENV="production" && python /opt/opsany/k8s/manage.py migrate --noinput && python /opt/opsany/k8s/manage.py createcachetable django_cache"

# Step4: 修改Openresty配置，开启k8s访问
cd ${INSTALL_PATH}/kubernetes/helm/opsany-paas/opsany-paas-openresty/
sed -i 's/127.0.0.1:7014/opsany-saas-k8s:7014/g' opsany_paas.conf
helm upgrade opsany-paas-openresty . -n opsany
OPENRESTY_POD=$(kubectl get pod -n opsany | grep opsany-paas-openresty | awk '{print $1}')
kubectl delete pod ${OPENRESTY_POD} -n opsany
kubectl get pod -n opsany | grep opsany-paas-openresty

# Step5: 从RBAC同步用户
cd /opt/opsany-paas/saas/
source ${INSTALL_PATH}/conf/.passwd_env
python3 sync-user-script.py --domain https://${DOMAIN_NAME} --paas_username admin --paas_password ${ADMIN_PASSWORD} --app_code k8s

# Step6: 测试访问，返回【HTTP/1.1 200 OK】为正常，其它状态码为异常。
K8S_SVC=$(kubectl get svc -n opsany | grep 'opsany-saas-k8s' | awk -F ' ' '{print $3}')
curl --head http://${K8S_SVC}:7014/o/k8s/healthz/
```

5.部署应用监控-prom

```
# Step1: 使用Helm部署prom服务。
$ helm install opsany-saas-prom ${INSTALL_PATH}/kubernetes/helm/opsany-ee/opsany-saas-prom/ -n opsany

# Step2: 等待到30-60秒后，查看prom服务Pod状态是否为Running。
$ kubectl get pod -n opsany | grep "opsany-saas-prom-"

# Step3: 执行数据库创建
PROM_POD=$(kubectl get pod -n opsany | grep opsany-saas-prom | awk '{print $1}')
kubectl exec $PROM_POD -n opsany -- sh -c   "export BK_ENV="production" && python /opt/opsany/prom/manage.py migrate --noinput && python /opt/opsany/prom/manage.py createcachetable django_cache"

# Step4: 修改Openresty配置，开启prom访问
cd ${INSTALL_PATH}/kubernetes/helm/opsany-paas/opsany-paas-openresty/
sed -i 's/127.0.0.1:7015/opsany-saas-prom:7015/g' opsany_paas.conf
helm upgrade opsany-paas-openresty . -n opsany
OPENRESTY_POD=$(kubectl get pod -n opsany | grep opsany-paas-openresty | awk '{print $1}')
kubectl delete pod ${OPENRESTY_POD} -n opsany
kubectl get pod -n opsany | grep opsany-paas-openresty

# Step5: 从RBAC同步用户
cd /opt/opsany-paas/saas/
source ${INSTALL_PATH}/conf/.passwd_env
python3 sync-user-script.py --domain https://${DOMAIN_NAME} --paas_username admin --paas_password ${ADMIN_PASSWORD} --app_code prom

# Step6: 测试访问，返回【HTTP/1.1 200 OK】为正常，其它状态码为异常。
PROM_SVC=$(kubectl get svc -n opsany | grep 'opsany-saas-prom' | awk -F ' ' '{print $3}')
curl --head http://${PROM_SVC}:7015/o/prom/healthz/
```

6.部署日志平台-log

```
# Step1: 使用Helm部署log服务。
$ helm install opsany-saas-log ${INSTALL_PATH}/kubernetes/helm/opsany-ee/opsany-saas-log/ -n opsany

# Step2: 等待到30-60秒后，查看log服务Pod状态是否为Running。
$ kubectl get pod -n opsany | grep "opsany-saas-log-"

# Step3: 执行数据库创建
LOG_POD=$(kubectl get pod -n opsany | grep opsany-saas-log | awk '{print $1}')
kubectl exec $LOG_POD -n opsany -- sh -c   "export BK_ENV="production" && python /opt/opsany/log/manage.py migrate --noinput && python /opt/opsany/log/manage.py createcachetable django_cache"

# Step4: 修改Openresty配置，开启log访问
cd ${INSTALL_PATH}/kubernetes/helm/opsany-paas/opsany-paas-openresty/
sed -i 's/127.0.0.1:7016/opsany-saas-log:7016/g' opsany_paas.conf
helm upgrade opsany-paas-openresty . -n opsany
OPENRESTY_POD=$(kubectl get pod -n opsany | grep opsany-paas-openresty | awk '{print $1}')
kubectl delete pod ${OPENRESTY_POD} -n opsany
kubectl get pod -n opsany | grep opsany-paas-openresty

# Step5: 从RBAC同步用户
cd /opt/opsany-paas/saas/
source ${INSTALL_PATH}/conf/.passwd_env
python3 sync-user-script.py --domain https://${DOMAIN_NAME} --paas_username admin --paas_password ${ADMIN_PASSWORD} --app_code log

# Step6: 测试访问，返回【HTTP/1.1 200 OK】为正常，其它状态码为异常。
LOG_SVC=$(kubectl get svc -n opsany | grep 'opsany-saas-log' | awk -F ' ' '{print $3}')
curl --head http://${LOG_SVC}:7016/o/log/healthz/
```

7.部署APM平台-apm

```
# Step1: 使用Helm部署apm服务。
$ helm install opsany-saas-apm ${INSTALL_PATH}/kubernetes/helm/opsany-ee/opsany-saas-apm/ -n opsany

# Step2: 等待到30-60秒后，查看apm服务Pod状态是否为Running。
$ kubectl get pod -n opsany | grep "opsany-saas-apm-"

# Step3: 执行数据库创建
APM_POD=$(kubectl get pod -n opsany | grep opsany-saas-apm | awk '{print $1}')
kubectl exec $APM_POD -n opsany -- sh -c   "export BK_ENV="production" && python /opt/opsany/apm/manage.py migrate --noinput && python /opt/opsany/apm/manage.py createcachetable django_cache"

# Step4: 修改Openresty配置，开启apm访问
cd ${INSTALL_PATH}/kubernetes/helm/opsany-paas/opsany-paas-openresty/
sed -i 's/127.0.0.1:7019/opsany-saas-apm:7019/g' opsany_paas.conf
helm upgrade opsany-paas-openresty . -n opsany
OPENRESTY_POD=$(kubectl get pod -n opsany | grep opsany-paas-openresty | awk '{print $1}')
kubectl delete pod ${OPENRESTY_POD} -n opsany
kubectl get pod -n opsany | grep opsany-paas-openresty

# Step5: 从RBAC同步用户
cd /opt/opsany-paas/saas/
source ${INSTALL_PATH}/conf/.passwd_env
python3 sync-user-script.py --domain https://${DOMAIN_NAME} --paas_username admin --paas_password ${ADMIN_PASSWORD} --app_code apm

# Step6: 测试访问，返回【HTTP/1.1 200 OK】为正常，其它状态码为异常。
APM_SVC=$(kubectl get svc -n opsany | grep 'opsany-saas-apm' | awk -F ' ' '{print $3}')
curl --head http://${APM_SVC}:7019/o/apm/healthz/
```

8.执行企业版初始化

```
cd /opt/opsany-paas/install/opsany-ee
./saas-ee-k8s-install.sh init
```

### 基本验证

- 管控平台-主机管理-纳管主机
- 管控平台-数据库管理-纳管数据库-MySQL和Redis
- 堡垒机-验证主机登录-验证MySQL登录
- 应用监控-验证监控
- APM平台-性能监控-验证微服务之间调用情况

待完善内容：

- 应用监控-告警规则-自动导入规则
- 管控平台-资产采集-自动导入采集插件
- 管控平台-指标采集-自动导入采集插件
- 应用监控-自动导入各种Grafana Dashboard

