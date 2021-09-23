#! -*- coding: utf-8 -*-
#
# author: forcemain@163.com

from __future__ import annotations

import typing as t

from types import ModuleType
from sqlalchemy.orm import Query
from sqlalchemy.sql.functions import GenericFunction
from sqlalchemy.sql.elements import BooleanClauseList
from service_core.core.decorator import AsLazyProperty
from sqlalchemy.ext.declarative import declarative_base
from service_sqlalchemy.core.client import SQLAlchemyClient
from sqlalchemy.orm.attributes import InstrumentedAttribute

from .evaluate import eval_join
from .evaluate import eval_query
from .schemas import SearchSchema
from .schemas import FilterSchema
from .evaluate import make_filter
from .evaluate import eval_filter
from .evaluate import eval_order_by
from .evaluate import eval_group_by
from .converts import convert_list_filter_to_dict
from .converts import convert_dict_filter_to_list

BaseModel = declarative_base()


class Search(object):
    """ 高级查询类 """

    def __init__(
            self,
            session: SQLAlchemyClient,
            *,
            module: ModuleType,
            query: t.List[t.Union[t.Text, t.Dict[t.Text, t.Any]]],
            join: t.Optional[t.List[t.Dict[t.Text, t.Any]]] = None,
            filter_by: t.Optional[t.Union[t.Dict, t.List]] = None,
            group_by: t.Optional[t.List[t.Union[t.Text, t.Dict][t.Text, t.Any]]] = None,
            having: t.Optional[t.Union[t.Dict, t.List]] = None,
            order_by: t.Optional[t.List[t.Union[t.Text, t.Dict[t.Text, t.Any]]]] = None,
            page: t.Optional[int] = None,
            page_size: t.Optional[int] = None
    ) -> None:
        """ 初始化实例

        @param session: 安全会话
        @param module: 模块对象
        @param query: 查询字段
        @param join: 联表字段
        @param filter_by: 过滤条件
        @param order_by: 排序字段
        @param page: 分页页码
        @param page_size: 分页大小
        """
        self._module, self._session = module, session
        self._page, self._page_size = page, page_size
        join = join or []
        if not isinstance(join, list):
            join = [join]
        having = having or []
        if not isinstance(having, list):
            having = [having]
        self._having = having
        order_by = order_by or []
        filter_by = filter_by or []
        if not isinstance(filter_by, list):
            filter_by = [filter_by]
        self._filter_by = filter_by
        group_by = group_by or []
        if not isinstance(group_by, list):
            group_by = [group_by]
        if not isinstance(order_by, list):
            order_by = [order_by]
        schema = SearchSchema(
            query=query, join=join, order_by=order_by,
            group_by=group_by, page=page,
            page_size=page_size
        )
        self._init_data = schema.dict()

    @AsLazyProperty
    def query(self) -> t.List[t.Union[BaseModel, InstrumentedAttribute, GenericFunction]]:
        """ 查询字段

        @return: t.List[t.Union[BaseModel, InstrumentedAttribute, GenericFunction]]
        """
        query = self._init_data['query']
        return eval_query(module=self._module, fields=query)

    @AsLazyProperty
    def join(self) -> t.List[t.Tuple[InstrumentedAttribute, BooleanClauseList, t.Dict[t.Text, t.Any]]]:
        """ 联表字段

        @return: t.List[t.Tuple[InstrumentedAttribute, BooleanClauseList, t.Dict[t.Text, t.Any]]]
        """
        joins = self._init_data['join']
        return eval_join(module=self._module, joins=joins)

    @AsLazyProperty
    def filter_by(self) -> BooleanClauseList:
        """ 查询条件

        @return: BooleanClauseList
        """
        # 整理成嵌套列表
        # 1.用于简化配置
        # 2.用于生成查询
        list_filters = make_filter(*self._filter_by)
        dict_filters = convert_list_filter_to_dict(list_filters)
        # 验证嵌套的数据
        dict_filters = FilterSchema(**dict_filters).dict()
        filters = convert_dict_filter_to_list(dict_filters)
        return eval_filter(module=self._module, filters=filters)

    @AsLazyProperty
    def group_by(self) -> t.List[t.Union[BaseModel, InstrumentedAttribute, GenericFunction]]:
        """ 查询字段

        @return: t.List[t.Union[BaseModel, InstrumentedAttribute, GenericFunction]]
        """
        group_by = self._init_data['group_by']
        return eval_group_by(module=self._module, fields=group_by)

    @AsLazyProperty
    def having(self) -> t.List[t.Union[BaseModel, InstrumentedAttribute, GenericFunction]]:
        """ 分组条件

        @return: t.List[t.Union[BaseModel, InstrumentedAttribute, GenericFunction]]
        """
        # 整理成嵌套列表
        # 1.用于简化配置
        # 2.用于生成查询
        list_filters = make_filter(*self._having)
        dict_filters = convert_list_filter_to_dict(list_filters)
        # 验证嵌套的数据
        dict_filters = FilterSchema(**dict_filters).dict()
        havings = convert_dict_filter_to_list(dict_filters)
        return eval_filter(module=self._module, filters=havings)

    @AsLazyProperty
    def order_by(self) -> t.List[t.Union[BaseModel, InstrumentedAttribute, GenericFunction]]:
        """ 查询字段

        @return: t.List[t.Union[BaseModel, InstrumentedAttribute, GenericFunction]]
        """
        order_by = self._init_data['order_by']
        return eval_order_by(module=self._module, fields=order_by)

    @AsLazyProperty
    def queryset(self) -> Query:
        """ 查询对象

        @return: Query
        """
        queryset = self._session.query(*self.query)
        for model, must, param in self.join:
            queryset = queryset.join(model, must, **param)
        queryset = queryset.filter(self.filter_by)
        if self.group_by:
            queryset = queryset.group_by(*self.group_by)
        if self._having:
            queryset = queryset.having(self.having)
        if self.order_by:
            queryset = queryset.order_by(*self.order_by)
        return queryset

    @AsLazyProperty
    def pagination(self) -> Query:
        """ 分页对象

        @return: Query
        """
        if self._page is None and self._page_size is None:
            return self.queryset
        else:
            page, page_size = self._page or 1, self._page_size or 15
            start, stop = (page - 1) * page_size, page * page_size
        return self.queryset.slice(start, stop)
