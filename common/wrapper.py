"""
============================
Author:古一
Time:2020/11/12
E-mail:369799130@qq.com
============================
"""
from loguru import logger


def log_info(func):
    """
    日志装饰器，简单记录函数输入输出
    :param func: 装饰的函数
    :return:
    """
    def inner(*args, **kwargs):
        res = func(*args, **kwargs)
        logger.info(f'\n调用函数:{func.__name__},\n传入参数：{args, kwargs},\n响应结果：{res}')
        return res

    return inner
