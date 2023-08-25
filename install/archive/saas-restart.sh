#!/bin/bash

#解决Docker直接停止，导致supervisord的sock文件没有删除的问题，先进行删除。
docker exec opsany-paas-paasagent rm -f /opt/opsany/paas-agent/apps/projects/job/run/supervisord.sock
docker exec opsany-paas-paasagent rm -f /opt/opsany/paas-agent/apps/projects/rbac/run/supervisord.sock
docker exec opsany-paas-paasagent rm -f /opt/opsany/paas-agent/apps/projects/workbench/run/supervisord.sock
docker exec opsany-paas-paasagent rm -f /opt/opsany/paas-agent/apps/projects/cmdb/run/supervisord.sock
docker exec opsany-paas-paasagent rm -f /opt/opsany/paas-agent/apps/projects/control/run/supervisord.sock
docker exec opsany-paas-paasagent rm -f /opt/opsany/paas-agent/apps/projects/cmp/run/supervisord.sock
docker exec opsany-paas-paasagent rm -f /opt/opsany/paas-agent/apps/projects/monitor/run/supervisord.sock
docker exec opsany-paas-paasagent rm -f /opt/opsany/paas-agent/apps/projects/devops/run/supervisord.sock
docker exec opsany-paas-paasagent rm -f /opt/opsany/paas-agent/apps/projects/bastion/run/supervisord.sock
#docker exec opsany-paas-paasagent rm -f /opt/opsany/paas-agent/apps/projects/pipeline/run/supervisord.sock
#docker exec opsany-paas-paasagent rm -f /opt/opsany/paas-agent/apps/projects/deploy/run/supervisord.sock
docker exec opsany-paas-paasagent rm -f /opt/opsany/paas-agent/apps/projects/dashboard/run/supervisord.sock


#start rbac
docker exec opsany-paas-paasagent /usr/bin/supervisord -c /opt/opsany/paas-agent/apps/projects/rbac/conf/supervisord.conf
sleep 3
docker exec opsany-paas-paasagent /usr/bin/supervisorctl -c /opt/opsany/paas-agent/apps/projects/rbac/conf/supervisord.conf status

#start workbench
docker exec opsany-paas-paasagent /usr/bin/supervisord -c /opt/opsany/paas-agent/apps/projects/workbench/conf/supervisord.conf
sleep 3
docker exec opsany-paas-paasagent /usr/bin/supervisorctl -c /opt/opsany/paas-agent/apps/projects/workbench/conf/supervisord.conf status

#start cmdb
docker exec opsany-paas-paasagent /usr/bin/supervisord -c /opt/opsany/paas-agent/apps/projects/cmdb/conf/supervisord.conf
sleep 3
docker exec opsany-paas-paasagent /usr/bin/supervisorctl -c /opt/opsany/paas-agent/apps/projects/cmdb/conf/supervisord.conf status

#start control
docker exec opsany-paas-paasagent /usr/bin/supervisord -c /opt/opsany/paas-agent/apps/projects/control/conf/supervisord.conf
sleep 3
docker exec opsany-paas-paasagent /usr/bin/supervisorctl -c /opt/opsany/paas-agent/apps/projects/control/conf/supervisord.conf status

#start job
docker exec opsany-paas-paasagent /usr/bin/supervisord -c /opt/opsany/paas-agent/apps/projects/job/conf/supervisord.conf
sleep 3
docker exec opsany-paas-paasagent /usr/bin/supervisorctl -c /opt/opsany/paas-agent/apps/projects/job/conf/supervisord.conf status

#start monitor
docker exec opsany-paas-paasagent /usr/bin/supervisord -c /opt/opsany/paas-agent/apps/projects/monitor/conf/supervisord.conf
sleep 3
docker exec opsany-paas-paasagent /usr/bin/supervisorctl -c /opt/opsany/paas-agent/apps/projects/monitor/conf/supervisord.conf status

#start cmp
docker exec opsany-paas-paasagent /usr/bin/supervisord -c /opt/opsany/paas-agent/apps/projects/cmp/conf/supervisord.conf
sleep 3
docker exec opsany-paas-paasagent /usr/bin/supervisorctl -c /opt/opsany/paas-agent/apps/projects/cmp/conf/supervisord.conf status

#start devops
docker exec opsany-paas-paasagent /usr/bin/supervisord -c /opt/opsany/paas-agent/apps/projects/devops/conf/supervisord.conf
sleep 3
docker exec opsany-paas-paasagent /usr/bin/supervisorctl -c /opt/opsany/paas-agent/apps/projects/devops/conf/supervisord.conf status

#start bastion
docker exec opsany-paas-paasagent /usr/bin/supervisord -c /opt/opsany/paas-agent/apps/projects/bastion/conf/supervisord.conf
sleep 3
docker exec opsany-paas-paasagent /usr/bin/supervisorctl -c /opt/opsany/paas-agent/apps/projects/bastion/conf/supervisord.conf status

#start pipeline
#docker exec opsany-paas-paasagent /usr/bin/supervisord -c /opt/opsany/paas-agent/apps/projects/pipeline/conf/supervisord.conf
#sleep 3
#docker exec opsany-paas-paasagent /usr/bin/supervisorctl -c /opt/opsany/paas-agent/apps/projects/pipeline/conf/supervisord.conf status

#start deploy
#docker exec opsany-paas-paasagent /usr/bin/supervisord -c /opt/opsany/paas-agent/apps/projects/deploy/conf/supervisord.conf
#sleep 3
#docker exec opsany-paas-paasagent /usr/bin/supervisorctl -c /opt/opsany/paas-agent/apps/projects/deploy/conf/supervisord.conf status

#start dashboard
docker exec opsany-paas-paasagent /usr/bin/supervisord -c /opt/opsany/paas-agent/apps/projects/dashboard/conf/supervisord.conf
sleep 3
docker exec opsany-paas-paasagent /usr/bin/supervisorctl -c /opt/opsany/paas-agent/apps/projects/dashboard/conf/supervisord.conf status
