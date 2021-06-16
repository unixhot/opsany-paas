# Base Image
FROM python:3.6.12-alpine3.11
# Volumes
VOLUME ["/etc/salt/pki", "/var/cache/salt", "/var/logs/salt", "/etc/salt/master.d", "/srv/salt"]

# Update System
RUN sed -i 's/dl-cdn.alpinelinux.org/mirrors.aliyun.com/g' /etc/apk/repositories \
    && apk add --no-cache openssh-client zeromq zeromq-dev gcc g++ make libffi-dev openssl-dev zlib-dev jpeg-dev linux-pam linux-pam-dev gmp libssh2 procps pcre supervisor \
    && pip --no-cache-dir install CherryPy salt -i http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com\
    && mkdir -p /opt/opsany/logs \
    && adduser -D saltapi \
    && echo "saltapi:OpsAny@2020" | chpasswd

# Supervisord config
ADD supervisord.conf /etc/supervisord.conf
ADD saltmaster.ini /etc/supervisord.d/saltmaster.ini
ADD saltapi.ini /etc/supervisord.d/saltapi.ini
ADD saltminion.ini /etc/supervisord.d/saltminion.ini

# Outside Port
EXPOSE 4505 4506 8005

# Supervisord start
CMD ["supervisord", "-c", "/etc/supervisord.conf"]
