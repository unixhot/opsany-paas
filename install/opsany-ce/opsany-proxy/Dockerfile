# Base Image
FROM python:3.6.15-slim-bullseye

# Add Proxy
ADD opsany-proxy /opt/opsany-proxy

# Update System
RUN sed -i 's/deb.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list \
    && apt-get update && apt-get -y install build-essential net-tools telnet iputils-ping libmariadb-dev supervisor snmp openssh-client openssl sshpass \
    && apt-get clean \ 
    && pip --no-cache-dir install CherryPy==18.6.1 jinja2==3.0.0 salt==3004.1 -i http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com \
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
