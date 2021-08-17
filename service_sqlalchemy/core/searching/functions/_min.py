#! -*- coding: utf-8 -*-
#
# author: forcemain@163.com

from sqlalchemy.sql.functions import GenericFunction

from .base import BaseFunction


class MinFunction(BaseFunction):
    """ https://docs.sqlalchemy.org/en/14/core/functions.html#sqlalchemy.sql.functions.min """

    alias = {'min'}

    def eval(self) -> GenericFunction:
        """ 生成的函数

        @return: GenericFunction
        """
        return self.func(self.field, **self._param)
