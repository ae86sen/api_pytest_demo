"""
============================
Author:古一
Time:2020/11/10
E-mail:369799130@qq.com
============================
"""
import os
import allure
import pytest
import yaml
from loguru import logger
from common.handle_assert import HandleAssert as HA
from common.handle_path import CONFIG_DIR, DATA_DIR
from case_loan.loan_case import LoanCase

case_data_path = os.path.join(DATA_DIR, 'loan_case_data.yaml')
datas = yaml.safe_load(open(case_data_path, encoding='utf-8'))


@allure.feature('项目')
class TestLoan(LoanCase):
    conf_data = LoanCase().get_yaml(CONFIG_DIR)

    @allure.story('添加项目')
    @allure.title('{data[title]}')
    @pytest.mark.zls
    @pytest.mark.parametrize('connect_mysql', [conf_data['mysql']], indirect=True)
    @pytest.mark.parametrize('data', datas['add_loan'])
    def test_add_loan(self, data, get_login_data, connect_mysql):
        login_data = get_login_data
        db = connect_mysql
        result = self.case_add_loan(data, login_data, db)
        logger.info(f'响应结果:{result}')
        HA().eq(data['expected']['code'], result['code'])
        HA().eq(data['expected']['msg'], result['msg'])
        if data['sql']:
            HA().eq(1, result['add_num'])

    @allure.story('审核项目')
    @allure.title('{data[title]}')
    # @pytest.mark.zls
    @pytest.mark.parametrize('connect_mysql', [conf_data['mysql']], indirect=True)
    @pytest.mark.parametrize('data', datas['audit'])
    def test_audit(self, data, get_login_data, connect_mysql):
        # allure.dynamic.description(f'测试数据为：{data["add_loan_json"]}\n'
        #                            f'测试步骤：\n1、管理员登录-加标-审核\n'
        #                            f'2、投资人登录-投资')
        login_data = get_login_data
        db = connect_mysql
        result = self.case_audit(data, login_data, db)
        logger.info(f'响应结果:{result}')
        HA().eq(data['expected']['code'], result['code'])
        HA().eq(data['expected']['msg'], result['msg'])
        if data['sql']:
            HA().eq(data['expected']['status'], result['status'])

    @allure.story('投资项目')
    @allure.title('{data[title]}')
    @pytest.mark.parametrize('connect_mysql', [conf_data['mysql']], indirect=True)
    @pytest.mark.parametrize('data', datas['invest'])
    def test_invest(self, data, get_login_data, connect_mysql):

        login_data = get_login_data
        db = connect_mysql
        result = self.case_invest(data, login_data, db)
        logger.info(f'响应结果:{result}')
        HA().eq(data['expected']['code'], result['code'])
        HA().eq(data['expected']['msg'], result['msg'])
        HA().eq(self.to_two_decimal(data['invest_json']['amount']), result['invest_amount'])
        if data['check_sql']:
            HA().eq(1, result['invest_num'])
            HA().eq(1, result['financeLog_num'])