"""
============================
Author:古一
Time:2020/11/10
E-mail:369799130@qq.com
============================
"""

import yaml

a = yaml.safe_load(open('demo.yaml', encoding='utf-8'))
from common.base_api import BaseApi
print(a)
# x = BaseApi().template(a, {'invest_member_id': 123456})
# print(x)
