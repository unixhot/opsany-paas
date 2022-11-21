# Base Image
FROM centos:7.9.2009

# Install Pkg
RUN curl -o /etc/yum.repos.d/epel.repo http://mirrors.aliyun.com/repo/epel-7.repo && yum install -y mariadb jq python3 python3-pip && yum clean all

# Pip Install
RUN pip --no-cache-dir install requests==2.25.1 grafana-api==1.0.3 mysql-connector==2.2.9 SQLAlchemy==1.4.22 bcrypt==3.2.2 -i http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com

ENV LANG "zh_CN.UTF-8"
# Outside Port
EXPOSE 4245 8085

#supervisord start
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisord.conf"]
