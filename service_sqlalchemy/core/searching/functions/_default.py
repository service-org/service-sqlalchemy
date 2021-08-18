#! -*- coding: utf-8 -*-
#
# author: forcemain@163.com

from sqlalchemy.sql.functions import GenericFunction

from .base import BaseFunction


class DefaultFunction(BaseFunction):
    """ https://docs.sqlalchemy.org/en/14/core/functions.html """

    alias = {'default'}

    def eval(self) -> GenericFunction:
        """ 生成的函数

        @return: GenericFunction
        """
        if isinstance(self.field, list):
            field = self.field
        else:
            field = [self.field]
        return self.func(*field, **self._param)
