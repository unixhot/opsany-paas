# Base Image
FROM centos:7.8.2003

# Install Pkg
RUN curl -o /etc/yum.repos.d/epel.repo http://mirrors.aliyun.com/repo/epel-7.repo && yum install -y libjpeg-turbo-devel openldap-devel kde-l10n-Chinese glibc-common sshpass nginx supervisor python2-pip python2-devel gcc glibc make zlib-devel openssl-devel curl-devel mysql-devel python36 python36-devel openssh-clients openssl-devel && mkdir -p /opt/opsany/logs && yum clean all && echo -e "LANG=zh_CN.UTF-8" > /etc/locale.conf && echo -e 'export LANG="zh_CN.UTF-8"' >> /etc/profile && localedef -c -f UTF-8 -i zh_CN zh_CN.utf8 && source /etc/profile

# Add paas-agent
ADD ./paas-agent /opt/opsany/paas-agent

# Pip Install
RUN pip --no-cache-dir install -r /opt/opsany/paas-agent/etc/build/packages/requirements.txt -i http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com && pip --no-cache-dir install virtualenv virtualenvwrapper supervisor==3.3.3 -i http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com && mkdir -p /opt/py36/bin && ln -s /usr/bin/python3.6 /opt/py36/bin/python && ln -s /usr/bin/pyvenv-3.6 /opt/py36/bin/pyvenv && ln -s /usr/bin/pip-3.6 /opt/py36/bin/pip

#Supervisord config
ADD nginx.conf /etc/nginx/nginx.conf
ADD supervisord.conf /etc/supervisord.conf
ADD paasagent.ini /etc/supervisord.d/paasagent.ini
ADD nginx.ini /etc/supervisord.d/nginx.ini

ENV LANG "zh_CN.UTF-8"
# Outside Port
EXPOSE 4245 8085

#supervisord start
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisord.conf"]
