import os

import pytest
import yaml
from loguru import logger

# from api_member.member_api import MemberApi
from common.handle_assert import HandleAssert as HA
from common.handle_path import CONFIG_DIR, DATA_DIR
from case_member.member_case import MemberCase

case_data_path = os.path.join(DATA_DIR, 'member_case_data.yaml')
datas = yaml.safe_load(open(case_data_path, encoding='utf-8'))


class TestMember(MemberCase):
    conf_data = MemberCase().get_yaml(CONFIG_DIR)

    @pytest.mark.parametrize('data', datas['login'])
    def test_login(self, data):
        logger.info(f'账户信息：{data["account"]}')
        result = self.login_api(**data['account']).json()
        logger.info(f'响应结果:{result}')
        HA().eq(data['expected']['code'], result['code'])
        HA().eq(data['expected']['msg'], result['msg'])

    @pytest.mark.parametrize('data', datas['register'])
    def test_register(self, data):
        logger.info(f'账户信息：{data["account"]}')
        result = self.case_register(data['account'])
        logger.info(f'响应结果:{result}')
        HA().eq(data['expected']['code'], result['code'])
        HA().eq(data['expected']['msg'], result['msg'])

    @pytest.mark.parametrize('connect_mysql', [conf_data['mysql']], indirect=True)
    @pytest.mark.parametrize('data', datas['recharge'])
    def test_recharge(self, data, get_login_data, connect_mysql):
        login_data = get_login_data
        db = connect_mysql
        logger.info(data)
        result = self.case_recharge(data, login_data, db)
        HA().eq(data['expected']['code'], result['code'])
        HA().eq(data['expected']['msg'], result['msg'])
        if data['sql']:
            HA().eq(self.to_two_decimal(data['amount']), result['recharge'])

    @pytest.mark.parametrize('connect_mysql', [conf_data['mysql']], indirect=True)
    @pytest.mark.parametrize('data', datas['withdraw'])
    def test_withdraw(self, data, get_login_data, connect_mysql):
        login_data = get_login_data
        db = connect_mysql
        logger.info(data)
        result = self.case_withdraw(data, login_data, db)
        logger.info(f'响应结果为：{result}')
        HA().eq(data['expected']['code'], result['code'])
        HA().eq(data['expected']['msg'], result['msg'])
        if data['sql']:
            HA().eq(self.to_two_decimal(data['amount']), result['withdraw'])
