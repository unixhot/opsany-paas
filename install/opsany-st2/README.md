# StackStorm in Docker Compose

## 部署ST2

1. 配置ST2

请根据实际情况修改Redis、RabbitMQ、MongoDB配置。

```
vim files/st2.docker.conf
[messaging]
url = amqp://opsany:OpsAny@2020@192.168.56.11:5672

[database]
host = 192.168.56.11
port = 27017
db_name = event
username = event
password = OpsAny@2020

[coordination]
url = redis://:OpsAny2020@192.168.56.11:6379
```

2. 启动ST2

- 安装docker-compose

```
# yum install -y docker-compose
```

- 启动ST2

```shell
export ST2_VERSION="3.8.0"
export ST2_IMAGE_REPO="registry.cn-beijing.aliyuncs.com/opsany/"
export ST2_EXPOSE_HTTP="0.0.0.0:8005"
docker-compose up -d
```

3. 测试st2

```shell
cd /opt/opsany/opsany-st2/
docker-compose exec st2client bash  # this gives you access to the st2 command line
```

3. 访问ST2
Open http://localhost:8005

默认帐号： st2admin/OpsAny@2023

## ST2 日常管理

- 获取ST2 API Key

```shell
cd /opt/opsany/opsany-st2/
docker-compose exec st2client st2 login st2admin -p OpsAny@2023
docker-compose exec st2client st2 apikey create -k -m '{"used_by": "OpsAny"}'
```

- 关闭ST2 

```shell
cd /opt/opsany/opsany-st2/
docker-compose down
```


- 直接运行ST2命令

```shell
cd /opt/opsany/opsany-st2/
docker-compose exec st2client st2 <st2 command>
```

- 进入容器运行ST2命令

```shell
cd /opt/opsany/opsany-st2/
docker exec -it opsanyst2_st2client_1 /bin/bash
```

## Pack Configuration

Pack configs will be in `/opt/stackstorm/configs/$PACKNAME`, which is a docker volume shared between st2api, st2actionrunner, and st2sensorcontainer. You can use the `st2 pack config <packname>` in the st2client container in order to configure a pack.

### Use st2 pack config

```shell
$ docker-compose exec st2client st2 pack config git
repositories[0].url: https://github.com/StackStorm/st2-dockerfiles.git
repositories[0].branch [master]:
~~~ Would you like to add another item to  "repositories" array / list? [y]: n
---
Do you want to preview the config in an editor before saving? [y]: n
---
Do you want me to save it? [y]: y
+----------+--------------------------------------------------------------+
| Property | Value                                                        |
+----------+--------------------------------------------------------------+
| id       | 5eb3164f566aa824ea88f536                                     |
| pack     | git                                                          |
| values   | {                                                            |
|          |     "repositories": [                                        |
|          |         {                                                    |
|          |             "url":                                           |
|          | "https://github.com/StackStorm/st2-dockerfiles.git",         |
|          |             "branch": "master"                               |
|          |         }                                                    |
|          |     ]                                                        |
|          | }                                                            |
+----------+--------------------------------------------------------------+
```

### Copy a config file into a container

First, find the actual container name of st2api by running `docker-compose ps st2api`.

```shell
$ docker-compose ps st2api
      Name                    Command               State    Ports
--------------------------------------------------------------------
compose_st2api_1   /opt/stackstorm/st2/bin/st ...   Up      9101/tcp
```

Next, use `docker cp` to copy your file into place.

```shell
docker cp git.yaml compose_st2api_1:/opt/stackstorm/configs/git.yaml
```

## Register the pack config

If you used `docker cp` to copy the config in, you will need to manually load that configuration. The st2client service does not need access to the configs directory, as it will talk to st2api.

```shell
$ docker-compose exec st2client st2 run packs.load packs=git register=configs
.
id: 5eb3171c566aa824ea88f538
action.ref: packs.load
context.user: st2admin
parameters:
  packs:
  - git
  register: configs
status: succeeded
start_timestamp: Wed, 06 May 2020 19:59:24 UTC
end_timestamp: Wed, 06 May 2020 19:59:25 UTC
result:
  exit_code: 0
  result:
    configs: 1
  stdout: ''
```
