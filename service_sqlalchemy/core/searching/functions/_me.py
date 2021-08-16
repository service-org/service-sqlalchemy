#! -*- coding: utf-8 -*-
#
# author: forcemain@163.com

from sqlalchemy.sql.functions import GenericFunction

from .base import BaseFunction


class MeFunction(BaseFunction):
    """ 返回模型字段自身 """

    alias = {'me'}

    def eval(self) -> GenericFunction:
        """ 生成的函数

        @return: GenericFunction
        """
        return self.field
