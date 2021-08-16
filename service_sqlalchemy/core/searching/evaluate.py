#! -*- coding: utf-8 -*-
#
# author: forcemain@163.com

from __future__ import annotations

import typing as t
from types import ModuleType
from sqlalchemy.sql import and_, or_
from sqlalchemy.sql.functions import GenericFunction
from sqlalchemy.sql.elements import BinaryExpression
from sqlalchemy.sql.elements import BooleanClauseList
from sqlalchemy.ext.declarative import declarative_base
from service_sqlalchemy.exception import ValidationError
from sqlalchemy.orm.attributes import InstrumentedAttribute

from .expresss import OperatorExpression
from .expresss import FunctionExpression

BaseModel = declarative_base()
condition_type = {'and': and_, 'or': or_}


def load_orm_class(
        *,
        module: ModuleType,
        field: t.Text
) -> t.Union[BaseModel, InstrumentedAttribute]:
    """ 加载ORM特定类

    @param module: 模块对象
    @param field: 字段名称
    @return: InstrumentedAttribute
    """
    if field.count('.') == 0:
        return getattr(module, field)
    if field.count('.') != 1:
        errs = f'{field} must be [Model].[Field]'
        raise ValidationError(errormsg=errs)
    model_name, field_name = field.rsplit('.', 1)
    order_name = {'-': 'desc', '+': 'asc'}.get(model_name[0], None)
    field = getattr(getattr(module, model_name), field_name)
    return getattr(field, order_name) if order_name else field


def eval_operator(
        *,
        module: ModuleType,
        field: t.Text,
        op: t.Text,
        value: t.Any,
        param: t.Optional[t.Dict[t.Text, t.Any]] = None
) -> BinaryExpression:
    """ 算操作表达式

    @param module: 模块对象
    @param field: 字段名称
    @param op: 操作名称
    @param value: 字段的值
    @param param: 操作选项
    @return: BooleanClauseList
    """
    param = param or {}
    model = BaseModel
    field_name = None
    if isinstance(field, dict) and 'op' in field:
        field_name = eval_operator(
            module=module,
            field=field['field'],
            op=field['op'],
            value=field['value'],
            param=field.get('param', {}) or {}
        )
    if isinstance(field, dict) and 'fn' in field:
        field_name = eval_function(
            module=module,
            field=field['field'],
            fn=field['fn'],
            param=field.get('parm', {}) or {}
        )
    if isinstance(value, dict) and 'op' in value:
        value = eval_operator(
            module=module,
            field=value['field'],
            op=value['op'],
            value=value['value'],
            param=value.get('param', {}) or {}
        )
    if isinstance(value, dict) and 'fn' in value:
        value = eval_function(
            module=module,
            field=value['field'],
            fn=value['fn'],
            param=value.get('parm', {}) or {}
        )
    if isinstance(field, str):
        model_name, field_name = field.rsplit('.', 1)
        model = getattr(module, model_name)
    operator_expression = OperatorExpression(
        model=model, field=field_name, op=op,
        param=param, value=value
    )
    return operator_expression.expr()


def eval_join(
        *,
        module: ModuleType,
        joins: t.List[t.Dict[t.Text, t.Any]]
) -> t.List[t.Tuple[InstrumentedAttribute, BooleanClauseList, t.Dict[t.Text, t.Any]]]:
    """ 构造Join条件

    @param module: 模块对象
    @param joins: 联表列表
    @return: t.List[t.Tuple[InstrumentedAttribute, BooleanClauseList, t.Dict[t.Text, t.Any]]]
    """
    result = []
    for join in joins:
        model = load_orm_class(module=module, field=join['model'])
        field = eval_operator(
            module=module,
            field=join['must']['field'],
            op=join['must']['op'],
            value=join['must']['value'],
            param=join['must'].get('param', {}) or {}
        )
        result.append((model, field, join['param']))
    return result


