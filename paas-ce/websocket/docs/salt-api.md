# SaltStack二次开发



## Salt API
  SaltStack提供了REST API，可以非常方便的将Salt与第三方系统进行集成。

### Salt API部署
创建Salt API执行用的用户
```
[root@dev-node1 ~]# useradd -M -s /sbin/nologin saltapi
[root@dev-node1 ~]# echo "saltapi" | passwd saltapi --stdin
#生成自签名证书, 过程中需要输入key密码及RDNs
[root@dev-node1 ~]# cd /etc/pki/tls/certs
[root@dev-node1 certs]# make testcert
#解密key文件，生成无密码的key文件, 过程中需要输入key密码，该密码为之前生成证书时设置的密码
[root@dev-node1 certs]# cd /etc/pki/tls/private/
[root@dev-node1 private]# openssl rsa -in localhost.key -out localhost_nopass.key
```

安装Salt API
```
[root@linux-node1 ~]# yum install -y salt-api
```

创建配置文件
```
[root@ops-node1 ~]# vim /etc/salt/master
default_include: master.d/*.conf  #将注释去掉
[root@ops-node1 ~]# vim /etc/salt/master.d/api.conf 
rest_cherrypy:
  host: 0.0.0.0
  port: 8011
  ssl_crt: /etc/pki/tls/certs/localhost.crt
  ssl_key: /etc/pki/tls/private/localhost_nopass.key

#可以同时使用两个的接口
[root@dev ~]# vim /etc/salt/master.d/tornado-api.conf
rest_tornado:
  port: 8012
  address: 0.0.0.0
  backlog: 128
  ssl_crt: /etc/pki/tls/certs/localhost.crt
  ssl_key: /etc/pki/tls/private/localhost_nopass.key
  debug: False
  disable_ssl: False
  webhook_disable_auth: False
  cors_origin: null

[root@ops-node1 ~]# vim /etc/salt/master.d/eauth.conf 
external_auth:
  pam:
    saltapi:
      - .*
      - '@wheel'
      - '@runner'
```

启动Salt API
```
[root@linux-node1 ~]# systemctl restart salt-master
[root@linux-node1 ~]# systemctl start salt-api
```

查看端口
```
[root@ops master.d]# netstat -ntlp | grep 8011
tcp        0      0 0.0.0.0:8011            0.0.0.0:*               LISTEN      14765/python        
[root@ops master.d]# netstat -ntlp | grep 8012
tcp        0      0 0.0.0.0:8012            0.0.0.0:*               LISTEN      14766/python        
```

### login接口
    login是学习salt-api的第一个方法，使用salt-api其它接口的时候，需要首先通过login接口通过认证来获取token，后期操作就不需要使用用户名和密码认证，使用token即可。
login例：
请求
```
[root@linux-node1 ~]# curl -sSk https://127.0.0.1:8011/login \
  -H "Accept: application/x-yaml" \
  -d username='saltapi' \
  -d password='123456.coM' \
  -d eauth='pam'
return:
- eauth: pam
  expire: 1488860776.622981
  perms:
  - .*
  - '@wheel'
  - '@runner'
  start: 1488817576.62298
  token: c0894cfa499f155250b35455d91a7832b6b99e1f
  user: saltapi
```

请记住返回结果中的token，我们会在后面的例子中使用，再次使用的时候可以通过X-Auth-Token这个HTTP的header来发送token给salt-api即可。


### 查询minions信息
用来将所有Minion的Grains获取到，然后写入数据库，作为资产管理的一部分，同时可以用于各种统计，如根据操作硬件型号、系统版本、CPU、内存生成不同用途的饼图。
```
curl -k https://127.0.0.1:8011/minions/liunx-node1.example.com \
-H "Accept: application/json" \
-H "X-Auth-Token: c0894cfa499f155250b35455d91a7832b6b99e1f "
```

### 运行Runner
获取当前所有minion的状态，用来在DashBoard上显示统计的饼图，总共管理多少客户端。当前Down状态的多少台，UP状态的多少台。
```
curl -k https://127.0.0.1:8000/  \
-H "Accept: application/json" \
-H "X-Auth-Token: 957e15e5683e5717b8a598be3017c3ac62734a43" \
-d client='runner' \
-d fun='manage.status'
```

### 远程执行模块
```
curl -k https://192.168.56.11:8000/ \
-H "Accept: application/x-yaml" \
-H "X-Auth-Token: 9fbf37c0ef0eff1432e4957e685a588fa6a4a581" \
-d client='local' \
-d tgt='*' \
-d fun='test.ping'
```

加参数
```
-d fun='pkg.install' \ 
-d arg='refresh=true \ 
-d arg='name=pkgName'
```

### Job管理
获取缓存的Job列表
```
curl -k https://127.0.0.1:8000/jobs \
-H "Accept: application/json" \
-H "X-Auth-Token: 957e15e5683e5717b8a598be3017c3ac62734a43"
```

查询指定的job
```
curl -k https://127.0.0.1:8000/jobs/ 20160508071355520184 \
-H "Accept: application/json" \
-H "X-Auth-Token: 957e15e5683e5717b8a598be3017c3ac62734a43"
```
### 执行wheel
查询所有key列表
```
curl -k https://localhost:8000/ \
     -H "Accept: application/x-yaml" \
     -H "X-Auth-Token: 957e15e5683e5717b8a598be3017c3ac62734a43" \
     -d client='wheel' \
     -d fun='key.list_all'
```

### 使用Targeting
如果想在api中使用salt的 Targeting 功能，可以在Request的Post Data中增加 expr_form (默认是 glob )及值即可:
```
curl -k https://127.0.0.1:8000/ \
     -H "Accept: application/x-yaml" \
     -H "X-Auth-Token: 957e15e5683e5717b8a598be3017c3ac62734a43" \
     -d client='local' \
     -d tgt='webcluster' \
     -d expr_form='nodegroup' \
     -d fun='test.ping'
```