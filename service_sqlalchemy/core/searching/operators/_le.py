#! -*- coding: utf-8 -*-
#
# author: forcemain@163.com

from __future__ import annotations

from sqlalchemy.sql.elements import BinaryExpression

from .base import BaseOperator


class LessThanEqualsOperator(BaseOperator):
    """ https://docs.sqlalchemy.org/en/14/core/sqlelement.html#sqlalchemy.sql.expression.ColumnElement.__le__ """

    alias = {'<=', 'le', 'lte', 'less_than_equal', 'less_than_equals'}

    def expr(self) -> BinaryExpression:
        """ 构造表达式

        @return: BinaryExpression
        """
        return self.field <= self._value  # type: ignore
