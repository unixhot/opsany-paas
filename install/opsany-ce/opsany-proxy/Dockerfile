# Base Image
FROM registry.cn-beijing.aliyuncs.com/opsany/python:3.12.11-slim-bullseye

# Add Proxy
ADD opsany-proxy /opt/opsany-proxy

# Update System
RUN sed -i 's/deb.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list \
    && sed -i 's/security.debian.org/mirrors.aliyun.com/g'  /etc/apt/sources.list \
    && echo "deb http://mirrors.aliyun.com/debian-security bullseye-security main contrib non-free" >> /etc/apt/sources.list \
    && apt-get update && apt-get -y install build-essential net-tools telnet vim iputils-ping libmariadb-dev supervisor snmp openssh-client openssl sshpass nmap \
    && apt-get clean && sed -i 's/mibs/#mibs/g' /etc/snmp/snmp.conf \ 
    && pip --no-cache-dir install CherryPy==18.10.0 jinja2==3.0.0 salt==3007.6 zmq==0.0.0 pyzmq==27.0.0 tornado==6.5.1 distro==1.9.0 backports.ssl_match_hostname==3.7.0.1 msgpack==1.1.1 looseversion==1.3.0 -i http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com \
    && pip --no-cache-dir install -r /opt/opsany-proxy/requirements.txt -i http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com \
    && mkdir -p /opt/opsany/logs/proxy \
    && useradd saltapi \
    && echo "saltapi:OpsAny@2020" | chpasswd

# Supervisord config
ADD supervisord.conf /etc/supervisord.conf
ADD saltmaster.ini /etc/supervisord.d/saltmaster.ini
ADD saltapi.ini /etc/supervisord.d/saltapi.ini
ADD proxy.ini /etc/supervisord.d/proxy.ini

ENV ANSIBLE_HOST_KEY_CHECKING=False
ENV OPS_ANY_ENV=production

# Outside Port
EXPOSE 4505 4506 8010

# Supervisord start
CMD ["supervisord", "-c", "/etc/supervisord.conf"]
