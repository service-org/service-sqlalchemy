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

from .schemas import FieldTypeEnum
from .expresss import OperatorExpression
from .expresss import FunctionExpression

BaseModel = declarative_base()
condition_type = {'and': and_, 'or': or_}

field_type = FieldTypeEnum.field.value
plain_type = FieldTypeEnum.plain.value


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
    order_maps = {'-': 'desc', '+': 'asc'}
    order_keys = tuple(order_maps.keys())
    if not model_name.startswith(order_keys):
        order_name = None
    else:
        order_type = model_name[0]
        model_name = model_name[1:]
        order_name = order_maps.get(order_type, None)
    model = getattr(module, model_name)
    field = getattr(model, field_name)
    if order_name is None: return field
    return getattr(field, order_name)()


def eval_operator(
        *,
        module: ModuleType,
        field: t.Text,
        type: t.Text,
        op: t.Text,
        value: t.Any,
        param: t.Optional[t.Dict[t.Text, t.Any]] = None
) -> BinaryExpression:
    """ 算操作表达式

    @param module: 模块对象
    @param field: 字段名称
    @param type: 字段类型
    @param op: 操作名称
    @param value: 字段的值
    @param param: 操作选项
    @return: BooleanClauseList
    """
    param, model, field_name = param or {}, BaseModel, None
    if isinstance(field, dict) and 'op' in field:
        field_name = eval_operator(
            module=module, field=field['field'],
            op=field['op'], value=field['value'],
            type=field['type'], param=field['param']
        )
    if isinstance(field, dict) and 'fn' in field:
        field_name = eval_function(
            module=module,
            field=field['field'], fn=field['fn'],
            type=field['type'], param=field['param']
        )
    if isinstance(value, list) and value:
        value_list = []
        for item in value:
            if item and 'op' in item:
                value_list.append(eval_operator(
                    module=module, field=item['field'],
                    op=item['op'], value=item['value'],
                    type=item['type'], param=item['param']
                ))
            if item and 'fn' in item:
                value_list.append(eval_function(
                    module=module,
                    field=item['field'], fn=item['fn'],
                    type=item['type'], param=item['param']
                ))
        value = value_list
    if isinstance(value, dict) and 'op' in value:
        value = eval_operator(
            module=module, field=value['field'],
            op=value['op'], value=value['value'],
            type=value['type'], param=value['param']
        )
    if isinstance(value, dict) and 'fn' in value:
        value = eval_function(
            module=module,
            field=value['field'], fn=value['fn'],
            type=value['type'], param=value['param']
        )
    if isinstance(field, str) and type == field_type:
        model_name, field_name = field.rsplit('.', 1)
        model = getattr(module, model_name)
    if isinstance(field, str) and type == plain_type:
        field_name = field
    operator_expression = OperatorExpression(
        model=model, field=field_name, type=type,
        op=op, param=param, value=value
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
        model = load_orm_class(
            module=module, field=join['model']
        )
        must = join.get('must', {}) or {}
        join_param = join.get('param', {}) or {}
        if must and 'op' in must:
            field = eval_operator(
                module=module, field=must['field'],
                op=must['op'], value=must['value'],
                type=must['type'], param=must['param']
            )
            result.append((model, field, join_param))
        if must and 'fn' in must:
            field = eval_function(
                module=module,
                field=must['field'], fn=must['fn'],
                type=must['type'], param=must['param']
            )
            result.append((model, field, join_param))
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
    a, o, b = filters
    if isinstance(a, list):
        a = eval_filter(module=module, filters=a)
    if isinstance(b, list):
        b = eval_filter(module=module, filters=b)
    if isinstance(a, dict) and 'op' in a:
        a = eval_operator(
            module=module, field=a['field'],
            op=a['op'], value=a['value'],
            type=a['type'], param=a['param']
        )
    if isinstance(a, dict) and 'fn' in a:
        a = eval_function(
            module=module,
            field=a['field'], fn=a['fn'],
            type=a['type'], param=a['param']
        )
    if isinstance(b, dict) and 'op' in b:
        b = eval_operator(
            module=module, field=b['field'],
            op=b['op'], value=b['value'],
            type=b['type'], param=b['param']
        )
    if isinstance(b, dict) and 'fn' in b:
        b = eval_function(
            module=module,
            field=b['field'], fn=b['fn'],
            type=b['type'], param=b['param']
        )
    return condition_type[o](a, b)


def eval_function(
        *, module: ModuleType,
        field: t.Text,
        type: t.Text,
        fn: t.Text,
        param: t.Optional[t.Dict[t.Text, t.Any]] = None
) -> GenericFunction:
    """ 算函数表达式

    @param module: 模块对象
    @param field: 字段名称
    @param type: 字段类型
    @param fn: 函数名称
    @param param: 函数选项
    @return: GenericFunction
    """
    param, model, field_name = param or {}, None, None
    if isinstance(field, list) and field:
        field_name = [eval_function(
            module=module,
            field=f['field'], fn=f['fn'],
            type=f['type'], param=f['param']
        ) for f in field]
    if isinstance(field, dict) and 'fn' in field:
        field_name = eval_function(
            module=module,
            field=field['field'], fn=field['fn'],
            type=field['type'], param=field['param']
        )
    if isinstance(field, str) and type == field_type:
        model_name, field_name = field.rsplit('.', 1)
        model = getattr(module, model_name)
    if isinstance(field, str) and type == plain_type:
        field_name = field
    function_expression = FunctionExpression(
        fn=fn, model=model, type=type,
        field=field_name, param=param
    )
    return function_expression.eval()


def eval_fields(
        *,
        module: ModuleType,
        fields: t.List[t.Union[t.Text, t.Dict[t.Text, t.Any]]]
) -> t.Union[BaseModel, InstrumentedAttribute, GenericFunction]:
    """ 构造字段列表

    @param module: 模块对象
    @param fields: 查询列表
    @return: t.List[InstrumentedAttribute]
    """
    result = []
    for field in fields:
        if isinstance(field, str):
            field = load_orm_class(
                module=module, field=field
            )
            result.append(field)
        if isinstance(field, dict) and 'op' in field:
            field = eval_operator(
                module=module, field=field['field'],
                op=field['op'], value=field['value'],
                type=field['type'], param=field['param']
            )
            result.append(field)
        if isinstance(field, dict) and 'fn' in field:
            field = eval_function(
                module=module,
                field=field['field'], fn=field['fn'],
                type=field['type'], param=field['param']
            )
            result.append(field)
    return result


# 查询字段
eval_query = eval_fields
# 排序字段
eval_order_by = eval_fields
# 分组字段
eval_group_by = eval_fields
