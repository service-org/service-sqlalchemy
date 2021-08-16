#! -*- coding: utf-8 -*-
#
# author: forcemain@163.com

from __future__ import annotations

from sqlalchemy.sql.elements import BinaryExpression
from service_sqlalchemy.exception import ValidationError

from .base import BaseOperator


class MatchOperator(BaseOperator):
    """ https://docs.sqlalchemy.org/en/14/core/sqlelement.html#sqlalchemy.sql.expression.ColumnOperators.match """

    alias = {'match'}

    def expr(self) -> BinaryExpression:
        """ 构造表达式

        @return: BinaryExpression
        """
        if not isinstance(self._value, str):
            errs = f'{self._field} must be string'
            raise ValidationError(errormsg=errs)
        return self.field.match(self._value, **self._param)
