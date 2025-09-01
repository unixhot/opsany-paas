# MySQL Operator使用

## 部署MySQL Operator

1. 安装CRD

```
kubectl apply -f deploy-crds.yaml
```

2. 安装控制器

```
# 执行安装
kubectl apply -f deploy-operator.yaml

# 查看安装结果
kubectl get deployment mysql-operator --namespace mysql-operator

# 出现以下类似内容，为安装成功
NAME             READY   UP-TO-DATE   AVAILABLE   AGE
mysql-operator   1/1     1            1           37s
```

## 使用MySQL Operator

