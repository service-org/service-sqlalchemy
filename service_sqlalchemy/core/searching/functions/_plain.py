#! -*- coding: utf-8 -*-
#
# author: forcemain@163.com


from sqlalchemy.sql.functions import GenericFunction

from .base import BaseFunction


class PlainFunction(BaseFunction):
    """ 返回原始数据内容 """

    alias = {'me', 'self', 'plain'}

    def eval(self) -> GenericFunction:
        """ 生成的函数

        @return: GenericFunction
        """
        return self.field
