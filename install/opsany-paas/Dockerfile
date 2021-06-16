# Base Image
FROM python:2.7.18-alpine3.11

# Install PATH
RUN mkdir /opt/opsany && mkdir /etc/supervisord.d

# Add File
ADD ./paas /opt/opsany/paas

# Install Gcc
RUN sed -i 's/dl-cdn.alpinelinux.org/mirrors.aliyun.com/g' /etc/apk/repositories \
    && apk add --no-cache gcc g++ make libffi-dev openssl-dev zlib-dev jpeg-dev \
    && pip --no-cache-dir install supervisor -i http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com \
    && pip --no-cache-dir install -r /opt/opsany/paas/paas/requirements.txt -i http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com

#Supervisord config
ADD supervisord.conf /etc/supervisord.conf
ADD paas.ini /etc/supervisord.d/paas.ini

# Outside Port
EXPOSE 8001

#supervisord start
CMD ["supervisord", "-c", "/etc/supervisord.conf"]
