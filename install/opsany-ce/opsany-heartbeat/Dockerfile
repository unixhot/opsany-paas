# Base Image
FROM centos:7.8.2003

# Install Pkg
ADD heartbeat-7.13.2-x86_64.rpm /tmp/heartbeat-7.13.2-x86_64.rpm
RUN rpm -ivh /tmp/heartbeat-7.13.2-x86_64.rpm && rm -f /tmp/heartbeat-7.13.2-x86_64.rpm

#supervisord start
CMD ["/usr/bin/heartbeat", "-c", "/etc/heartbeat/heartbeat.yml"]
