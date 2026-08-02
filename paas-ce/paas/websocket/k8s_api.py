import datetime
import json
import logging
from kubernetes.config.kube_config import _get_kube_config_loader
from kubernetes.client import ApiClient, Configuration
from kubernetes import client
from kubernetes.client.exceptions import ApiException
from kubernetes.stream import stream
import io

import urllib3

urllib3.disable_warnings()


class K8sApi:
    def __init__(self, config_string):
        io_space = io.StringIO()
        io_space.write(config_string)
        self._base_kwargs = {
            # 实际超时时间 是 _request_timeout 的 4 倍
            "_request_timeout": 2
        }
        try:
            config = Configuration()
            config.verify_ssl = False
            loader = _get_kube_config_loader(io_space)
            loader.load_and_set(config)
            self.api_client = ApiClient(configuration=config)
        except Exception as e:
            self.api_client = None
        io_space.close()

    def pod_exec(self, namespace, name, height=80, width=120, container=None):
        if not namespace or not name:
            return False, "namespace and name are required"
        api_instance = client.CoreV1Api(self.api_client)
        # 如果未指定 container，可尝试读取 Pod 信息自动选择第一个容器
        if not container:
            try:
                pod = api_instance.read_namespaced_pod(name, namespace)
                if pod.spec.containers:
                    container = pod.spec.containers[0].name
                else:
                    return False, "pod is not in container"
            except ApiException as e:
                return False, f"Failed to get pod info: {e}"
            except Exception as e:  # 增加网络层捕获
                return False, f"Network/Unknown error getting pod: {str(e)}"
        try:
            exec_command = [
                "/bin/sh",
                "-c",
                'TERM=xterm-256color; export TERM; [ -x /bin/bash ] '
                '&& ([ -x /usr/bin/script ] '
                '&& /usr/bin/script -q -c "/bin/bash" /dev/null || exec /bin/bash) '
                '|| exec /bin/sh'
                '&& cp -rp /etc/skel/.bash* /root/'
            ]
            cont_stream = stream(
                api_instance.connect_get_namespaced_pod_exec,
                name=name,
                namespace=namespace,
                container=container,
                command=exec_command,
                stdin=True,
                stdout=True,
                stderr=True,
                tty=True,
                _preload_content=False,
            )
            try:
                cont_stream.write_channel(4, json.dumps({"Height": int(height), "Width": int(width)}))
            except Exception as e:
                # 如果写入失败，关闭流并返回错误
                cont_stream.close()
                return False, f"Failed to resize terminal: {str(e)}"
            return True, cont_stream
        except ApiException as e:
            return False, f"Exec failed: {e.status}, {e.reason}"
        except Exception as e:
            # 捕获所有其他异常（超时、连接断开、SSL错误等）
            return False, f"Exec unexpected error: {str(e)}"

    def websocket_handler(self, msg):
        print(f"Received message: {msg}")
