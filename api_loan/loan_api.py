"""
============================
Author:古一
Time:2020/11/9
E-mail:369799130@qq.com
============================
"""
import os

import allure
from jsonpath import jsonpath

from common.base_api import BaseApi
from common.handle_path import CONF_DIR


# conf_path = os.path.join(CONF_DIR, 'config.yaml')


class LoanApi(BaseApi):
    # conf_data = BaseApi().get_yaml(conf_path)
    # host = conf_data['env']['host']
    # headers = conf_data['request_headers']['headers']

    @allure.step('调用添加项目接口')
    def add_loan_api(self, member_id: int, title, amount, loan_rate, loan_term: int,
                     loan_date_type: int, bidding_days: int, token):
        """
        添加项目接口
        :param member_id: 用户id
        :param title: 项目标题
        :param amount: 借款金额
        :param loan_rate: 年利率，如18.0%，传18.0
        :param loan_term: 借款期限,如6个月为 6,此时 loan_date_type 为 1,30天为30,此时loan_date_type为2
        :param loan_date_type: 借款期限类型,1-按月 2-按天
        :param bidding_days: 竞标天数,1-10天
        :param token:
        :return:
        """
        api = self.conf_data['loan_api']['add']
        data = {
            'url': self.host + api,
            'method': 'post',
            'headers': self.headers,
            'json': {
                'member_id': member_id,
                'title': title,
                'amount': amount,
                'loan_rate': loan_rate,
                'loan_term': loan_term,
                'loan_date_type': loan_date_type,
                'bidding_days': bidding_days
            }
        }
        # data['headers'].update({'Authorization': token})
        self.headers['Authorization'] = token
        response = self.send_http(data)
        return response

    def audit_loan_api(self, loan_id: int, approval_result: bool):
        """
        项目审核接口
        :param loan_id: 项目id
        :param approval_result: 审核结果，True-通过，False-不通过
        :return:
        """
        api = self.conf_data['loan_api']['audit']
        data = {
            'url': self.host + api,
            'method': 'patch',
            'headers': self.headers,
            'json': {
                'loan_id': loan_id,
                'approved_or_not': approval_result
            }
        }
        response = self.send_http(data)
        return response

    @allure.step('step:调用投资api')
    def invest_loan_api(self, member_id, loan_id, amount, token):
        api = self.conf_data['member_api']['invest']
        data = {
            'url': self.host + api,
            'method': 'post',
            'headers': self.headers,
            'json': {
                'member_id': member_id,
                'loan_id': loan_id,
                'amount': amount
            }
        }
        # data['headers'].update({'Authorization': token})
        self.headers['Authorization'] = token
        response = self.send_http(data)
        return response

    def loan_list_api(self):
        api = self.conf_data['loan_api']['loan_list']
        data = {
            'url': self.host + api,
            'method': 'get',
            'headers': self.headers,
            'params': {
                'pageIndex': 1,
                'pageSize': 10
            }
        }
        response = self.send_http(data)
        return response



