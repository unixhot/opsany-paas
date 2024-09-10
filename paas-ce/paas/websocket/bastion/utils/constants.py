import re

# 内网正则校验
PRIVATE_IP_PATTERN = re.compile(r'^(127\.0\.0\.1)|(localhost)|(10\.\d{1,3}\.\d{1,3}\.\d{1,3})|(172\.((1[6-9])|(2\d)|(3[01]))\.\d{1,3}\.\d{1,3})|(192\.168\.\d{1,3}\.\d{1,3})$')
# IP正则校验
IP_PATTERN = re.compile(r'((2(5[0-5]|[0-4]\d))|[0-1]?\d{1,2})(\.((2(5[0-5]|[0-4]\d))|[0-1]?\d{1,2})){3}')
# 英文正则校验
ENGLISH_PATTERN = re.compile(r'[a-zA-Z]+')

# Model config
BLOCK_TYPE = [1, 2]
# IP限制类型 1 无 2 黑名单 3 白名单
IP_LIMIT = [1, 2, 3]
