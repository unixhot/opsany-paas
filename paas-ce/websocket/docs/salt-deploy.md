# SaltStack 部署

## 安装SaltStack
```
[root@linux-node1 ~]# yum install -y https://mirrors.aliyun.com/epel/epel-release-latest-7.noarch.rpm
[root@linux-node1 ~]# yum install -y https://mirrors.aliyun.com/saltstack/yum/redhat/salt-repo-latest-2.el7.noarch.rpm
[root@linux-node1 ~]# sed -i "s/repo.saltstack.com/mirrors.aliyun.com\/saltstack/g" /etc/yum.repos.d/salt-latest.repo
[root@linux-node1 ~]# yum install -y salt-ssh salt-master salt-minion
```

## 配置SaltStack

### 配置Salt Master

```
[root@ops ~]# vim /etc/salt/master
file_roots:
  base:
    - /srv/salt
[root@ops ~]# systemctl enable salt-master && systemctl start salt-master
```

### 配置Salt Minion

```
[root@ops ~]# vim /etc/salt/minion
master: 127.0.0.1
[root@ops ~]# systemctl enable salt-minion && systemctl start salt-minion
```

