#! -*- coding: utf-8 -*-
#
# author: forcemain@163.com

from __future__ import annotations

import typing as t

from sqlalchemy.sql.elements import BinaryExpression
from sqlalchemy.sql.functions import GenericFunction
from sqlalchemy.ext.declarative import declarative_base
from service_sqlalchemy.exception import ValidationError

from .schemas import FieldTypeEnum
from .operators import OperatorMeta
from .functions import FunctionMeta
from .functions import DefaultFunction

BaseModel = declarative_base()


class FunctionExpression(object):
    """ 函数表达式 """

    def __init__(
            self, *,
            fn: t.Text,
            model: BaseModel,
            field: t.Union[t.Text, GenericFunction],
            type: t.Optional[t.Text] = None,
            param: t.Optional[t.Dict[t.Text, t.Any]] = None
    ) -> None:
        """ 初始化实例

        @param fn: 函数名称
        @param model: 模型对象
        @param field: 字段名称
        @param type: 字段类型
        @param param: 函数选项
        """
        Function = FunctionMeta.mapping.get(
            fn, DefaultFunction
        )
        param = param or {}
        type = type or FieldTypeEnum.field.value
        kwargs = {'func': fn, 'model': model, 'field': field,
                  'type': type, 'param': param}
        self._function = Function(**kwargs)

    def eval(self) -> GenericFunction:
        """ 生成的函数

        @return: GenericFunction
        """
        return self._function.eval()


class OperatorExpression(object):
    """ 操作表达式 """

    def __init__(
            self, *,
            model: BaseModel,
            field: t.Union[t.Text, GenericFunction],
            op: t.Text,
            value: t.Any,
            type: t.Optional[t.Text] = None,
            param: t.Optional[t.Dict[t.Text, t.Any]] = None
    ) -> None:
        """ 初始化实例

        @param op: 操作名称
        @param model: 模型对象
        @param field: 字段名称
        @param value: 字段的值
        @param type: 字段类型
        @param param: 操作选项
        """
        try:
            Operator = OperatorMeta.mapping[op]
        except KeyError:
            errs = f'invalid operator {op}'
            raise ValidationError(errormsg=errs)
        param = param or {}
        type = type or FieldTypeEnum.field.value
        kwargs = {
            'model': model, 'field': field,
            'type': type,
            'value': value, 'param': param}
        self._operator = Operator(**kwargs)

    def expr(self) -> BinaryExpression:
        """ 构造表达式

        @return: BinaryExpression
        """
        return self._operator.expr()
