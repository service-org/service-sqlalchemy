#! -*- coding: utf-8 -*-
#
# author: forcemain@163.com

from __future__ import annotations

from sqlalchemy.sql.elements import BinaryExpression
from service_sqlalchemy.exception import ValidationError

from .base import BaseOperator


class NotInOperator(BaseOperator):
    """ https://docs.sqlalchemy.org/en/14/core/sqlelement.html#sqlalchemy.sql.expression.ColumnOperators.not_in """

    alias = {'notin', 'not_in'}

    def expr(self) -> BinaryExpression:
        """ 构造表达式

        @return: BinaryExpression
        """
        if not hasattr(self._value, '__iter__'):
            errs = f'{self._field} must be iterable'
            raise ValidationError(errormsg=errs)
        return self.field.not_in(self._value)
