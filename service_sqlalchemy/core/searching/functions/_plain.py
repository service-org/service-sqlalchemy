#! -*- coding: utf-8 -*-
#
# author: forcemain@163.com


from sqlalchemy.sql.functions import GenericFunction

from .base import BaseFunction


class PlainFunction(BaseFunction):
    """ sqlalchemy.sql.expression.asc """

    alias = {'me', 'self', 'plain'}

    def eval(self) -> GenericFunction:
        """ 生成的函数

        @return: GenericFunction
        """
        return self.field
