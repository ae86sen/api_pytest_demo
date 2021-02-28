import os

import allure
import pytest
import yaml
from loguru import logger

from common.handle_path import DATA_DIR
from cases.case_member.member_case import MemberCase

case_data_path = os.path.join(DATA_DIR, 'member_case_data.yaml')
datas = yaml.safe_load(open(case_data_path, encoding='utf-8'))


@allure.feature('人员')
class TestMember(MemberCase):
    conf_mysql = MemberCase().mysql_conf

    @allure.story('登录')
    @allure.title('{data[title]}')
    @pytest.mark.parametrize('data', datas['login'])
    def test_login(self, data):
        """登录功能验证"""
        result = self.login_api(**data['account']).json()
        self.assert_equal(data['expected']['code'], result['code'])
        self.assert_equal(data['expected']['msg'], result['msg'])
        logger.info('用例通过！')

    @allure.story('注册')
    @allure.title('{data[title]}')
    @pytest.mark.parametrize('data', datas['register'])
    def test_register(self, data):
        """注册功能验证"""
        result = self.case_register(data['account'])
        self.assert_equal(data['expected']['code'], result['code'])
        self.assert_equal(data['expected']['msg'], result['msg'])
        logger.info('用例通过！')

    @allure.story('充值')
    @allure.title('{data[title]}')
    @pytest.mark.parametrize('connect_mysql', [conf_mysql], indirect=True)
    @pytest.mark.parametrize('data', datas['recharge'])
    def test_recharge(self, data, get_login_data, connect_mysql):
        """充值业务验证"""
        login_data = get_login_data
        db = connect_mysql
        result = self.case_recharge(data, login_data, db)
        self.assert_equal(data['expected']['code'], result['code'])
        self.assert_equal(data['expected']['msg'], result['msg'])
        if data['sql']:
            self.assert_equal(self.to_two_decimal(data['amount']), result['recharge'])
        logger.info('用例通过！')

    @allure.story('提现')
    @allure.title('{data[title]}')
    @pytest.mark.parametrize('connect_mysql', [conf_mysql], indirect=True)
    @pytest.mark.parametrize('data', datas['withdraw'])
    def test_withdraw(self, data, get_login_data, connect_mysql):
        """提现业务验证"""
        login_data = get_login_data
        db = connect_mysql
        logger.info(data)
        result = self.case_withdraw(data, login_data, db)
        self.assert_equal(data['expected']['code'], result['code'])
        self.assert_equal(data['expected']['msg'], result['msg'])
        if data['sql']:
            self.assert_equal(self.to_two_decimal(data['amount']), result['withdraw'])
        logger.info('用例通过！')
