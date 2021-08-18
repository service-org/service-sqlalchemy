#! -*- coding: utf-8 -*-
#
# author: forcemain@163.com

from __future__ import annotations

from .base import FunctionMeta

from ._asc import AscFunction
from ._desc import DescFunction
from ._distinct import DistinctFunction

from ._plain import PlainFunction
from ._field import FieldFunction

# 所有sqlalchemy.func支持的函数都默认处理
from ._default import DefaultFunction
