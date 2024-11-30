# 使用AlmaLinux官方镜像作为基础镜像
FROM docker.m.daocloud.io/almalinux:9.5

# 安装OpenSSH服务
RUN dnf -y update && \
    dnf -y install -y openssh-server && \
    dnf clean all

# 设置SSH支持密码登录
RUN ssh-keygen -A && \
    mkdir /var/run/sshd && \
    echo 'root:123456.coM' | chpasswd && \
    sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config

# 开放22端口
EXPOSE 22
 
# 启动ssh服务
CMD ["/usr/sbin/sshd", "-D"]
