# Base Image
FROM python:3.7.12-alpine3.15

# Install PATH
RUN mkdir -p /opt/opsany/logs && mkdir /etc/supervisord.d

# Add File
ADD ./websocket /opt/opsany/websocket

# Install Gcc
RUN sed -i 's/dl-cdn.alpinelinux.org/mirrors.aliyun.com/g' /etc/apk/repositories \
    && apk add --no-cache gcc g++ make libffi-dev openssl-dev zlib-dev jpeg-dev mariadb-dev openssh-client tzdata \
    && pip --no-cache-dir install supervisor uvicorn==0.11.8 gunicorn==19.9.0 gevent==22.10.2 -i http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com \
    && pip --no-cache-dir install -r /opt/opsany/websocket/requirements.txt -i http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com

ENV TZ="Asia/Shanghai"
#Supervisord config
ADD supervisord.conf /etc/supervisord.conf
ADD websocket.ini /etc/supervisord.d/websocket.ini

# Outside Port
EXPOSE 8004

#supervisord start
CMD ["supervisord", "-c", "/etc/supervisord.conf"]
