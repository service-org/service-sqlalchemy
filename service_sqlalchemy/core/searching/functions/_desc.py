#! -*- coding: utf-8 -*-
#
# author: forcemain@163.com

import sqlalchemy as sa

from sqlalchemy.sql.functions import GenericFunction

from .base import BaseFunction


class DescFunction(BaseFunction):
    """ sqlalchemy.sql.expression.desc """

    alias = {'desc'}

    def eval(self) -> GenericFunction:
        """ 生成的函数

        @return: GenericFunction
        """
        return sa.desc(self.field, **self._param)
