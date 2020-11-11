"""
============================
Author:古一
Time:2020/10/28
E-mail:369799130@qq.com
============================
"""
import allure
import requests
from jsonpath import jsonpath
from loguru import logger

from common.utils import Utils


class BaseApi:
    @staticmethod
    def send_http(data):
        try:
            response = requests.request(**data)
        except Exception as e:
            logger.error(f'发送请求失败，请求参数为：{data}')
            logger.exception(f'发生的错误为：{e}')
            raise e
        else:
            return response

    @staticmethod
    def get_yaml(file_name):
        """
        读取yaml文件
        :param file_name: 文件路径名称
        :return: dict
        """
        return Utils.handle_yaml(file_name)

    @staticmethod
    def get_token(response):
        """
        处理并提取token
        :param response:
        :return:
        """
        return Utils.handle_token(response)

    @staticmethod
    @allure.step('step:数据替换')
    def template(source_data: str, data: dict):
        """
        替换数据
        :param source_data: 源数据
        :param data: 替换内容，如{data:new_data}
        :return:
        """

        return Utils.handle_template(source_data, data)

    @staticmethod
    def to_two_decimal(data):
        """
        将整数或浮点数转化为两位数decimal
        :param data:
        :return:
        """
        return Utils.handle_decimal(data)

    @staticmethod
    def random_phone():
        """
        生成随机手机号
        :return:
        """
        return Utils.handle_random_phone()


if __name__ == '__main__':
    a = BaseApi()
    a.template()
