"""
============================
Author:古一
Time:2020/10/28
E-mail:369799130@qq.com
============================
"""

# 项目目录的路径 | 如果运行的时候项目目录路径出错，使用上面abspath的方式来获取当前文件的绝对路径
import os

BASEDIR = os.path.dirname(os.path.dirname(__file__))
# 配置文件的路径
CONF_DIR = os.path.join(BASEDIR, "conf")
CONFIG_DIR = os.path.join(CONF_DIR, 'config.yaml')
# 用例数据的目录
DATA_DIR = os.path.join(BASEDIR, "data")
# 日志文件目录
LOG_DIR = os.path.join(BASEDIR, "log")
# 测试报告的路
REPORT_DIR = os.path.join(BASEDIR, "reports")
# 测试用例模块所在的目录
CASE_DIR = os.path.join(BASEDIR, "testcases")
