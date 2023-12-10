# Base Image
FROM centos:7.9.2009

# Install Pkg
RUN curl -o /etc/yum.repos.d/epel.repo http://mirrors.aliyun.com/repo/epel-7.repo && \
    curl -s https://packagecloud.io/install/repositories/StackStorm/stable/script.rpm.sh | bash && \
    yum install -y st2 crudini httpd-tools st2web supervisor nginx && \
    yum clean all

# Setup Datastore Encryption
RUN DATASTORE_ENCRYPTION_KEYS_DIRECTORY="/etc/st2/keys" && \
    DATASTORE_ENCRYPTION_KEY_PATH="${DATASTORE_ENCRYPTION_KEYS_DIRECTORY}/datastore_key.json" && \
    mkdir -p ${DATASTORE_ENCRYPTION_KEYS_DIRECTORY} && \
    st2-generate-symmetric-crypto-key --key-path ${DATASTORE_ENCRYPTION_KEY_PATH} && \
    chgrp st2 ${DATASTORE_ENCRYPTION_KEYS_DIRECTORY} && \
    chmod o-r ${DATASTORE_ENCRYPTION_KEYS_DIRECTORY} && \
    chgrp st2 ${DATASTORE_ENCRYPTION_KEY_PATH} && \
    chmod o-r ${DATASTORE_ENCRYPTION_KEY_PATH} && \
    crudini --set /etc/st2/st2.conf keyvalue encryption_key_path ${DATASTORE_ENCRYPTION_KEY_PATH} && \

#Supervisord config
ADD nginx.conf /etc/nginx/nginx.conf
ADD supervisord.conf /etc/supervisord.conf
ADD nginx.ini /etc/supervisord.d/nginx.ini
ADD st2api.ini /etc/supervisord.d/st2api.ini

ENV LANG "zh_CN.UTF-8"
# Outside Port
EXPOSE 8088

#supervisord start
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisord.conf"]
