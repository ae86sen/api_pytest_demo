"""
============================
Author:古一
Time:2020/10/28
E-mail:369799130@qq.com
============================
"""
import os

import pytest
from loguru import logger

logger.add('./log/{time}.log', rotation='20 MB', retention='1 week', encoding='utf-8')

pytest.main(['-s', r"--alluredir=report/json", "--clean-alluredir"])
os.system('allure generate ./report/json -o ./report/html -c')
# pytest.main(['-s'])
