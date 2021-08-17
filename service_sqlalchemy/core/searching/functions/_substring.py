#! -*- coding: utf-8 -*-
#
# author: forcemain@163.com


from sqlalchemy.sql.functions import GenericFunction

from .base import BaseFunction


class SubstringFunction(BaseFunction):
    """ sqlalchemy.sql.func.substring """

    alias = {'substring'}

    def eval(self) -> GenericFunction:
        """ 生成的函数

        @return: GenericFunction
        """
        if isinstance(self.field, list):
            field = self.field
        else:
            field = [self.field]
        return self.func(*field, **self._param)
