#! -*- coding: utf-8 -*-
#
# author: forcemain@163.com

from sqlalchemy.sql.functions import GenericFunction

from .base import BaseFunction


class LowerFunction(BaseFunction):
    """ sqlalchemy.sql.func.lower """

    alias = {'lower'}

    def eval(self) -> GenericFunction:
        """ 生成的函数

        @return: GenericFunction
        """

        return self.func(self.field, **self._param)
