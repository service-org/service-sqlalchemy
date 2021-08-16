#! -*- coding: utf-8 -*-
#
# author: forcemain@163.com

from __future__ import annotations

import typing as t

from pydantic import BaseModel
from pydantic.fields import Field


class FunctionSchema(BaseModel):
    """ 标准函数模式 """
    field: t.Union[t.Text, FunctionSchema] = Field(description='字段名称')
    fn: t.Text = Field(description='函数名称')
    param: t.Optional[t.Dict[t.Text, t.Any]] = Field(description='函数选项', default={})


FunctionSchema.update_forward_refs()


class OperatorSchema(BaseModel):
    """ 标准操作模式 """
    field: t.Union[t.Text, FunctionSchema] = Field(description='字段名称')
    op: t.Text = Field(description='操作名称')
    value: t.Union[t.Text, int, float, bool, t.List, OperatorSchema, FunctionSchema] = Field(description='字段的值')
    param: t.Optional[t.Dict[t.Text, t.Any]] = Field(description='操作选项', default={})


OperatorSchema.update_forward_refs()


class FilterSchema(BaseModel):
    """ 过滤条件模式 """
    a: t.Union[OperatorSchema, t.List[OperatorSchema], FilterSchema] = Field(description='条件a', default=None)
    o: t.Text = Field(description='运算o', default='and', regex=r'and|or')
    b: t.Union[OperatorSchema, t.List[OperatorSchema], FilterSchema] = Field(description='条件b', default=None)


FilterSchema.update_forward_refs()


class JoinSchema(BaseModel):
    """ 联合查询模式 """
    model: t.Text = Field(description='模型名称')
    must: t.Optional[OperatorSchema] = Field(description='联合条件', default=None)
    param: t.Dict[t.Text, t.Any] = Field(description='联合参数', default={})


class SearchSchema(BaseModel):
    """ 高级查询模式 """
    query: t.List[t.Union[t.Text, FunctionSchema]] = Field(description='查询字段')
    join: t.Optional[t.List[JoinSchema]] = Field(description='JOIN查询', default=[])
    filter_by: FilterSchema = Field(description='过滤条件', default=[])
    group_by: t.Optional[t.List[t.Union[t.Text, FunctionSchema]]] = Field(description='分组字段', default=[])
    having: t.List[OperatorSchema] = Field(description='分组过滤', default=[])
    order_by: t.List[t.Union[t.Text, FunctionSchema]] = Field(description='排序字段', default=[])
    page: t.Optional[int] = Field(description='分页页码', default=None)
    page_size: t.Optional[int] = Field(description='分页大小', default=None)
