import json
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

    def pod_exec(self, namespace, name, height, width, container=""):
        try:
            api_instance = client.CoreV1Api(self.api_client)
            
            exec_command = [
                "/bin/sh",
                "-c",
                'TERM=xterm-256color; export TERM; [ -x /bin/bash ] '
                '&& ([ -x /usr/bin/script ] '
                '&& /usr/bin/script -q -c "/bin/bash" /dev/null || exec /bin/bash) '
                '|| exec /bin/sh'
                '&& cp -rp /etc/skel/.bash* /root/']
            
            cont_stream = stream(api_instance.connect_get_namespaced_pod_exec,
                                 name=name,
                                 namespace=namespace,
                                 container=container,
                                 command=exec_command,
                                 stderr=True,
                                 stdin=True,
                                 stdout=True,
                                 tty=True,
                                 _preload_content=False
                                 )
            cont_stream.write_channel(4, json.dumps({"Height": int(height), "Width": int(width)}))
            return True, cont_stream
        except ApiException as api_e:
            return False, str(api_e.reason)
        except Exception as e:
            return False, str(e)
    
    def websocket_handler(self, msg):
        print(f"Received message: {msg}")
