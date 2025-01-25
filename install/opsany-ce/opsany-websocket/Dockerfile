# Base Image
FROM registry.cn-beijing.aliyuncs.com/opsany/python:3.7.12-slim-bullseye

# Install PATH
RUN mkdir -p /opt/opsany/logs && mkdir /etc/supervisord.d

# Add File
ADD ./websocket /opt/opsany/websocket

# Install Gcc
RUN sed -i 's/deb.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list && \
    sed -i 's/security.debian.org/mirrors.aliyun.com/g'  /etc/apt/sources.list && \
    apt-get update && apt-get -y install build-essential libmariadb-dev net-tools telnet iputils-ping openssh-client vim && apt-get clean && \
    echo '    StrictHostKeyChecking no' >> /etc/ssh/ssh_config && \ 
    pip --no-cache-dir install supervisor grafana-api==1.0.3 uvicorn==0.11.8 gunicorn==19.9.0 gevent==22.10.2 -i http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com && \
    pip --no-cache-dir install -r /opt/opsany/websocket/requirements.txt -i http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com

ENV TZ="Asia/Shanghai"
#Supervisord config
ADD supervisord.conf /etc/supervisord.conf
ADD websocket.ini /etc/supervisord.d/websocket.ini

# Outside Port
EXPOSE 8004

#supervisord start
CMD ["supervisord", "-c", "/etc/supervisord.conf"]
