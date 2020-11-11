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


# @pytest.fixture(scope='class')
# def get_login_data():
#     response = ma.login_api()
#     return response

#
# print(get_login_data().json())
# s = {"host": 'api.lemonban.com',
#      "user": "future",
#      "password": '123456',
#      "port": 3306}
#
# db = HandleMysql(**s)
# print(db)
# x = db.count("SELECT * FROM  futureloan.loan WHERE member_id=202744;")
# print(x,type(x))