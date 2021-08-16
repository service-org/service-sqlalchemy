#! -*- coding: utf-8 -*-
#
# author: forcemain@163.com

from __future__ import annotations

from sqlalchemy.sql.elements import BinaryExpression
from service_sqlalchemy.exception import ValidationError

from .base import BaseOperator


class NotInOperator(BaseOperator):
    """ https://docs.sqlalchemy.org/en/14/core/sqlelement.html#sqlalchemy.sql.expression.ColumnOperators.notin_ """

    alias = {'notin', 'not_in'}

    def expr(self) -> BinaryExpression:
        """ 构造表达式

        @return: BinaryExpression
        """
        if hasattr(self._value, '__iter__'):
            return self.field.notin_(self._value)
        errs = f'{self._field} must be iterable'
        raise ValidationError(errormsg=errs)
