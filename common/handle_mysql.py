"""
============================
Author:古一
Time:2020/10/28
E-mail:369799130@qq.com
============================
"""
import os

import pymysql
from loguru import logger

from common.handle_path import CONF_DIR
from common.base_api import BaseApi


class HandleMysql:
    def __init__(self, **kwargs):
        # 连接到数据库
        try:
            self.con = pymysql.connect(charset="utf8", **kwargs)
        except Exception as e:
            logger.error(f'数据库连接失败，连接参数：{kwargs}')
            raise e
        else:
            # 创建一个游标
            self.cur = self.con.cursor()

    def get_one(self, sql):
        """获取查询到的第一条数据"""
        self.con.commit()
        self.cur.execute(sql)
        return self.cur.fetchone()

    def get_all(self, sql):
        """获取sql语句查询到的所有数据"""
        self.con.commit()
        self.cur.execute(sql)
        return self.cur.fetchall()

    def count(self, sql):
        """获取sql语句查询到的数量"""
        self.con.commit()
        res = self.cur.execute(sql)
        return res

    def close(self):
        # 关闭游标对象
        self.cur.close()
        # 断开连接
        self.con.close()


if __name__ == '__main__':
    p = os.path.join(CONF_DIR, 'config.yaml')
    a = BaseApi()
    conf = a.get_yaml(p)
    mysql = conf['mysql']
    db = HandleMysql(**mysql)
    x = db.count('SELECT * FROM  futureloan.financeLog WHERE id=44708')
    print(x)
# id（用户id） loan_id(标id) amount creat_time  is_valid 0无效 1有效
# id