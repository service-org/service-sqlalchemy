#! -*- coding: utf-8 -*-
#
# author: forcemain@163.com

from __future__ import annotations

import typing as t

from enum import Enum
from pydantic import BaseModel
from pydantic.fields import Field


class FieldTypeEnum(str, Enum):
    """ 字段类型枚举 """
    field = 'field'
    plain = 'plain'


class FunctionSchema(BaseModel):
    """ 标准函数模式 """
    field: t.Union[
        t.List[t.Union[OperatorSchema, FunctionSchema]],
        t.Text, OperatorSchema, FunctionSchema
    ] = Field(description='字段名称')
    type: t.Optional[
        FieldTypeEnum
    ] = Field(description='字段类型', default=FieldTypeEnum.field)
    fn: t.Text = Field(description='函数名称')
    param: t.Optional[
        t.Dict[t.Text, t.Any]
    ] = Field(description='函数选项', default={})


class OperatorSchema(BaseModel):
    """ 标准操作模式 """
    field: t.Union[
        t.Text, OperatorSchema, FunctionSchema
    ] = Field(description='字段名称')
    type: t.Optional[
        FieldTypeEnum
    ] = Field(description='字段类型', default=FieldTypeEnum.field)
    op: t.Text = Field(description='操作名称')
    value: t.Union[
        t.List[t.Union[OperatorSchema, FunctionSchema]],
        t.Text, int, float, bool, None,
        OperatorSchema, FunctionSchema,
    ] = Field(description='字段的值')
    param: t.Optional[
        t.Dict[t.Text, t.Any]
    ] = Field(description='操作选项', default={})


# 注意: Operator和Function存在相互引用
FunctionSchema.update_forward_refs()
OperatorSchema.update_forward_refs()


class FilterSchema(BaseModel):
    """ 过滤条件模式 """
    a: t.Union[
        t.List[t.Union[OperatorSchema, FunctionSchema]],
        OperatorSchema, FunctionSchema, 'FilterSchema'
    ] = Field(description='条件a', default=None)
    o: t.Text = Field(description='运算o', default='and', regex=r'and|or')
    b: t.Union[
        t.List[t.Union[OperatorSchema, FunctionSchema]],
        OperatorSchema, FunctionSchema, 'FilterSchema'
    ] = Field(description='条件b', default=None)


FilterSchema.update_forward_refs()


class JoinSchema(BaseModel):
    """ 联合查询模式 """
    model: t.Text = Field(description='模型名称')
    must: t.Optional[
        t.Union[OperatorSchema, FunctionSchema]
    ] = Field(description='联合条件', default=None)
    param: t.Dict[
        t.Text, t.Any
    ] = Field(description='联合参数', default={})


class SearchSchema(BaseModel):
    """ 高级查询模式 """
    query: t.List[
        t.Union[t.Text, OperatorSchema, FunctionSchema]
    ] = Field(description='查询字段')
    join: t.Optional[
        t.List[JoinSchema]
    ] = Field(description='JOIN查询', default=[])
    group_by: t.Optional[
        t.List[t.Union[t.Text, OperatorSchema, FunctionSchema]]
    ] = Field(description='分组字段', default=[])
    order_by: t.Optional[
        t.List[t.Union[t.Text, OperatorSchema, FunctionSchema]]
    ] = Field(description='排序字段', default=[])
    page: t.Optional[
        int
    ] = Field(description='分页页码', default=None)
    page_size: t.Optional[
        int
    ] = Field(description='分页大小', default=None)
