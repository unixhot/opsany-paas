# Base Image
FROM python:2.7.18-alpine3.11

# Install PATH
RUN mkdir /opt/opsany && mkdir /etc/supervisord.d

# Install Gcc
RUN sed -i 's/dl-cdn.alpinelinux.org/mirrors.aliyun.com/g' /etc/apk/repositories \
    && apk add --no-cache gcc g++ make libffi-dev openssl-dev zlib-dev jpeg-dev \
    && pip --no-cache-dir install supervisor -i http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com

# Add paas
ADD ./paas /opt/opsany/paas

# Pip Install
RUN pip --no-cache-dir install -r /opt/opsany/paas/login/requirements.txt -i http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com

#Supervisord config
ADD supervisord.conf /etc/supervisord.conf
ADD login.ini /etc/supervisord.d/login.ini

# Outside Port
EXPOSE 8003

#supervisord start
CMD ["supervisord", "-c", "/etc/supervisord.conf"]
