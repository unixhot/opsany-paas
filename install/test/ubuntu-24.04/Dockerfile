# 使用Ubuntu官方镜像作为基础镜像
FROM docker.m.daocloud.io/ubuntu:24.04

# 安装OpenSSH服务
RUN sed -i 's/deb.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list && \
    sed -i 's/security.debian.org/mirrors.aliyun.com/g'  /etc/apt/sources.list && \
    apt-get update && apt-get install -y openssh-server net-tools curl wget sudo && \
    apt-get clean

# 设置SSH支持密码登录
RUN mkdir /var/run/sshd && \
    echo 'root:123456.coM' | chpasswd && \
    sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config

# 开放22端口
EXPOSE 22
 
# 启动ssh服务
CMD ["/usr/sbin/sshd", "-D"]
