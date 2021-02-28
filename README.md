### 设计说明

**API Object**是**Page Object**设计模式在接口测试上的一种延伸，顾名思义，这里是将各种基础接口进行了一层抽象封装，将其作为object，通过不同的API对象调用来组装成不同的业务流场景。因为ui自动化测试面临较多变更，所以Page Object模式的价值比较大，而如果是针对单接口的简单接口测试，其实接口层相对稳定，封装po的价值并不明显。

但是，实际项目中往往不仅是需要单接口自动化测试，更多且更有价值的是业务流的接口自动化测试，而业务流的接口测试，通常一个业务会有很多的接口依赖和调用，并且有些接口会有非常多的http协议字段填充，比如各种`headers`、`token`以及默认字段；有些接口会反复调用，比如提现业务中会调用获取账户id的接口，充值业务中也会涉及到获取账户id的接口；有些接口会有较多的处理，比如加解密等。而针对这些情况，尤其是当项目接口越来越多，业务越来越繁杂，API Object的优势就凸显出来了。（下面以一个贷款项目详细说明）

### 技术栈

- python
- requests
- pytest
- yaml
- 模板替换
- allure

### 分层设计

整个框架分为五层：`Base层`、`接口层`、`业务层`、`用例层`、`数据层`。

如图所示：

