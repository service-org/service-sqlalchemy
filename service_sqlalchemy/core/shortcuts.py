#! -*- coding: utf-8 -*-
#
# author: forcemain@163.com

from __future__ import annotations

import typing as t

from types import ModuleType
from logging import getLogger
from sqlalchemy.orm.query import Query
from sqlalchemy.exc import MultipleResultsFound
from sqlalchemy.ext.declarative import declarative_base

from .searching import Search
from .transaction import safe_transaction
from .dependencies.session import SQLAlchemy

logger = getLogger(__name__)
BaseModel = declarative_base()


def select_or_create(
        orm: SQLAlchemy,
        *,
        model: BaseModel,
        defaults: t.Optional[t.Dict[t.Text, t.Any]] = None,
        **query: t.Any
) -> Query:
    """ 查询并创建实例

    @param orm: sqlalchemy
    @param model: 目标模型
    @param defaults: 初始字典
    @param query: 查询字典
    @return: Query
    """
    defaults = defaults or {}
    with safe_transaction(orm, nested=True, commit=False) as session:
        queryset = session.query(model).filter_by(**query)
        if queryset.count() > 1: raise MultipleResultsFound(f'{model} - {query}')
        instance = queryset.first()
        if not instance:
            defaults.update(query)
            instance = model(**defaults)
            session.add(instance)
            session.commit()
        return instance


def update_or_create(
        orm: SQLAlchemy,
        *,
        model: BaseModel,
        defaults: t.Optional[t.Dict[t.Text, t.Any]] = None,
        **query: t.Any
) -> Query:
    """ 更新并创建实例

    @param orm: sqlalchemy
    @param model: 目标模型
    @param defaults: 初始字典
    @param query: 查询字典
    @return: Query
    """
    defaults = defaults or {}
    with safe_transaction(orm, nested=True, commit=True) as session:
        queryset = session.query(model).filter_by(**query)
        if queryset.count() > 1: raise MultipleResultsFound(f'{model} - {query}')
        instance = queryset.first()
        if instance:
            items = defaults.items()
            for k, v in items: setattr(instance, k, v)
        else:
            defaults.update(query)
            instance = model(**defaults)
            session.add(instance)
        return instance


def orm_json_search(
        orm: SQLAlchemy,
        *,
        module: ModuleType,
        query: t.List[t.Union[t.Text, t.Dict]],
        join: t.Optional[t.List[t.Dict[t.Text, t.Any]]] = None,
        filter_by: t.Optional[t.Union[t.Dict, t.List]] = None,
        group_by: t.Optional[t.List[t.Union[t.Text, t.Dict]]] = None,
        having: t.Optional[t.Union[t.Dict, t.List]] = None,
        order_by: t.Optional[t.List[t.Union[t.Text, t.Dict]]] = None,
        page: t.Optional[int] = None,
        page_size: t.Optional[int] = None
) -> Query:
    """ 基于json构建查询

    @param orm: sqlalchemy
    @param module: 模块对象
    @param query: 查询字段
    @param join: 联表字段
    @param filter_by: 过滤条件
    @param group_by: 分组字段
    @param having: 分组条件
    @param order_by: 排序字段
    @param page: 分页页码
    @param page_size: 每页大小
    @return: Query
    """
    with safe_transaction(orm, commit=False) as session:
        return Search(
            session,
            module=module,
            query=query,
            join=join,
            filter_by=filter_by,
            group_by=group_by,
            having=having,
            order_by=order_by,
            page=page,
            page_size=page_size
        ).pagination
