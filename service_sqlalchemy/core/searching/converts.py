#! -*- coding: utf-8 -*-
#
# author: forcemain@163.com

from __future__ import annotations

import typing as t


def convert_filter(filters: t.List) -> t.Dict[t.Text, t.Any]:
    """ 转换make_filter的数据

    主要用于FilterSchema验证

    @param filters: 嵌套过滤器
    @return: t.Dict[t.Text, t.Any]
    """
    result = {}
    if not filters: return result
    a = result.setdefault('a', filters[0])
    o = result.setdefault('o', filters[1])
    b = result.setdefault('b', filters[2])
    a = convert_filter(a) if isinstance(a, list) else a
    b = convert_filter(b) if isinstance(b, list) else b
    return {'a': a, 'o': o, 'b': b}
