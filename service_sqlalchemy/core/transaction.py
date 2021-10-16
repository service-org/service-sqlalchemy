#! -*- coding: utf-8 -*-
#
# author: forcemain@163.com

from __future__ import annotations

import typing as t

from logging import getLogger
from contextlib import contextmanager

from .client import SQLAlchemyClient
from .dependencies.session import SQLAlchemy

logger = getLogger(__name__)


@contextmanager
def safe_transaction(
        orm: SQLAlchemy,
        *,
        nested: t.Optional[bool] = None,
        commit: t.Optional[bool] = True,
) -> SQLAlchemyClient:
    """ 开启安全事务模式

    @param orm: sqlalchemy
    @param commit: 自动提交
    @param nested: 是否嵌套
    @return: SQLAlchemyClient
    """
    session = None
    try:
        session = orm.get_client()
        nested and session.begin_nested()
        yield session
        commit and session.commit()
    except:
        session and session.rollback()
        logger.error(f'unexpected error while execute sql', exc_info=True)
    finally:
        session and session.close()
