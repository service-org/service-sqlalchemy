#! -*- coding: utf-8 -*-
#
# author: forcemain@163.com

from __future__ import annotations

from sqlalchemy.sql.elements import BinaryExpression

from .base import BaseOperator


class NotEqualsOperator(BaseOperator):
    """ https://docs.sqlalchemy.org/en/14/core/sqlelement.html#sqlalchemy.sql.expression.ColumnOperators.__ne__ """

    alias = {'ne', '!=', 'notequal', 'not_equal', 'notequals', 'not_equals'}

    def expr(self) -> BinaryExpression:
        """ 构造表达式

        @return: BinaryExpression
        """
        return self.field != self._value  # type: ignore
