import allure
from loguru import logger


class HandleAssert:

    @staticmethod
    @allure.step('step:断言')
    def eq(ex, re):
        try:
            assert str(ex) == str(re)
            return True
        except Exception as e:
            logger.error(f"eq断言失败，预期结果：{ex}，实际结果：{re}")
            logger.error("用例失败！")
            raise e

    @staticmethod
    def contains(ex, re):
        try:
            assert str(ex) in str(re)
            return True
        except Exception as e:
            logger.error(f"contains断言失败，预期结果：{ex}，实际结果：{re}")
            # logger.exception(f'发生的错误为：{e}')
            raise e

    @staticmethod
    def not_contains(ex, re):
        try:
            assert str(ex) not in str(re)
            return True
        except Exception as e:
            logger.error(f"not_contains断言失败，预期结果：{ex}，实际结果：{re}")
            # logger.exception(f'发生的错误为：{e}')
            raise e

    def assert_result(self, assert_type, ex, re):
        """
        根据断言类型调用对应的断言方法
        :param assert_type:
        :param ex:
        :param re:
        :return:
        """
        try:
            if assert_type == "eq":
                return self.eq(ex, re)
            elif assert_type == "contains":
                return self.contains(ex, re)
            elif assert_type == "not_contains":
                return self.not_contains(ex, re)
        except Exception as e:
            logger.error(f"出现了非法的比较类型或者比较结果：{assert_type}")
            # logger.exception(f'发生的错误为：{e}')
            raise e
