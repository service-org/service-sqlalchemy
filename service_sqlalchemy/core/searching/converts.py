#! -*- coding: utf-8 -*-
#
# author: forcemain@163.com

from __future__ import annotations

import typing as t


def convert_dict_filter_to_list(filters: t.Dict[t.Text, t.Any]) -> t.List:
    """ 转换make_filter的数据

    FilterSchema验证后的数据

    @param filters: 嵌套过滤器
    @return: t.List
    """
    result = [[], 'and', []]
    if not filters: return result
    if 'a' in filters and 'o' in filters and 'b' in filters:
        a = filters['a']
        o = filters['o']
        b = filters['b']
        a = convert_dict_filter_to_list(a) if isinstance(a, dict) and a else a
        b = convert_dict_filter_to_list(b) if isinstance(b, dict) and b else b
        return [a, o, b]
    return filters  # type: ignore


def convert_list_filter_to_dict(filters: t.List) -> t.Dict[t.Text, t.Any]:
    """ 转换make_filter的数据

    FilterSchema验证初始数据

    @param filters: 嵌套过滤器
    @return: t.Dict[t.Text, t.Any]
    """
    result = {}
    if not filters: return result
    a = result.setdefault('a', filters[0])
    o = result.setdefault('o', filters[1])
    b = result.setdefault('b', filters[2])
    a = convert_list_filter_to_dict(a) if isinstance(a, list) and a else a
    b = convert_list_filter_to_dict(b) if isinstance(b, list) and b else b
    return {'a': a, 'o': o, 'b': b}
