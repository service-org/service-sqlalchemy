#! -*- coding: utf-8 -*-
#
# author: forcemain@163.com

from sqlalchemy.sql.functions import GenericFunction

from .base import BaseFunction


class LengthFunction(BaseFunction):
    """ sqlalchemy.sql.func.length """

    alias = {'length'}

    def eval(self) -> GenericFunction:
        """ 生成的函数

        @return: GenericFunction
        """

        return self.func(self.field, **self._param)
