#! -*- coding: utf-8 -*-
#
# author: forcemain@163.com

from __future__ import annotations

from sqlalchemy.sql.elements import BinaryExpression
from service_sqlalchemy.exception import ValidationError

from .base import BaseOperator


class BetweenOperator(BaseOperator):
    """ https://docs.sqlalchemy.org/en/14/core/sqlelement.html#sqlalchemy.sql.expression.ColumnOperators.between """

    alias = {'contains'}

    def expr(self) -> BinaryExpression:
        """ 构造表达式

        @return: BinaryExpression
        """
        if not isinstance(self._value, list):
            errs = f'{self._field} must be list'
            raise ValidationError(errormsg=errs)
        if len(self._value) != 2:
            errs = f'{self._field} != 2 items'
            raise ValidationError(errormsg=errs)
        return self.field.between(*self._value, **self._param)
