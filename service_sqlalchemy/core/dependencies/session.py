#! -*- coding: utf-8 -*-
#
# author: forcemain@163.com

from __future__ import annotations

import typing as t

from logging import getLogger
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session
from service_sqlalchemy.core.client import SQLAlchemyClient
from service_core.core.service.dependency import Dependency
from service_sqlalchemy.constants import SQLALCHEMY_CONFIG_KEY

logger = getLogger(__name__)


class SQLAlchemy(Dependency):
    """ SQLAlchemy依赖类 """

    def __init__(
            self,
            alias: t.Text,
            engine_options: t.Optional[t.Dict[t.Text, t.Any]] = None,
            session_wrapper: t.Optional[t.Callable[..., t.Any]] = None,
            session_options: t.Optional[t.Dict[t.Text, t.Any]] = None,
            migrate_options: t.Optional[t.Dict[t.Text, t.Any]] = None,
            **kwargs: t.Any
    ) -> None:
        """ 初始化实例

        @param alias: 配置别名
        @param engine_options:  引擎配置
        @param session_wrapper: 会话装饰
        @param session_options: 会话配置
        @param migrate_options: 迁移配置
        @param kwargs: 其它参数
        """
        self.alias = alias
        self.engine = None
        self.session_map = {}
        self.session_cls = None
        self.session_wrapper = session_wrapper
        self.engine_options = engine_options or {}
        # 默认设置连接池的大小为1024允许最大超出连接为1024
        self.engine_options.setdefault('pool_size', 1024)
        self.engine_options.setdefault('max_overflow', 1024)
        # 根据配置中的echo设置是否开启orm详细日志打印的功能
        self.engine_options.setdefault('echo', False)
        # 允许在数据库宕机恢复后新的请求自动尝试重新建立连接
        self.engine_options.setdefault('pool_pre_ping', True)
        # 当连接池中没有连接可用时等待时间,如连接未及时关闭
        self.engine_options.setdefault('pool_timeout', 0)
        # 连接池中连接存活多久就尝试回收,解决MYSQL8小时问题
        self.engine_options.setdefault('pool_recycle', 2 * 60 * 60)
        self.session_options = session_options or {}
        self.migrate_options = migrate_options or {}
        kwargs.setdefault('once_inject', False)
        super(SQLAlchemy, self).__init__(**kwargs)

    def setup(self) -> None:
        """ 生命周期 - 载入阶段

        @return: None
        """
        sqlalchemy_url = self.container.config.get(f'{SQLALCHEMY_CONFIG_KEY}.{self.alias}.url', default='')
        engine_options = self.container.config.get(f'{SQLALCHEMY_CONFIG_KEY}.{self.alias}.engine_options', default={})
        # 防止YAML中声明值为None
        self.engine_options = (engine_options or {}) | self.engine_options
        session_options = self.container.config.get(f'{SQLALCHEMY_CONFIG_KEY}.{self.alias}.session_options', default={})
        # 防止YAML中声明值为None
        self.session_options = (session_options or {}) | self.session_options
        self.engine = create_engine(sqlalchemy_url, **self.engine_options)
        self.session_cls = scoped_session(sessionmaker(bind=self.engine, **self.session_options))
        self.session_cls = self.session_wrapper(self.session_cls) if self.session_wrapper else self.session_cls

    def stop(self) -> None:
        """ 生命周期 - 关闭阶段

        @return: None
        """
        self.engine.dispose()

    def get_client(self) -> SQLAlchemyClient:
        """ 获取一个独立的会话

        @return: SQLAlchemyClient
        """
        return self.session_cls()
