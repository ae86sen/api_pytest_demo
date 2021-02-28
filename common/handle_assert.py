import allure
from loguru import logger


class HandleAssert:

    @staticmethod
    @allure.step('step:断言')
    def eq(ex, re):
        """
        断言相等
        :param ex: 预期结果
        :param re: 实际结果
        :return:
        """
        try:
            assert str(ex) == str(re)
        except AssertionError as e:
            logger.error(f"eq断言失败，预期结果：{ex}，实际结果：{re}")
            logger.error("用例失败！")
            raise e

    @staticmethod
    def contains(content, target):
        """
        断言包含
        :param content: 文本内容
        :param target: 目标文本
        :return:
        """
        try:
            assert str(content) in str(target)
        except AssertionError as e:
            logger.error(f"contains断言失败，目标文本{target}包含 文本{content}")
            raise e
