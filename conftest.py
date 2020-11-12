"""
============================
Author:古一
Time:2020/10/28
E-mail:369799130@qq.com
============================
"""
import pytest
import requests
import jsonpath
from loguru import logger

from api_member.member_api import MemberApi
from common.handle_mysql import HandleMysql

ma = MemberApi()


@pytest.fixture(scope='class')
def get_login_data():
    data = MemberApi().get_login_data()
    return data


@pytest.fixture(scope='class')
def connect_mysql(request):
    db = HandleMysql(**request.param)
    yield db
    db.close()


@pytest.fixture(scope='session', autouse=True)
def task_mark():
    logger.debug("{:=^50}".format('测试任务开始'))
    yield
    logger.debug("{:=^50}".format('测试任务结束'))


@pytest.fixture(autouse=True)
def case_mark():
    logger.debug("{:=^50}".format('用例开始'))
    yield
    logger.debug("{:=^50}".format('用例结束'))
