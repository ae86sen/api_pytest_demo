"""
============================
Author:古一
Time:2020/11/10
E-mail:369799130@qq.com
============================
"""
from loguru import logger
import allure
from api_loan.loan_api import LoanApi
from common.handle_mysql import HandleMysql
from api_member.member_api import MemberApi
from jsonpath import jsonpath
from common.wrapper import log_info


class LoanCase(LoanApi):
    @log_info
    @allure.step('step:调用业务api-添加项目')
    def case_add_loan(self, data, login_data, db: HandleMysql = None):
        # 替换数据
        data = self.template(data, {'member_id': login_data['member_id']})
        if data['sql']:
            before_num: int = db.count(data['sql'])
            add_loan_response = self.add_loan_api(**data['json'], token=login_data['token'])
            res = add_loan_response.json()
            after_num: int = db.count(data['sql'])
            add_num = after_num - before_num
            res['add_num'] = add_num
        else:
            add_loan_response = self.add_loan_api(**data['json'], token=login_data['token'])
            res = add_loan_response.json()
        return res

    @log_info
    @allure.step('step:调用业务api-审核')
    def case_audit(self, data, login_data, db: HandleMysql = None):
        data = self.template(data, {'member_id': login_data['member_id']})
        # 添加项目
        add_loan_res = self.add_loan_api(**data['add_loan_json'], token=login_data['token']).json()
        loan_id = jsonpath(add_loan_res, '$..id')[0]
        # 审核
        audit_res = self.audit_loan_api(loan_id, data['audit_json']['approved_or_not']).json()
        audit_res['loan_id'] = loan_id
        if 'again' in data.keys():
            audit_res = self.audit_loan_api(loan_id, data['audit_json']['approved_or_not']).json()
        if 'sql' in data.keys() and data['sql']:
            data = self.template(data, {'loan_id': loan_id})
            status = db.get_one(data['sql'])[0]
            audit_res['status'] = status
        return audit_res

    @log_info
    @allure.step('step:调用业务api-投资')
    def case_invest(self, data, login_data, db: HandleMysql = None):

        member = MemberApi()
        # 管理员登录-加标-审核
        audit_res = self.case_audit(data, login_data)
        # 获取审核通过后的标的id
        pass_loan_id = audit_res['loan_id']
        # 投资人登录
        investor_account = member.conf_data['investor_account']
        # 获取投资人登录信息
        investor_login_data = member.get_login_data(**investor_account)
        data = self.template(data, {'invest_member_id': investor_login_data['member_id'],
                                    'loan_id': pass_loan_id})
        if data['check_sql']:
            before_investor_balance = investor_login_data['leave_amount']
            # 投资人投资
            invest_res = self.invest_loan_api(**data['invest_json'],
                                              token=investor_login_data['token']).json()
            invest_info = member.get_user_info_api(investor_login_data['member_id'],
                                                   investor_login_data['token']).json()
            after_investor_balance = invest_info['data']['leave_amount']
            # 投资人投资金额 = 投资前账户余额 - 投资后账户余额
            invest_amount = before_investor_balance - after_investor_balance
            # 投资完成后,invest表和financeLog表分别增加一条记录
            invest_num = db.count(data['check_sql']['check_invest'])
            finance_num = db.count(data['check_sql']['check_financeLog'])
            invest_res['invest_num'] = invest_num
            invest_res['financeLog_num'] = finance_num
            invest_res['invest_amount'] = self.to_two_decimal(invest_amount)
        else:
            invest_res = self.invest_loan_api(**data['invest_json'],
                                              token=investor_login_data['token']).json()
        return invest_res
