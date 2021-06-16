# 完善测试数据

- 更新 blueking/tests/utils/utils.py 中 load_tests_settings 返回的数据为有效值
- 更新 conf/default.py 中 APP_ID、APP_TOKEN、BK_PAAS_HOST 为有效值

# 执行测试

```
python manage.py test --keepdb blueking.tests.test_client
python manage.py test --keepdb blueking.tests.test_shortcuts
python manage.py test --keepdb blueking.tests.test_utils
```
