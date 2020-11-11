"""
============================
Author:古一
Time:2020/10/28
E-mail:369799130@qq.com
============================
"""
import os

import pytest

pytest.main(['-m', 'zls', '-s', r"--alluredir=report/json", "--clean-alluredir"])
os.system('allure generate ./report/json -o ./report/html -c')
# pytest.main(['-s'])