def make_filter(
        a: t.Optional[t.Union[t.Dict[t.Text, t.Any], t.List[t.Dict]]] = None,
        o: t.Optional[t.Text] = None,
        b: t.Optional[t.Union[t.Dict[t.Text, t.Any], t.List[t.Dict]]] = None,
) -> t.List:
    """ 整理过滤条件

    @param a: 条件a
    @param o: and/or
    @param b: 条件b
    @return: None
    """
    if isinstance(a, list) and a:
        a = make_filter(*a)
    if isinstance(b, list) and b:
        b = make_filter(*b)
    a, o, b = a or [], o or 'and', b or []
    check_a = isinstance(a, (dict, list)) or not a
    check_b = isinstance(b, (dict, list)) or not b
    if check_a and check_b: return [a, o, b]


def eval_filter(
        *,
        module: ModuleType,
        filters: t.List
) -> BooleanClauseList:
    """ 构造过滤条件

    @param module: 模块对象
    @param filters: 过滤列表
    @return: BooleanClauseList
    """
    if not filters:
        return and_()
    (a, o, b), c = filters, []
    if isinstance(a, list):
        a = eval_filter(module=module, filters=a)
    if isinstance(b, list):
        b = eval_filter(module=module, filters=b)
    if isinstance(a, dict) and 'op' in a:
        a = eval_operator(
            module=module,
            field=a['field'], op=a['op'],
            value=a['value'],
            param=a.get('param', {}) or {}
        )
        c.append(a)
    if isinstance(a, dict) and 'fn' in a:
        a = eval_function(
            module=module,
            field=a['field'], fn=a['fn'],
            param=a.get('param', {}) or {}
        )
        c.append(a)
    if isinstance(b, dict) and 'op' in b:
        b = eval_operator(
            module=module,
            field=b['field'], op=b['op'],
            value=b['value'],
            param=b.get('param', {}) or {})
        c.append(b)
    if isinstance(b, dict) and 'fn' in b:
        b = eval_function(
            module=module,
            field=b['field'], fn=b['fn'],
            param=b.get('param', {}) or {}
        )
        c.append(b)
    return condition_type[o](*c)


def eval_function(
        *, module: ModuleType,
        field: t.Text,
        fn: t.Text,
        param: t.Optional[t.Dict[t.Text, t.Any]] = None
) -> GenericFunction:
    """ 算函数表达式

    @param module: 模块对象
    @param field: 字段名称
    @param fn: 函数名称
    @param param: 函数选项
    @return: GenericFunction
    """
    param = param or {}
    model_name, field_name = field.rsplit('.', 1)
    model = getattr(module, model_name)
    if isinstance(field, dict) and 'fn' in field:
        field_name = eval_function(
            module=module,
            field=field['field'],
            fn=field['fn'],
            param=field.get('parm', {}) or {}
        )
    function_expression = FunctionExpression(
        fn=fn, model=model, field=field_name, param=param
    )
    return function_expression.eval()


def eval_fields(
        *,
        module: ModuleType,
        queries: t.List[t.Union[t.Text, t.Dict[t.Text, t.Any]]]
) -> t.Union[BaseModel, InstrumentedAttribute, GenericFunction]:
    """ 构造字段列表

    @param module: 模块对象
    @param queries: 查询列表
    @return: t.List[InstrumentedAttribute]
    """
    result = []
    for query in queries:
        if isinstance(query, str):
            field = load_orm_class(
                module=module, field=query
            )
            result.append(field)
        if isinstance(query, dict):
            fn = query['fn']
            field = query['field']
            param = query.get('param', {}) or {}
            field = eval_function(
                module=module, field=field,
                fn=fn, param=param
            )
            result.append(field)
    return result


def eval_having(
        *,
        module: ModuleType,
        havings: t.List[t.Union[t.Text, t.Dict[t.Text, t.Any]]]
) -> t.List[BooleanClauseList]:
    """ 构造分组字段

    @param module: 模块对象
    @param havings: 分组列表
    @return: t.List[BooleanClauseList]
    """
    result = []
    for having in havings:
        if isinstance(having, dict) and 'op' in having:
            field = eval_operator(
                module=module,
                field=having['field'], op=having['op'],
                value=having['value'],
                param=having.get('param', {}) or {}
            )
            result.append(field)
        if isinstance(having, dict) and 'fn' in having:
            field = eval_function(
                module=module,
                field=having['field'],
                fn=having['fn'],
                param=having.get('param', {}) or {}
            )
            result.append(field)
    return result


# 查询字段
eval_query = eval_fields
# 排序字段
eval_order_by = eval_fields
# 分组字段
eval_group_by = eval_fields
