#! -*- coding: utf-8 -*-
#
# author: forcemain@163.com

from __future__ import annotations

from .base import OperatorMeta

from ._eq import EqualsOperator
from ._ne import NotEqualsOperator
from ._lt import LessThanOperator
from ._le import LessThanEqualsOperator
from ._gt import GreaterThanOperator
from ._ge import GreaterThanEqualsOperator
from ._between import BetweenOperator

from ._like import LikeOperator
from ._ilike import ILikeOperator
from ._not_like import NotLikeOperator
from ._not_ilike import NotIlikeOperator
from ._startswith import StartsWithOperator
from ._istartswith import IStartsWithOperator
from ._endswith import EndsWithOperator
from ._iendswith import IEndsWithOperator
from ._contains import ContainsOperator
from ._icontains import IContainsOperator

from ._in import InOperator
from ._not_in import NotInOperator
from ._is import IsOperator
from ._is_not import IsNotOperator
from ._is_null import IsNullOperator
from ._is_not_null import IsNotNullOperator

from ._asc import AscOperator
from ._desc import DescOperator
from ._distinct import DistinctOperator

from ._regexp_match import RegexpMatchOperator
from ._regexp_replace import RegexpReplaceOperator

from ._any import AnyOperator
from ._has import HasOperator

from ._label import LabelOperator

from ._plain import PlainOperator
from ._field import FieldOperator
