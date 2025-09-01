# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa
from esb.utils import SmartHost


SYSTEM_NAME = 'CMSI'


host = SmartHost(
    host_prod='need_to_be_updated',
)


# 通过 SMTP 发送邮件的配置
smtp_host = 'smtp.qq.com'
smtp_port = 465
smtp_user = '873515490@qq.com'
smtp_pwd = 'nwsgocgaoregbedc'
smtp_usessl = True
smtp_usetls = False
# mail_sender = 'blueking@bking.com'
mail_sender = '873515490@qq.com'

# 通过第三方接口发送邮件的配置
dest_url = ''  # 邮件第三方接口完整路径

# send_weixin 组件微信消息类型配置
wx_type = 'qy'

# 发送微信公众号消息配置
wx_app_id = ''
wx_secret = ''
wx_template_id = 'yrxKwt3OR4BGvuZzwiASaSm_GfOtxwak3mMfh5Ijiaw'

# 微信企业号配置
wx_qy_corpid = ''
wx_qy_corpsecret = ''
wx_qy_agentid = ''

# 发送短信腾讯云配置 sdkappid 对应的 appkey，需要业务方高度保密
qcloud_app_id = '1400468115'
qcloud_app_key = 'eba8d646e9a6df4eb0421417f759a68e'

# cmsi支持的信息发送类型
msg_type = [
    {
        "type": "weixin",
        "label": "微信",
        "label_en": "weixin"
    },
    {
        "type": "mail",
        "label": "邮件",
        "label_en": "mail"
    },
    {
        "type": "sms",
        "label": "短信",
        "label_en": "sms"
    },
    {
        "type": "voice",
        "label": "语音",
        "label_en": "voice"
    }
]

msg_type_map = {
    "weixin": "send_weixin",
    "mail": "send_mail",
    "sms": "send_sms",
    "voice": "send_voice_msg"
}