![](https://cdn.jsdelivr.net/gh/ae86sen/mypic2/img/api.png)

继承关系：用例层-->业务层-->接口层-->Base层。

调用关系：用例层（从数据层拿测试数据）-->业务层-->接口层-->Base层。

#### Base层

**baseapi**用于封装通用的接口流程方法，它代表的是通用接口的封装，用于跟各个api object提供支持，如提供发送http请求、读取yaml文件、替换数据等公共方法，而无关业务逻辑。

```python
import os

import allure
import requests
from loguru import logger

from common.handle_assert import HandleAssert
from common.handle_path import CONF_DIR
from common.utils import Utils


class BaseApi:
    conf_path = os.path.join(CONF_DIR, 'config.yaml')
    # 配置文件数据
    conf_data = Utils().handle_yaml(conf_path)
    host = conf_data['env']['host']
    headers = conf_data['request_headers']['headers']
    account = conf_data['account']
    investor_account = conf_data['investor_account']
    mysql_conf = conf_data['mysql']

    def send_http(self, data:dict):
        """
        发送http请求
        :param data: 请求数据
        :return:
        """
        try:
            self.__api_log(**data)
            response = requests.request(**data)
            logger.info(f"响应结果为：{response.status_code}")
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

    @staticmethod
    def __api_log(method, url, headers=None, params=None, json=None):
        logger.info(f"请求方式：{method}")
        logger.info(f"请求地址：{url}")
        logger.info(f"请求头：{headers}")
        logger.info(f"请求参数：{params}")
        logger.info(f"请求体：{json}")

    @staticmethod
    def assert_equal(ex, re):
        """
        断言相等
        :param ex:预期结果
        :param re:实际结果
        :return:
        """
        return HandleAssert.eq(ex, re)

    @staticmethod
    def assert_contains(content, target):
        """
        断言包含
        :param content: 文本内容
        :param target: 目标文本
        :return:
        """
        return HandleAssert.contains(content, target)


```

此外，`baseapi`的核心只关心api的通用逻辑（遵循设计模式中单一职责原则），所以这里对`baseapi`做了瘦身，解耦了无关逻辑（ 比如它不需要关心yaml用哪个库，能搞定就行 ），因此将工具方法单独封装到`utils.py`模块中，`baseapi`只需调用即可。

*utils.py*

```python
import yaml
from jsonpath import jsonpath
from loguru import logger
from decimal import Decimal
from string import Template
from faker import Faker


class Utils:
    """提供工具方法"""
    @classmethod
    def handle_yaml(cls, file_name):
        """
        读取yaml文件
        :param file_name:
        :return:
        """
        try:
            yaml_data = yaml.safe_load(open(file_name, encoding='utf-8'))
        except Exception as e:
            logger.error(f'yaml文件读取失败，文件名称：{file_name}')
            raise e
        else:
            return yaml_data

    @classmethod
    def handle_token(cls, response):
        """
        组装token
        :param response:
        :return:
        """
        token_type = jsonpath(response.json(), '$..token_type')[0]
        token_value = jsonpath(response.json(), '$..token')[0]
        token = f'{token_type} {token_value}'
        return token

    @classmethod
    def handle_template(cls, source_data, replace_data: dict, ):
        """
        替换文本变量
        :param source_data:
        :param replace_data:
        :return:
        """
        res = Template(str(source_data)).safe_substitute(**replace_data)
        return yaml.safe_load(res)

    @classmethod
    def handle_decimal(cls, data: int):
        """
        将小数或整数转换为两位数decimal
        :param data:
        :return:
        """
        x = '{0:.2f}'.format(float(data))
        return Decimal(x)

    @classmethod
    def handle_random_phone(cls):
        """
        生成随机手机号
        :return:
        """
        fake = Faker(locale='zh_CN')
        phone_number = fake.phone_number()
        return phone_number
```

#### 接口层

接口层是对所有基础单接口的封装，负责http协议的填充。

```python
import os

import allure
from jsonpath import jsonpath

from common.base_api import BaseApi
from common.wrapper import api_call


class MemberApi(BaseApi):

    @api_call
    def login_api(self, user=BaseApi().account['user'], pwd=BaseApi().account['pwd']):
        """
        登录接口
        :return:
        """
        api = self.conf_data['member_api']['login']
        data = {
            'url': self.host + api,
            'method': 'post',
            'headers': self.headers,
            'json': {
                'mobile_phone': user,
                'pwd': pwd
            }
        }
        response = self.send_http(data)
        return response

    @allure.step('step:调用获取登录结果api')
    def get_login_data(self, user=BaseApi().account['user'], pwd=BaseApi().account['pwd']):
        """
        提取处理登录响应数据，包括id、leave_amount、mobile_phone、reg_name

        :return:
        """
        response = self.login_api(user, pwd)
        res = response.json()
        login_data = dict()
        login_data['token'] = self.get_token(response)
        login_data['member_id'] = jsonpath(res, '$..id')[0]
        login_data['leave_amount'] = jsonpath(res, '$..leave_amount')[0]
        login_data['mobile_phone'] = jsonpath(res, '$..mobile_phone')[0]
        login_data['reg_name'] = jsonpath(res, '$..reg_name')[0]
        return login_data

    @api_call
    def register_api(self, mobile_phone: str, pwd: str, member_type: int, reg_name=None):
        """
        注册接口
        :param mobile_phone: 手机号
        :param pwd: 密码
        :param member_type: 0-管理员，1-普通会员，不传默认为1
        :param reg_name:注册名
        :return:
        """
        api = self.conf_data['member_api']['register']
        data = {
            'url': self.host + api,
            'method': 'post',
            'headers': self.headers,
            'json': {
                'mobile_phone': mobile_phone,
                'pwd': pwd,
                'type': member_type,
                # 'reg_name': reg_name
            }
        }
        if reg_name:
            data['json']['reg_name'] = reg_name
        response = self.send_http(data)
        return response

    @api_call
    def recharge_api(self, member_id: int, amount: float, token):
        """
        账户充值接口
        :param member_id: 用户id
        :param amount: 充值金额（最多小数点后两位）
        :param token:
        :return:
        """
        api = self.conf_data['member_api']['recharge']
        data = {
            'url': self.host + api,
            'method': 'post',
            'headers': self.headers,
            'json': {
                'member_id': member_id,
                'amount': amount
            }
        }
        data['headers'].update({'Authorization': token})
        response = self.send_http(data)
        return response

    @api_call
    def withdraw_api(self, member_id: int, amount: float, token):
        """
        账户提现接口
        :param member_id: 用户id
        :param amount: 提现金额（最多小数点后两位）
        :param token:
        :return:
        """
        api = self.conf_data['member_api']['withdraw']
        data = {
            'url': self.host + api,
            'method': 'post',
            'headers': self.headers,
            'json': {
                'member_id': member_id,
                'amount': amount
            }
        }
        self.headers['Authorization'] = token
        response = self.send_http(data)
        return response

    @api_call
    def info_update_api(self, member_id: int, reg_name: str, token):
        """
        用户信息更新接口
        :param member_id:用户id
        :param reg_name:修改名称
        :param token:
        :return:
        """
        api = self.conf_data['member_api']['update']
        data = {
            'url': self.host + api,
            'method': 'patch',
            'headers': self.headers,
            'json': {
                'member_id': member_id,
                'reg_name': reg_name
            }
        }
        # data['headers'].update({'Authorization': token})
        self.headers['Authorization'] = token
        response = self.send_http(data)
        return response

    @api_call
    def get_user_info_api(self, member_id, token):
        """
        获取单个用户信息接口
        :param member_id:用户id
        :param token:
        :return:
        """
        data = {
            'url': self.host + f'/member/{member_id}/info',
            'method': 'get',
            'headers': self.headers,
        }
        self.headers['Authorization'] = token
        response = self.send_http(data)
        return response


```

所有api进行http协议填充后，发送http请求并返回response，供后续对响应结果进行相关处理。

#### 业务层

这一层，即业务流层，完成测试数据的组装并且通过调用不同的接口来实现具体业务逻辑。

```python
from decimal import Decimal

import allure
from loguru import logger

from common.wrapper import log_info
from api_member.member_api import MemberApi
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

```

#### 用例层

这一层，通过调用不同的业务，来完成相关测试。用例层不关心底层逻辑，比如某个业务具体是如何实现的，测试数据是具体如何清洗组装的，它只关心测试逻辑，这个业务场景如何测试，如何断言。

```python
import os

import allure
import pytest
import yaml
from loguru import logger

from common.handle_path import DATA_DIR
from case_member.member_case import MemberCase

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

```

如果在测试用例中直接塞进去各种http协议的填充过程，会导致用例慢慢的丢失重心，尤其是当业务越来越繁杂后，用例会非常臃肿难以维护。测试用例还是要围绕业务进行，业务要围绕实现进行，通过分层可以让用例更优雅更简洁。

#### 数据层

测试数据（测试用例）通过`yaml`管理维护，结合`pytest.paramtrize`可以非常轻松完成数据驱动。在用例层获取yaml中的测试数据，然后将数据打包给业务层，业务层进行数据拆卸组装给到接口层，接口层再封装为http请求格式进行接口请求。这样当测试数据发生变化或者用例更新，我们将不用去更新测试代码，只需维护这份yaml文件即可。

```yaml
# 登录接口
login:
  - title: '确认输入正确账号密码登录成功'
    account:
      user: '15882345570'
      pwd: 'admin123'
    expected: {"code": 0,"msg": "OK"}

  - 'title': '验证手机号为空登录失败'
    account:
      'user': ''
      'pwd': 'admin123'
    'expected': {"code": 1,"msg": "手机号码为空"}

  - 'title': '验证密码为空登录失败'
    account:
      'user': '15882345570'
      'pwd': ''
    'expected': {"code": 1,"msg": "密码为空"}

  - 'title': '验证手机号未注册登录失败'
    'account':
      'user': '15880000000'
      'pwd': 'admin123'
    'expected': {"code": 1001,"msg": "账号信息错误"}

  - 'title': '验证密码错误登录失败'
    'account':
      'user': '15882345570'
      'pwd': '123123'
    'expected': {"code": 1001,"msg": "账号信息错误"}

  - 'title': '验证手机号格式错误登录失败'
    'account':
      'user': '12345678910'
      'pwd': '123123'
    'expected': {"code": 2,"msg": "无效的手机格式"}

# 注册接口
register:
  - title: '确认带注册名注册成功'
    account:
      mobile_phone: '$mobile_phone'
      pwd: 'admin123'
      member_type: '1'
      reg_name: '派大星'
    expected: {"code": 0,"msg": "OK"}

  - title: '确认不带注册名注册成功'
    account:
      mobile_phone: '$mobile_phone'
      pwd: 'admin123'
      member_type: '1'
    expected: {"code": 0,"msg": "OK"}

  - title: '验证不输入手机号注册失败'
    account:
      mobile_phone: ''
      pwd: 'admin123'
      member_type: '1'
    expected: {"code": 1,"msg": "手机号为空"}

  - title: '验证手机号长度为10位注册失败'
    account:
      mobile_phone: '1351514174'
      pwd: 'admin123'
      member_type: '1'
    expected: {"code": 2,"msg": "无效的手机格式"}

  - title: '验证手机号长度为12位注册失败'
    account:
      mobile_phone: '135151417444'
      pwd: 'admin123'
      member_type: '1'
    expected: {"code": 2,"msg": "无效的手机格式"}

  - title: '验证使用已注册手机号注册失败'
    account:
      mobile_phone: '15882345570'
      pwd: 'admin123'
      member_type: '1'
    expected: {"code": 2,"msg": "账号已存在"}

  - title: '验证密码为7位注册失败'
    account:
      mobile_phone: '$mobile_phone'
      pwd: 'admin12'
      member_type: '1'
    expected: {"code": 2,"msg": "密码格式为8到16位"}

  - title: '验证不输入密码注册失败'
    account:
      mobile_phone: '$mobile_phone'
      pwd: ''
      member_type: '1'
    expected: {"code": 1,"msg": "密码为空"}

  - title: '验证注册名11位注册失败'
    account:
      mobile_phone: '$mobile_phone'
      pwd: 'admin123'
      member_type: '1'
      reg_name: '12345678901'
    expected: {"code": 2,"msg": "用户昵称长度超过10位"}

  - title: '验证type类型为2注册失败'
    account:
      mobile_phone: '$mobile_phone'
      pwd: 'admin123'
      member_type: '2'
    expected: {"code": 2,"msg": "不支持的用户类型"}

  - title: '验证不输入类型注册失败'
    account:
      mobile_phone: '$mobile_phone'
      pwd: 'admin123'
      member_type: ''
    expected: {"code": 0,"msg": "OK"}

# 充值接口
recharge:
  - 'title': '验证充值金额为整数充值成功'
    'member_id': '$member_id'
    'amount': 600
    'expected': {"code": 0,"msg": "OK"}
    'sql': 'SELECT leave_amount FROM futureloan.member WHERE mobile_phone="$mobile_phone"'

  - 'title': '验证充值金额为1位小数充值成功'
    'member_id': '$member_id'
    'amount': 600.1
    'expected': {"code": 0,"msg": "OK"}
    'sql': 'SELECT leave_amount FROM futureloan.member WHERE mobile_phone="$mobile_phone"'

  - 'title': '验证充值金额为2位小数充值成功'
    'member_id': '$member_id'
    'amount': 600.22
    'expected': {"code": 0,"msg": "OK"}
    'sql': 'SELECT leave_amount FROM futureloan.member WHERE mobile_phone="$mobile_phone"'

  - 'title': '验证充值金额为50万充值成功'
    'member_id': '$member_id'
    'amount': 500000
    'expected': {"code": 0,"msg": "OK"}
    'sql': 'SELECT leave_amount FROM futureloan.member WHERE mobile_phone="$mobile_phone"'

  - 'title': '验证会员id为空充值失败'
    'member_id': ''
    'amount': 600
    'expected': {"code": 1,"msg": "用户id为空"}
    'sql': ''

  - 'title': '验证会员id不是当前登录的用户充值失败'
    'member_id': '98999888'
    'amount': 600
    'expected': {"code": 1007,"msg": "无权限访问，请检查参数"}
    'sql': ''

  - 'title': '验证充值金额为0充值失败'
    'member_id': '$member_id'
    'amount': 0
    'expected': {"code": 2,"msg": "余额必须大于0并且小于或者等于500000"}
    'sql': ''

  - 'title': '验证会员id为字符串充值失败'
    'member_id': 'abcde'
    'amount': 600
    'expected': {"code": 2,"msg": "数字格式化异常"}
    'sql': ''

  - 'title': '验证充值金额为负数充值失败'
    'member_id': '$member_id'
    'amount': -600
    'expected': {"code": 2,"msg": "余额必须大于0并且小于或者等于500000"}
    'sql': ''

  - 'title': '验证充值金额大于50万充值失败'
    'member_id': '$member_id'
    'amount': 1000000
    'expected': {"code": 2,"msg": "余额必须大于0并且小于或者等于500000"}
    'sql': ''

#提现接口
withdraw:
  - 'title': '验证提现金额为整数提现成功'
    'member_id': '$member_id'
    'amount': 600
    'expected': {"code": 0,"msg": "OK"}
    'sql': 'SELECT leave_amount FROM futureloan.member WHERE mobile_phone="$mobile_phone"'

  - 'title': '验证提现金额为1位小数提现成功'
    'member_id': '$member_id'
    'amount': 600.1
    'expected': {"code": 0,"msg": "OK"}
    'sql': 'SELECT leave_amount FROM futureloan.member WHERE mobile_phone="$mobile_phone"'

  - 'title': '验证提现金额为2位小数提现成功'
    'member_id': '$member_id'
    'amount': 600.22
    'expected': {"code": 0,"msg": "OK"}
    'sql': 'SELECT leave_amount FROM futureloan.member WHERE mobile_phone="$mobile_phone"'

  - 'title': '验证提现金额为50万提现成功'
    'member_id': '$member_id'
    'amount': 500000
    'expected': {"code": 0,"msg": "OK"}
    'sql': 'SELECT leave_amount FROM futureloan.member WHERE mobile_phone="$mobile_phone"'

  - 'title': '验证会员id为空提现失败'
    'member_id': ''
    'amount': 600
    'expected': {"code": 1,"msg": "用户id为空"}
    'sql': ''

  - 'title': '验证提现金额为空提现失败'
    'member_id': '$member_id'
    'amount': 600
    'expected': {"code": 1,"msg": "余额为空"}
    'sql': ''

  - 'title': '验证提现金额为3位小数提现失败'
    'member_id': '$member_id'
    'amount': 600.333
    'expected': {"code": 2,"msg": "余额小数超过两位"}
    'sql': ''
```

### 项目结构说明

- apis ---->接口层，单接口封装
- cases ---->业务层，业务场景封装
- common  ---->公共方法
  - base_api ---->baseapi层
  - handle_assert ---->断言封装
  - handle_mysql ---->mysql数据库操作封装
  - handle_path ---->路径处理
  - utils ---->工具方法封装
  - wrapper ---->日志装饰器

- conf ---->配置文件
- data ---->测试数据
- log --->日志
- report --->测试报告
- testcases  --->测试用例
- conftest  --->前置条件处理
- pytest.ini  --->pytest配置文件
- run.py  --->测试用例运行主程序

### 接口依赖处理

#### token

`token`或者`cookies`需要登录获取，后续其它接口大多需要其鉴权，因此将登录接口作为前置条件放于`conftest.py`中。

*conftest.py*

```python
# 为了避免频繁登录，级别可以根据需求设置
# 这里整个class只会调用一次登录
@pytest.fixture(scope='class')
def get_login_data():
    """获取登录数据"""
    data = MemberApi().get_login_data()
    # 如果只需要token，可以直接返回token
    return data
```

这里返回的不是`token`，而是整个登录响应结果（字典），其中还包含了用户id、余额、token等信息，是因为其它接口还可能需要除token外的其它登录信息，而其它接口需要什么登录信息，直接字典取值即可。

```python
    def get_login_data(self, user=BaseApi().account['user'], pwd=BaseApi().account['pwd']):
        """
        提取处理登录响应数据，包括id、leave_amount、mobile_phone、reg_name

        :return:
        """
        response = self.login_api(user, pwd)
        res = response.json()
        login_data = dict()
        login_data['token'] = self.get_token(response)
        login_data['member_id'] = jsonpath(res, '$..id')[0]
        login_data['leave_amount'] = jsonpath(res, '$..leave_amount')[0]
        login_data['mobile_phone'] = jsonpath(res, '$..mobile_phone')[0]
        login_data['reg_name'] = jsonpath(res, '$..reg_name')[0]
        return login_data
```

如何获取传递token呢？

在用例中调用`conftest.py`的`get_login_data()`即可。

```python
    def test_demo(self, get_login_data):
        login_data = get_login_data
        token = login_data["token"]
```

#### 测试数据动态处理

测试数据中的参数有时候不能写死，而是动态变化由上一个接口的返回值中获取的。而本框架的测试数据又都是由yaml管理，那么如何能让yaml中的测试数据“动”起来呢？

本框架采用的是**模板引擎替换**技术。

举个栗子，比如在调用充值接口充值的时候，那么肯定要先拿到具体的需要充值的账户id，而账户id是由登录接口获取的，因此在构造充值测试数据时，账户id不能写死，而是以`$`标记，先调用登录接口拿到账户id，然后替换掉充值接口测试数据中的变量。

```yaml
recharge:
  - 'title': '验证充值金额为整数充值成功'
  	# 以$标记表明该参数是动态变换，需要由实参来替换
    'member_id': '$member_id'
    'amount': 600
    'expected': {"code": 0,"msg": "OK"}
```

具体替换方法，由python内置模块`string`实现：

```python
from string import Template
def handle_template(cls, source_data, replace_data: dict, ):
    """
        替换文本变量
        :param source_data:源数据
        :param replace_data:需要替换的变量，如{'member_id': '12345'}
        :return:
        """
    res = Template(str(source_data)).safe_substitute(**replace_data)
    return yaml.safe_load(res)
```

### 测试报告

运行`run.py`后，当用例全部执行完毕，`allure`会自动收集测试报告到`/report/html/`中，打开`index.html`即可看到完整测试报告。

![](https://cdn.jsdelivr.net/gh/ae86sen/mypic2/img/rr.jpg)