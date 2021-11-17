#! -*- coding: utf-8 -*-
#
# author: forcemain@163.com

from __future__ import annotations

import typing as t

from logging import getLogger
from contextlib import contextmanager

from .dependencies import SQLAlchemy
from .client import SQLAlchemyClient


logger = getLogger(__name__)


@contextmanager
def safe_transaction(
        orm: SQLAlchemy,
        *,
        nested: t.Optional[bool] = False,
        commit: t.Optional[bool] = True,
) -> SQLAlchemyClient:
    """ 开启安全事务模式

    @param orm: sqlalchemy
    @param commit: 自动提交
    @param nested: 是否嵌套
    @return: SQLAlchemyClient
    """
    session, finish = None, False
    try:
        session = orm.get_client()
        nested and session.begin_nested()
        yield session
        commit and session.commit()
        finish = True
    finally:
        session and not finish and session.rollback()
        session and not nested and session.close()
