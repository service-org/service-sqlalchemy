#! -*- coding: utf-8 -*-
#
# author: forcemain@163.com

from __future__ import annotations

from service_core.exception import RemoteError


class ValidationError(RemoteError):
    """ SQLAlchemy异常 """
    pass
