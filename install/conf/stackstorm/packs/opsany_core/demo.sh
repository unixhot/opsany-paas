#!/bin/bash
function image_build() {
    ImageInfo=registry-bj-dx-dzqywjd-hlw-icp.inspurcloud.cn/${namespace}/${controller_name}:${name}-${DATETAG}
    docker build -f ${dockerfile} -t ${ImageInfo} .
    docker push ${ImageInfo}
    if [ ${controller_type} == 'deployment' ]; then
      set_deployment_images
    else
      set_statefulse_images
    fi

}

function set_deployment_images() {
    if [ ${namespace} == 'tydl' ];then
         kubectl --kubeconfig=${kube_config} -n cmpt set image deployments/${controller_name} *=registry-bj-dx-dzqywjd-hlw-icp.inspurcloud.cn/${namespace}/${controller_name}:${name}-${DATETAG} --all
    else
        kubectl --kubeconfig=${kube_config} -n ${namespace} set image deployments/${controller_name} *=registry-bj-dx-dzqywjd-hlw-icp.inspurcloud.cn/${namespace}/${controller_name}:${name}-${DATETAG} --all
    fi
}

function set_statefulse_images() {
    if [ ${namespace} == 'tydl' ];then
        kubectl --kubeconfig=${kube_config} -n cmpt set image  sts ${controller_name} ${controller_name}=registry-bj-dx-dzqywjd-hlw-icp.inspurcloud.cn/${namespace}/${controller_name}:${name}-${DATETAG} --record
    else
        kubectl --kubeconfig=${kube_config} -n ${namespace} set image  sts ${controller_name} ${controller_name}=registry-bj-dx-dzqywjd-hlw-icp.inspurcloud.cn/${namespace}/${controller_name}:${name}-${DATETAG} --record
    fi
}

function main() {
  image_build

}

set -x
DATETAG=$(date +%Y%m%d%H%M)
dockerfile=Dockerfile_tydl_cmpt-service_php_test
name=sso-service-test
kube_config=/root/.k8s/inspur/test/config
namespace=tydl
controller_name=cmpt-service
controller_type=statefulset
cd /data/docker
main