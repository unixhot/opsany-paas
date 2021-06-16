## 自定义Grains

**编写Grains**

在minion配置文件中定义的grains是静态的，不能够动态的在minion上生成。可以用Python非常方便的写“动态”的grains。minion启动时，会执行grains包所带的模块及自定义grains模块中的公开函数，返回的结果就是grains。grains模块中的函数必须返回一个dict，其中key是grains的名字，value是值。
这里的“动态” grains 是指 minion 启动时动态生成，事先并不知道内容，在启动后，这些值依然是不变的。
很明显，自定义的grains并不是直接放在minion上，而是放在master配置文件中定义的file_roots下base环境的_grains目录中。执行state.highstate，saltutil.sync_grains，saltutil.sync_all等命令时，会将_grains中的文件分发到客户端上。
下面来编写一个最简单的Grains来，了解如何自己编写：我们的file_roots为/srv/salt/base，增加自定义grain的操作如下：
```
[root@linux-node1 ~]# mkdir /srv/salt/base/_grains/
    下面我们来编写grains，记住：必须返回一个字典！
[root@linux-node1 ~]# vim /srv/salt/base/_grains/my_grains.py
#!/usr/bin/env python
#-*- coding: utf-8 -*-
def my_grains():
    #初始化一个grains字典
    grains = {}
    #设置字典中的key-value
    grains['roles'] = 'apache'
    grains['iaas'] = 'openstack'
    #返回这个字典
return grains
```

刷新grains
```
[root@linux-node1 ~]#  salt '*' saltutil.sync_grains
linux-node1.example.com:
    - grains.my_grains
linux-node2.example.com:
    - grains.my_grains
```
刷新后，我们自定义的grains脚本会存放在minion配置文件制定的cache目录下：

```
[root@linux-node1 ~]#  ls -l /var/cache/salt/minion/extmods/grains
total 8
-rw------- 1 root root 251 Jan 23 11:08 my_grains.py
-rw------- 1 root root 370 Jan 23 11:08 my_grains.pyc
    现在我们可以获取到我们自己编写的grains。同时，除了执行saltutil.sync_grains进行刷新外，也可以执行saltutil.sync_grains进行刷新操作。或者在我们执行state.highstate的时候也会自动进行刷新。
[root@linux-node1 ~]# salt '*' grains.get iaas
linux-node2.example.com:
    openstack
linux-node1.example.com:
    openstack
```

### Grains的优先级
到目前位置，我们知道Grains有四种存放的方法，或者说是位置：SaltStack自带的Grains，自定义的Grains和我们编写的grains的模块返回的Grains，如果grains的名称一样，到底以哪个为准呢？优先级从低到高如下：
1)系统自带grains
2)/etc/salt/grains里面指定的grains
3)/etc/salt/minion里面设置的grains
4)自已编写的grains模块
   请看下面的输出，对于linu
```
[root@linux-node1 ~]# salt '*' grains.get roles
linux-node2.example.com:
    apache
linux-node1.example.com:
    winner
```

## 编写Returners

编写Returnners和Module类似，你需要在file_roots目录下创建一个_returners目录，将编写的Retuner文件放置其中。可以通过执行saltutil.sync_returners 或者 saltutil.sync_all命令同步到Minion。或者对Minion执行state.highstate时会自动同步，同步后在/var/cache/salt/minion/files/base/_returners/目录下找到编写的returners模块。

1. Returners编写方法：

一个return是一个模块，其中包含returner函数(function)。这个returner函数只能指定一个参数。参数是通过调用minion函数的返回结果. 比如minion函数test.ping将返回的参数是True。
例：编写一个将结果写到日志文件里面的Returner
```
[root@test ~]# cd /etc/salt/states/
[root@test states]# mkdir _returners
[root@test states]# cd _returners/
[root@test _returners]# vim localfile_return.py
# -*- coding: utf-8 -*-
'''
The localfile returner will write return data to system file
'''

# Import python libs
from __future__ import print_function

def __virtual__():
    '''
    return name
    '''
    return "localfile_return"

def returner(ret):
    '''
    Write the return data to the system file
    '''
    f=open('/var/log/salt/localfile_returner.log','a+')
    f.write(str(ret)[1:-1]+'\n')
f.close()
```

例子中先打开了一个log文件，然后将返回数据写到了文件中。注意__virtual__()中返回的名称就是这个自定义Returners的名称。

2. 同步到各个Minion

```
[root@test _returners]# salt '*' saltutil.sync_returners
```

3. 使用自定义的Returners
[root@lb-node1 _returners]# salt 'lb-node2.example.com' cmd.run 'uptime' --return localfile_return
lb-node2.dianjoy.com:
     16:00:27 up 244 days, 18:07,  1 user,  load average: 1.21, 1.21, 1.19
4.查看结果
[root@lb-node2 ~]# tail -f /var/log/salt/localfile_returner.log 
'fun_args': ['uptime'], 'jid': '20141023160027343808', 'return': ' 16:00:27 up 244 days, 18:07,  1 user,  load average: 1.21, 1.21, 1.19', 'retcode': 0, 'success': True, 'fun': 'cmd.run', 'id': 'lb-node2. example.com'

## 编写执行Module

**内置模块**
我们在前面一直在使用模块，其实SaltStack的每个模块都是一个独立的Python脚本，存放在对应Python的site-packages/salt/modules目录下，而且每个模块的每个方法都对应到这个脚本里面的函数。
比如可以通过自带的service模块来学习：
```
[root@linux-node1 ~]# cat /usr/lib/python2.6/site-packages/salt/modules/service.py
```

**外置模块**
如果内置的模块满足不了生产需要，SlatStack支持用户自己编写模块。模块的名字就是模块文件的名字，比如foo.py得模块名为foo。同时注意如果你编写的模块名和系统内置的相同会覆盖掉系统内置的模块。
如果要编写自己的模块，需要在之前设置的file_roots（Master.conf里面配置）下面创建_modules目录，所编写的自定义模块放在这里，编写完毕后，如果需要使用该模块需要将模块同步到Minion上去，使用saltutil.sync_modules或者saltutil.sync_all命令。还有一种方法就是当你对某个Minion执行state.highstate的时候会自动同步到相应的节点上。
SlatStack自定义模块的强大在于你可以调用SALT自身的一些模块或者组件，比如你可以在自定义模块中使用Grains（__grains__）、Pillar，甚至直接使用cmd.run(__salt__)。调用别的模块。
```
[root@linux-node1 ~]# mkdir /srv/salt/_modules/
[root@linux-node1 ~]# vim /srv/salt/_modules/my_disk.py
def list():
    cmd = 'df -h'
    ret = __salt__['cmd.run'](cmd)
return ret
同步自定义模块到Minion,和Grains类似，自定义的脚本默认会存放在
/var/cache/salt/minion/extmods/modules/目录下。
[root@linux-node1 ~]# salt '*' saltutil.sync_modules
test-node2.dianjoy.com:
    - modules.my_disk
test-node3.dianjoy.com:
    - modules.my_disk
[root@linux-node1 ~]# salt '*' my_disk.list
```
在很多时候，你完全可以使用自定义模块来替代cmd.run，这也是SaltStack推荐的方式。