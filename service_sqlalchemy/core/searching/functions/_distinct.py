#! -*- coding: utf-8 -*-
#
# author: forcemain@163.com

from sqlalchemy import distinct
from sqlalchemy.sql.functions import GenericFunction

from .base import BaseFunction


class DistinctFunction(BaseFunction):
    """ sqlalchemy.sql.expression.distinct """

    alias = {'distinct'}

    def eval(self) -> GenericFunction:
        """ 生成的函数

        @return: GenericFunction
        """
        return distinct(self.field)
