# OpsAny访问架构

OpsAny的访问架构自2.0.0版本之后变的清晰易懂，文字描述如下：

- 最外层由Openresty承担代理的功能，承载所有入站请求，根据用户请求的URL（例如/o/cmp/为云管平台）将请求转发到对应平台的Nginx。
- 各个平台的Nginx收到请求后，将请求转发给本地的uwsgi socket，进行请求的处理。

![访问架构图](./static/access-arch.png)


## OpenResty配置解析

OpenResty容器服务opsany-base-openresty容器挂载了安装目录下的配置文件。

```
vim ${INSTALL_PATH}/conf/nginx-conf.d/opsany_paas.conf

# PaaS服务的Upstream配置
upstream OPEN_PAAS {
    server 192.168.56.13:8001 max_fails=1  fail_timeout=30s;
}
upstream OPEN_PAAS_APPENGINE {
    server 192.168.56.13:8000 max_fails=1  fail_timeout=30s;
}
upstream OPEN_PAAS_ESB {
    server 192.168.56.13:8002 max_fails=1  fail_timeout=30s;
}
upstream OPEN_PAAS_LOGIN {
    server 192.168.56.13:8003 max_fails=1  fail_timeout=30s;
}
upstream BASTION_WS {
    server 192.168.56.13:8004 max_fails=1  fail_timeout=30s;
}
upstream MONITOR_ZABBIX {
    server 192.168.56.13:8006 max_fails=1  fail_timeout=30s;
}
upstream DASHBOARD_GRAFANA {
    server 192.168.56.13:8007 max_fails=1  fail_timeout=30s;
}

# 下面是所有SaaS平台的upstrem配置
upstream SAAS_RBAC {
    server 192.168.56.13:7001 max_fails=1  fail_timeout=30s;
}
upstream SAAS_WORKBENCH {
    server 192.168.56.13:7002 max_fails=1  fail_timeout=30s;
}
upstream SAAS_CMDB {
    server 192.168.56.13:7003 max_fails=1  fail_timeout=30s;
}
upstream SAAS_CONTROL {
    server 192.168.56.13:7004 max_fails=1  fail_timeout=30s;
}
upstream SAAS_JOB {
    server 192.168.56.13:7005 max_fails=1  fail_timeout=30s;
}
upstream SAAS_MONITOR {
    server 192.168.56.13:7006 max_fails=1  fail_timeout=30s;
}
upstream SAAS_CMP {
    server 192.168.56.13:7007 max_fails=1  fail_timeout=30s;
}
upstream SAAS_BASTION {
    server 192.168.56.13:7008 max_fails=1  fail_timeout=30s;
}
upstream SAAS_DEVOPS {
    server 192.168.56.13:7009 max_fails=1  fail_timeout=30s;
}
upstream SAAS_CODE {
    server 192.168.56.13:7010 max_fails=1  fail_timeout=30s;
}
upstream SAAS_EVENT {
    server 192.168.56.13:7011 max_fails=1  fail_timeout=30s;
}
upstream SAAS_AUTO {
    server 192.168.56.13:7012 max_fails=1  fail_timeout=30s;
}
upstream SAAS_PIPELINE {
    server 192.168.56.13:7017 max_fails=1  fail_timeout=30s;
}
upstream SAAS_DEPLOY {
    server 192.168.56.13:7018 max_fails=1  fail_timeout=30s;
}
upstream SAAS_REPO {
    server 192.168.56.13:7020 max_fails=1  fail_timeout=30s;
}

# 开发环境使用PaaSAgent
upstream PAAS_AGENT_TEST {
    server 192.168.56.13:8084 max_fails=1  fail_timeout=30s;
}
upstream PAAS_AGENT_PROD {
    server 192.168.56.13:8085 max_fails=1  fail_timeout=30s;
}

# 80跳转到443，强制HTTPS访问。
server {
    listen 80;
    server_name 192.168.56.13 demo.opsany.com;
    location ~ ^/uploads/(.*) {
        autoindex off;
        root /opt/opsany/;
    }
    location ~/ {
        rewrite ^(.*)$ https://$host$1 permanent;
    }
}

server {
     listen       443 ssl http2;
     server_name 192.168.56.13 demo.opsany.com;
     access_log /opt/opsany/logs/paas_nginx_access.log;
     error_log /opt/opsany/logs/paas_nginx_error.log;
     ssl_certificate /etc/nginx/conf.d/ssl/demo.opsany.com.pem;
     ssl_certificate_key /etc/nginx/conf.d/ssl/demo.opsany.com.key;
     ssl_session_timeout 5m;
     ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:ECDHE:ECDH:AES:HIGH:!NULL:!aNULL:!MD5:!ADH:!RC4;
     ssl_protocols TLSv1 TLSv1.1 TLSv1.2;
     ssl_prefer_server_ciphers on;
    # gzip config
    gzip on;
    gzip_min_length 1k;
    gzip_comp_level 9;
    gzip_types text/plain application/javascript application/x-javascript text/css application/xml text/javascript application/x-httpd-php image/jpeg image/gif image/png;
    gzip_vary on;
    gzip_disable "MSIE [1-6]\.";
    client_max_body_size    2048m;
    underscores_in_headers on;

    # ============================ paas ============================
    # Zabbix
    location /zabbix/ {
        proxy_pass http://MONITOR_ZABBIX;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_redirect off;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Host $server_name;
    }

    # Grafana
    location /grafana/ {
        proxy_pass https://DASHBOARD_GRAFANA;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_redirect off;
        proxy_set_header Host $host;
        proxy_set_header X-WEBAUTH-USER admin;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Host $server_name;
    }

    # BASTION WebSocket
     location /ws/bastion/ {
        proxy_pass http://BASTION_WS;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_redirect off;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Host $server_name;
    }
    # PAAS_SERVICE HOST/PORT

    location / {
        proxy_pass http://OPEN_PAAS;
        proxy_pass_header Server;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Scheme $scheme;
        proxy_set_header Host $http_host;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Scheme $scheme;
        proxy_redirect http:// $scheme://;
        proxy_read_timeout 600;
    }

    # uploads
    location ~ ^/uploads/(.*) {
        autoindex off;
        root /opt/opsany/;
    }

    # 社区版文档
    location ~ ^/docs/ {
        index index.html;
        root /opt/opsany/uploads/;
    }

    # 社区支持版，移动端配置。
    location ~ ^/phone/ {
         root /opt/opsany/uploads/;
         index index.html;
    }


    # ============================ appengine ============================
    # ENGINE_SERVICE HOST/PORT
    location ~ ^/v1 {
        proxy_pass http://OPEN_PAAS_APPENGINE;
        proxy_pass_header Server;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header Host $http_host;
        proxy_set_header X-Scheme $scheme;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 600;
    }

    # ============================ esb ============================
    # ESB_SERVICE HOST/PORT
    location ~ ^/api/(.*) {
        proxy_pass http://OPEN_PAAS_ESB/$1$is_args$args;
        proxy_pass_header Server;
        proxy_set_header X-Request-Uri $request_uri;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Scheme $scheme;
        proxy_set_header Host $http_host;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
        proxy_read_timeout 600;
    }


    # ============================ login ============================
    # LOGIN_SERVICE HOST/PORT
    location ~ ^/login/(.*) {
        proxy_pass http://OPEN_PAAS_LOGIN/$1$is_args$args;
        proxy_pass_header Server;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Real-IP $remote_addr;
        #proxy_set_header X-Scheme https;
        proxy_set_header X-Scheme $scheme;
        proxy_set_header Host $http_host;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
        proxy_read_timeout 600;
    }

    # ============================ paas_agent ============================
    # for apps test
    location ~ ^/t/ {
        proxy_pass http://PAAS_AGENT_TEST;
        proxy_pass_header Server;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Scheme $scheme;
        proxy_set_header Host $http_host;
        proxy_redirect off;
        proxy_read_timeout 600;
    }

    # ============================ OpsAny SaaS ============================
    # 统一权限 rbac
    location ~ ^/o/rbac/ {
        proxy_pass http://SAAS_RBAC;
        proxy_pass_header Server;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Scheme $scheme;
        proxy_set_header Host $http_host;
        proxy_redirect off;
        proxy_read_timeout 600;
    }

    # 工作台 workbench
    location ~ ^/o/workbench/ {
        proxy_pass http://SAAS_WORKBENCH;
        proxy_pass_header Server;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Scheme $scheme;
        proxy_set_header Host $http_host;
        proxy_redirect off;
        proxy_read_timeout 600;
    }
    # 资源平台 cmdb
    location ~ ^/o/cmdb/ {
        proxy_pass http://SAAS_CMDB;
        proxy_pass_header Server;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Scheme $scheme;
        proxy_set_header Host $http_host;
        proxy_redirect off;
        proxy_read_timeout 600;
    }
    # 管控平台 control
    location ~ ^/o/control/ {
        proxy_pass http://SAAS_CONTROL;
        proxy_pass_header Server;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Scheme $scheme;
        proxy_set_header Host $http_host;
        proxy_redirect off;
        proxy_read_timeout 600;
    }
    # 作业平台 job
    location ~ ^/o/job/ {
        proxy_pass http://SAAS_JOB;
        proxy_pass_header Server;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Scheme $scheme;
        proxy_set_header Host $http_host;
        proxy_redirect off;
        proxy_read_timeout 600;
    }
    # 基础监控 monitor
    location ~ ^/o/monitor/ {
        proxy_pass http://SAAS_MONITOR;
        proxy_pass_header Server;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Scheme $scheme;
        proxy_set_header Host $http_host;
        proxy_redirect off;
        proxy_read_timeout 600;
    }
    # 云管平台 cmp
    location ~ ^/o/cmp/ {
        proxy_pass http://SAAS_CMP;
        proxy_pass_header Server;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Scheme $scheme;
        proxy_set_header Host $http_host;
        proxy_redirect off;
        proxy_read_timeout 600;
    }
    # 堡垒机 bastion
    location ~ ^/o/bastion/ {
        proxy_pass http://SAAS_BASTION;
        proxy_pass_header Server;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Scheme $scheme;
        proxy_set_header Host $http_host;
        proxy_redirect off;
        proxy_read_timeout 600;
    }
    # 应用平台 devops
    location ~ ^/o/devops/ {
        proxy_pass http://SAAS_DEVOPS;
        proxy_pass_header Server;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Scheme $scheme;
        proxy_set_header Host $http_host;
        proxy_redirect off;
        proxy_read_timeout 600;
    }
    # 代码仓库 code
    location ~ ^/o/code/ {
        proxy_pass http://SAAS_CODE;
        proxy_pass_header Server;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Scheme $scheme;
        proxy_set_header Host $http_host;
        proxy_redirect off;
        proxy_read_timeout 600;
    }
    # 流水线 pipeline
    location ~ ^/o/pipeline/ {
        proxy_pass http://SAAS_PIPELINE;
        proxy_pass_header Server;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Scheme $scheme;
        proxy_set_header Host $http_host;
        proxy_redirect off;
        proxy_read_timeout 600;
    }
    # 持续部署 deploy
    location ~ ^/o/deploy/ {
        proxy_pass http://SAAS_DEPLOY;
        proxy_pass_header Server;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Scheme $scheme;
        proxy_set_header Host $http_host;
        proxy_redirect off;
        proxy_read_timeout 600;
    }
    # 制品仓库 repo
    location ~ ^/o/repo/ {
        proxy_pass http://SAAS_REPO;
        proxy_pass_header Server;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Scheme $scheme;
        proxy_set_header Host $http_host;
        proxy_redirect off;
        proxy_read_timeout 600;
    }
}

```
