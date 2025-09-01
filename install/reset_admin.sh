#!/bin/bash

docker exec -it opsany-saas-ce-rbac sh -c "python /opt/opsany/rbac/rbac/utils/reset_admin_mfa"
docker exec -it opsany-paas-login sh -c "python /opt/opsany/paas/login/init_admin.py"