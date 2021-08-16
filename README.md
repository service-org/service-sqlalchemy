# 运行环境

|system |python | 
|:------|:------|      
|cross platform |3.9.16|

# 注意事项

You may use any database [driver compatible with SQLAlchemy](http://docs.sqlalchemy.org/en/rel_0_9/dialects/index.html)
provided it is safe to use with [eventlet](http://eventlet.net). This will include all pure This will inc-python
drivers. Known safe drivers are:

* [pysqlite](http://docs.sqlalchemy.org/en/rel_0_9/dialects/sqlite.html#module-sqlalchemy.dialects.sqlite.pysqlite)
* [pymysql](http://docs.sqlalchemy.org/en/rel_0_9/dialects/mysql.html#module-sqlalchemy.dialects.mysql.pymysql)
* [pyodbc](https://docs.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server?view=sql-server-ver15)

# 组件安装

```shell
pip install -U service-sqlalchemy 
```

# 社区扩展

You may need extensions [awesome-sqlalchemy](https://github.com/dahlia/awesome-sqlalchemy)

# 配置文件

> config.yaml

```yaml
COMMAND:
  - service_sqlalchemy.cli.subcmds.migrate:Alembic
SQLALCHEMY:
  test:
    url: mysql+pymysql://${MYSQL_USER:root}:${MYSQL_PASS:toor}@${MYSQL_HOST:127.0.0.1}:${MYSQL_PORT:3306}/demo?charset=utf8mb4
    migrate_options:
      script_location: alembic/test
```

# 入门案例

```text
├── facade.py
├── config.yaml
└── project
    ├── __init__.py
    ├── service.py
    └── models
      ├── base.py
      ├── item.py
      └── user.py
```

> project/models/base.py

```python
#! -*- coding: utf-8 -*-
#
# author: forcemain@163.com

from __future__ import annotations

from sqlalchemy.ext.declarative import declarative_base

BaseModel = declarative_base()
```

> project/models/user.py

```python
#! -*- coding: utf-8 -*-
#
# author: forcemain@163.com

from __future__ import annotations

import sqlalchemy as sa
import sqlalchemy_utils as su

from .base import BaseModel


class User(BaseModel, su.Timestamp):
    """ 用户模型 """
    __tablename__ = 'users'
    __table_args__ = {
        'comment': '用户表'
    }

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True, comment='用户ID')
    name = sa.Column('用户名称', sa.String(64), nullable=False, comment='用户名称')
```

> project/models/item.py

```python
#! -*- coding: utf-8 -*-
#
# author: forcemain@163.com

from __future__ import annotations

import sqlalchemy as sa
import sqlalchemy_utils as su

from .base import BaseModel


class Item(BaseModel, su.Timestamp):
    """ 事物模型 """
    __tablename__ = 'items'
    __table_args__ = {
        'comment': '事物表'
    }

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True, comment='事务ID')
    name = sa.Column(sa.String(64), nullable=False, comment='事物名称')
```

> project/models/\_\_init\_\_.py

```python
#! -*- coding: utf-8 -*-
#
# author: forcemain@163.com

from __future__ import annotations

from .user import User
from .item import Item
```

> project/service.py

```python
#! -*- coding: utf-8 -*-
#
# author: forcemain@163.com

from __future__ import annotations

import typing as t

from logging import getLogger
from service_croniter.core.entrypoints import croniter
from service_sqlalchemy.core.dependencies import SQLAlchemy
from service_core.core.service import Service as BaseService
from service_sqlalchemy.core.shortcuts import update_or_create

from . import models

logger = getLogger(__name__)


class Service(BaseService):
    """ 微服务类 """

    # 微服务名称
    name = 'demo'
    # 微服务简介
    desc = 'demo'

    db_session = SQLAlchemy(alias='test', debug=True)

    def __init__(self, *args: t.Any, **kwargs: t.Any) -> None:
        # 此服务无需启动监听端口, 请初始化掉下面参数
        self.host = ''
        self.port = 0
        super(Service, self).__init__(*args, **kwargs)

    @croniter.cron('* * * * * */1')
    def test_database_update_or_create(self) -> None:
        """ 测试数据库存在更新不存在创建

        doc: https://github.com/kiorky/croniter
             https://docs.sqlalchemy.org/en/14/contents.html
             
        """
        # defaults不为空才会触发更新事件
        defaults = {'name': 'forcemain'}
        user = update_or_create(self.db_session,  # type: ignore
                                model=models.User,
                                defaults=defaults,
                                name='forcemain')
        logger.debug(f'yeah~ yeah~ yeah~, i am changed at {user.updated}')
```

> facade.py

```python
#! -*- coding: utf-8 -*-
#
# author: forcemain@163.com

from __future__ import annotations

from project import Service

service = Service()
```

# 执行迁移

:exclamation: --name值必须存在于SQLALCHEMY配置段下且script_location必须是init初始化时为此名称指定的目录名

:point_right: core alembic --name test init alembic/test

```text
├── alembic.ini
├── alembic
└── test
    ├── script.py.mako
    ├── env.py
    ├── README
    └── versions
```

:point_right: core alembic --name test revision --autogenerate -m "init"

> alembic/test/env.py

```python
from project.models.base import BaseModel

# 必须指定你所有自定义模型的基类模型用于数据迁移
target_metadata = BaseModel.metadata
```

> alembic/test/env.py

```python
import sqlalchemy as sa
# 为alembic迁移脚本注入sqlalchemy_utils支持
import sqlalchemy_utils as su
```

:point_right: core alembic --name test upgrade head

# 高级查询
```
├── facade.py
├── config.yaml
└── project
    ├── __init__.py
    ├── service.py
    └── models
      ├── base.py
      ├── user.py
      ├── role.py
      └── perm.py
```
> project/models/user.py
```python
#! -*- coding: utf-8 -*-
#
# author: forcemain@163.com

from __future__ import annotations

import sqlalchemy as sa

from sqlalchemy.orm import relationship

from .base import BaseModel


class User(BaseModel):
    """ 用户模型 """
    __tablename__ = 'users'
    __table_args__ = {
        'comment': '用户表'
    }

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True, comment='用户ID')
    name = sa.Column(sa.String(64), nullable=False, comment='用户名称')
    roles = relationship('Role')
```
> project/models/role.py
```python
#! -*- coding: utf-8 -*-
#
# author: forcemain@163.com

from __future__ import annotations

import sqlalchemy as sa

from sqlalchemy.orm import relationship

from .base import BaseModel


class Role(BaseModel):
    """ 角色模型 """
    __tablename__ = 'roles'
    __table_args__ = {
        'comment': '角色表'
    }

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True, comment='角色ID')
    name = sa.Column(sa.String(64), nullable=False, comment='角色名称')
    user_id = sa.Column(sa.Integer, sa.ForeignKey('users.id'))
    perm_id = sa.Column(sa.Integer, sa.ForeignKey('perms.id'))
    perms = relationship('Perm')
```
> project/models/perm.py
```python
#! -*- coding: utf-8 -*-
#
# author: forcemain@163.com

from __future__ import annotations

import sqlalchemy as sa

from .base import BaseModel


class Perm(BaseModel):
    """ 权限模型 """
    __tablename__ = 'perms'
    __table_args__ = {
        'comment': '权限表'
    }

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True, comment='权限ID')
    name = sa.Column(sa.String(64), nullable=False, comment='权限名称')
```
* [eq](https://docs.sqlalchemy.org/en/14/core/sqlelement.html#sqlalchemy.sql.expression.ColumnOperators.__eq__)
```python
from service_sqlalchemy.core.shortcuts import orm_json_search

result = orm_json_search(
    self.db_session,  # type: ignore
    module=models,
    query=['User.name'],
    filter_by={
        'field': 'User.name',
        'op': 'eq',  # 'eq', '==', 'equal', 'equals'
        'value': 'admin'
    }
)
```
* group_by
```python
from service_sqlalchemy.core.shortcuts import orm_json_search

result = orm_json_search(
    self.db_session,  # type: ignore
    module=models,
    query=[
        'User.name',
        {
            'field': 'User.name',
            'fn': 'count'
        }
    ],
    group_by=['User.name']
)
```

# 运行服务

> core start facade --debug

# 运行调试

> core debug --port `port`
