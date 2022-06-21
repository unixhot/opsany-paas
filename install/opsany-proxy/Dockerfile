# Base Image
FROM python:3.6.15-alpine3.15

# Add Proxy
ADD opsany-proxy /opt/opsany-proxy

# Update System
RUN sed -i 's/dl-cdn.alpinelinux.org/mirrors.aliyun.com/g' /etc/apk/repositories \
    && apk add --no-cache sshpass build-base py-gevent mariadb-dev openssh-client zeromq zeromq-dev gcc g++ make libffi-dev openssl-dev zlib-dev jpeg-dev linux-pam linux-pam-dev gmp libssh2 procps pcre supervisor \
    && pip --no-cache-dir install CherryPy==18.6.1 jinja2==3.0.0 salt==3004.1 -i http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com \
    && pip --no-cache-dir install -r /opt/opsany-proxy/requirements.txt -i http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com \
    && mkdir -p /opt/opsany/logs \
    && adduser -D saltapi \
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
