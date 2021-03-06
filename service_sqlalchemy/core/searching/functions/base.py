#! -*- coding: utf-8 -*-
#
# author: forcemain@163.com

from __future__ import annotations

import typing as t

from sqlalchemy import func as funcs
from sqlalchemy.sql.functions import GenericFunction
from service_core.core.decorator import AsLazyProperty
from sqlalchemy.ext.declarative import declarative_base
from service_sqlalchemy.core.searching.schemas import FieldTypeEnum

BaseModel = declarative_base()


class FunctionMeta(type):
    """ 函数的收集器 """

    mapping = {}

    def __new__(mcs, name: t.Text, bases: t.Tuple[type, ...], namespace: t.Dict[t.Text, t.Any]) -> t.Type:
        """ 初始化子类

        @param mcs: 元类实例
        @param name: 收集的类名
        @param bases: 继承的类
        @param namespace: 属性
        """
        klass = type.__new__(mcs, name, bases, namespace)
        # 过滤掉过滤器基类
        if name == 'BaseFunction':
            return klass
        else:
            data = {alias: klass for alias in klass.alias}
            mcs.mapping.update(data)
            return klass


class BaseFunction(object, metaclass=FunctionMeta):
    """ 函数的基类 """

    alias: t.Set[t.Text] = None

    def __init__(
            self, *,
            func: t.Text,
            model: BaseModel,
            field: t.Union[t.Text, GenericFunction],
            type: t.Optional[t.Text] = None,
            param: t.Optional[t.Dict[t.Text, t.Any]] = None
    ) -> None:
        """ 初始化实例

        @param func: 函数名称
        @param model: 模型对象
        @param field: 字段名称
        @param field: 字段类型
        @param param: 操作选项
        """
        self._func = func
        self._model = model
        self._field = field
        self._param = param or {}
        self._type = type or FieldTypeEnum.field.value

    @AsLazyProperty
    def func(self) -> t.Type[GenericFunction]:
        """ 实际的函数

        @return: GenericFunction
        """
        return getattr(funcs, self._func)

    def eval(self) -> GenericFunction:
        """ 生成的函数

        @return: GenericFunction
        """
        raise NotImplementedError

    @AsLazyProperty
    def field(self) -> t.Any:
        """ 模型的字段

        @return: Column
        """
        if isinstance(self._field, str):
            if self._type == FieldTypeEnum.plain.value:
                return self._field
            if self._type == FieldTypeEnum.field.value:
                return getattr(self._model, self._field)
        this_is_an_other_type_field = self._field
        return this_is_an_other_type_field
