# Base Image
FROM registry.cn-beijing.aliyuncs.com/opsany/python:3.12.11-slim-bullseye

# Add paas-agent
ADD ./paas-agent /opt/opsany/paas-agent

# Update System
RUN sed -i 's/deb.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list \
    && sed -i 's/security.debian.org/mirrors.aliyun.com/g'  /etc/apt/sources.list \
    && sed -i '2s/main$/main non-free/' /etc/apt/sources.list \
    && sed -i '4s/main$/main contrib non-free/' /etc/apt/sources.list \
    && apt-get update && apt-get -y install build-essential procps tree mariadb-client net-tools telnet vim iputils-ping libmariadb-dev supervisor nginx git \
    && apt-get clean
    
# Pip Install
RUN pip --no-cache-dir install -r /opt/opsany/paas-agent/etc/build/packages/requirements.txt -i http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com \
    && mkdir -p /opt/py312/bin && ln -s /usr/local/bin/python3.12 /opt/py312/bin/python3  && ln -s /usr/bin/pip3.12 /opt/py312/bin/pip3

#Supervisord config
ADD nginx.conf /etc/nginx/nginx.conf
ADD supervisord.conf /etc/supervisord.conf
ADD paasagent.ini /etc/supervisord.d/paasagent.ini
ADD nginx.ini /etc/supervisord.d/nginx.ini

# Outside Port
EXPOSE 4245 8085

#supervisord start
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisord.conf"]
