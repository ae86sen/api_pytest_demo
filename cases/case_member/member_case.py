from decimal import Decimal

import allure
from loguru import logger

from apis.api_member.member_api import MemberApi
from common.handle_mysql import HandleMysql


class MemberCase(MemberApi):
    @allure.step('step:调用业务api-注册')
    def case_register(self, data):
        """
        注册业务场景
        :param data:
        :return:
        """
        data = self.template(data, {'mobile_phone': self.random_phone()})
        res = self.register_api(**data).json()
        return res

    @allure.step('step:调用业务api-充值')
    def case_recharge(self, data, login_data, db: HandleMysql):
        """
        账户充值业务场景
        :param data: 充值接口所需参数
        :param login_data: 登录响应结果提取
        :param db: 数据库连接对象
        :return:
        """
        # 替换数据
        data = self.template(data, {'member_id': login_data['member_id'],
                                    'mobile_phone': login_data['mobile_phone']})
        # logger.info(f'替换后的数据:{data}')
        if data['sql']:
            # 充值前账户余额
            try:
                before_balance: Decimal = db.get_one(data['sql'])[0]
            except Exception as e:
                logger.error('报错了')
                logger.exception(e)
                raise e
            # logger.info(f'充值前账户余额：{before_balance}')
            recharge_response = self.recharge_api(data['member_id'], data['amount'], login_data['token'])
            res = recharge_response.json()
            # 充值后账户余额
            after_balance: Decimal = db.get_one(data['sql'])[0]
            # logger.info(f'充值后账户余额：{after_balance}')
            recharge: Decimal = after_balance - before_balance
            # logger.info(f'充值金额：{recharge}')
            res['recharge'] = recharge
        else:
            recharge_response = self.recharge_api(data['member_id'], data['amount'], login_data['token'])
            res = recharge_response.json()
        return res

    @allure.step('step:调用业务api-提现')
    def case_withdraw(self, data, login_data, db: HandleMysql):
        """
        账户提现业务场景
        :param data: 提现接口所需参数
        :param login_data: 登录响应结果提取
        :param db: 数据库连接对象
        :return:
        """
        # 替换数据
        data = self.template(data, {'member_id': login_data['member_id'],
                                    'mobile_phone': login_data['mobile_phone']})
        if data['sql']:
            # 充值前账户余额
            before_balance: Decimal = db.get_one(data['sql'])[0]
            withdraw_response = self.withdraw_api(data['member_id'], data['amount'], login_data['token'])
            res = withdraw_response.json()
            # 充值后账户余额
            after_balance: Decimal = db.get_one(data['sql'])[0]
            withdraw: Decimal = before_balance - after_balance
            res['withdraw'] = withdraw
        else:
            recharge_response = self.recharge_api(data['member_id'], data['amount'], login_data['token'])
            res = recharge_response.json()
        return res
