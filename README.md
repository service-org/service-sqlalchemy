# 运行环境

|system |python | 
|:------|:------|      
|cross platform |3.9.16|

# [注意事项](https://specs.openstack.org/openstack/openstack-specs/specs/eventlet-best-practices.html#database-drivers)

> 如下为已知在Eventlet协程下不会出现死锁的db driver, 数据库选型时请注意

- [pysqlite](https://docs.sqlalchemy.org/en/14/dialects/sqlite.html#module-sqlalchemy.dialects.sqlite.pysqlite)
- [pymysql](https://docs.sqlalchemy.org/en/14/dialects/mysql.html#module-sqlalchemy.dialects.mysql.pymysql)
- [pyodbc](https://docs.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server?view=sql-server-ver15)

# [社区扩展](https://github.com/dahlia/awesome-sqlalchemy)

# 组件安装

```shell
pip install -U service-sqlalchemy 
```

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
      ├── user.py
      ├── role.py
      ├── perm.py
      ├── role_perm.py
      ├── user_perm.py
      ├── user_role.py
      └── __init__.py
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

from sqlalchemy.orm import relationship

from .base import BaseModel
# secondary必须是Table对象
from .user_role import UserRole
from .user_perm import UserPerm


class User(BaseModel):
    """ 用户模型 """
    __tablename__ = 'user'
    __table_args__ = (
        # 字典配置必须放最底部
        {'comment': '用户表'},
    )

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True, comment='用户ID')
    name = sa.Column(sa.String(64), nullable=False, comment='用户名称')
    roles = relationship('Role', secondary=UserRole, back_populates='users')
    perms = relationship('Perm', secondary=UserPerm, back_populates='users')
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
# secondary必须是Table对象
from .user_role import UserRole
from .role_perm import RolePerm


class Role(BaseModel):
    """ 角色模型 """
    __tablename__ = 'role'
    __table_args__ = (
        # 字典配置必须放最底部
        {'comment': '角色表'},
    )

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True, comment='角色ID')
    name = sa.Column(sa.String(64), nullable=False, comment='角色名称')
    users = relationship('User', secondary=UserRole, back_populates='roles')
    perms = relationship('Perm', secondary=RolePerm, back_populates='roles')
```

> project/models/perm.py

```python
#! -*- coding: utf-8 -*-
#
# author: forcemain@163.com

from __future__ import annotations

import sqlalchemy as sa

from sqlalchemy.orm import relationship

from .base import BaseModel
# secondary必须是Table对象
from .user_perm import UserPerm
from .role_perm import RolePerm


class Perm(BaseModel):
    """ 权限模型 """
    __tablename__ = 'perm'
    __table_args__ = (
        # 字典配置必须放最底部
        {'comment': '权限表'}
    )

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True, comment='权限ID')
    name = sa.Column(sa.String(64), nullable=False, comment='权限名称')
    users = relationship('User', secondary=UserPerm, back_populates='perms')
    roles = relationship('Role', secondary=RolePerm, back_populates='perms')
```

> project/models/role_perm.py

```python
#! -*- coding: utf-8 -*-
#
# author: forcemain@163.com

from __future__ import annotations

import sqlalchemy as sa

from .base import BaseModel

# 角色权限
RolePerm = sa.Table(
    'role_perm',
    BaseModel.metadata,
    sa.Column('id', sa.Integer, primary_key=True, autoincrement=True, comment='关联ID'),
    sa.Column('role_id', sa.Integer, sa.ForeignKey('role.id'), nullable=False, comment='角色ID'),
    sa.Column('perm_id', sa.Integer, sa.ForeignKey('perm.id'), nullable=False, comment='权限ID')
)
```

> project/models/user_perm.py

```python
#! -*- coding: utf-8 -*-
#
# author: forcemain@163.com

from __future__ import annotations

import sqlalchemy as sa

from .base import BaseModel

# 用户权限
UserPerm = sa.Table(
    'user_perm',
    BaseModel.metadata,
    sa.Column('id', sa.Integer, primary_key=True, autoincrement=True, comment='关联ID'),
    sa.Column('user_id', sa.Integer, sa.ForeignKey('user.id'), nullable=False, comment='用户ID'),
    sa.Column('perm_id', sa.Integer, sa.ForeignKey('perm.id'), nullable=False, comment='权限ID')
)
```

> project/models/user_role.py

```python
#! -*- coding: utf-8 -*-
#
# author: forcemain@163.com

from __future__ import annotations

import sqlalchemy as sa

from .base import BaseModel

# 用户角色
UserRole = sa.Table(
    'user_role',
    BaseModel.metadata,
    sa.Column('id', sa.Integer, primary_key=True, autoincrement=True, comment='关联ID'),
    sa.Column('user_id', sa.Integer, sa.ForeignKey('user.id'), nullable=False, comment='用户ID'),
    sa.Column('role_id', sa.Integer, sa.ForeignKey('role.id'), nullable=False, comment='角色ID')
)
```

> project/models/\_\_init\_\_.py

```python
#! -*- coding: utf-8 -*-
#
# author: forcemain@163.com

from __future__ import annotations

from .user import User
from .role import Role
from .perm import Perm
from .user_role import UserRole
from .user_perm import UserPerm
from .role_perm import RolePerm

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
        defaults = {'name': 'admin'}
        update_or_create(self.db_session,  # type: ignore
                         model=models.Perm,
                         defaults=defaults,
                         name='admin')
        logger.debug(f'yeah~ yeah~ yeah~, i am changed')
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
├── ...........
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

# 运行服务

> core start facade --debug

# 运行调试

> core debug --port `port`

# 构造查询

> `orm_json_search`函数可将json转为orm查询表达式,支持高级查询语句的构建,更多功能等你挖掘~

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
from service_sqlalchemy.core.shortcuts import orm_json_search

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
    def test_database_orm_json_search(self) -> None:
        """ 测试构造数据库高级查询

        @return: None
        """
        """
        SELECT perm.id AS perm_id
        FROM perm
        WHERE perm.name = %(name_1)s
        """
        result = orm_json_search(
            self.db_session,  # type: ignore
            module=models,
            query=['Perm'],
            filter_by={
                'field': 'Perm.name',
                'op': 'eq',
                'value': 'admin'
            }
        )
        logger.debug(f'sql: {result} res: {result.all()}')
```

* [any](https://docs.sqlalchemy.org/en/14/orm/internals.html#sqlalchemy.orm.RelationshipProperty.Comparator.any)

```python
"""
SELECT `role`.id AS role_id, `role`.name AS role_name
FROM `role`
WHERE EXISTS (SELECT 1
FROM role_perm, perm
WHERE `role`.id = role_perm.role_id AND perm.id = role_perm.perm_id AND perm.name = %(name_1)s)
"""
result = orm_json_search(
    self.db_session,  # type: ignore
    module=models,
    query=['Role'],
    filter_by={
        'field': 'Role.perms',
        'op': 'any',
        'value': {
            'field': 'Perm.name',
            'op': 'eq',
            'value': 'can_view'
        }
    }
)
```

* [between](https://docs.sqlalchemy.org/en/14/core/sqlelement.html#sqlalchemy.sql.expression.ColumnOperators.between)

```python
"""
SELECT perm.id AS perm_id, perm.name AS perm_name
FROM perm
WHERE perm.id BETWEEN %(id_1)s AND %(id_2)s
"""
result = orm_json_search(
    self.db_session,  # type: ignore
    module=models,
    query=['Perm'],
    filter_by={
        'field': 'Perm.id',
        'op': 'between',
        'value': [1, 2]
    }
)
```

* [contains](https://docs.sqlalchemy.org/en/14/core/sqlelement.html#sqlalchemy.sql.expression.ColumnOperators.contains)

```python
"""
SELECT perm.id AS perm_id, perm.name AS perm_name
FROM perm
WHERE (perm.name LIKE concat(concat('%%', %(name_1)s), '%%'))
"""
result = orm_json_search(
    self.db_session,  # type: ignore
    module=models,
    query=['Perm'],
    filter_by={
        'field': 'Perm.name',
        'op': 'contains',
        'value': 'admin'
    }
)
```

* [endswith](https://docs.sqlalchemy.org/en/14/core/sqlelement.html#sqlalchemy.sql.expression.ColumnOperators.endswith)

```python
"""
SELECT perm.id AS perm_id, perm.name AS perm_name
FROM perm
WHERE (perm.name LIKE concat('%%', %(name_1)s))
"""
result = orm_json_search(
    self.db_session,  # type: ignore
    module=models,
    query=['Perm'],
    filter_by={
        'field': 'Perm.name',
        'op': 'endswith',
        'value': 'view'
    }
)
```

* [eq](https://docs.sqlalchemy.org/en/14/core/sqlelement.html#sqlalchemy.sql.expression.ColumnOperators.__eq__)

```python
"""
SELECT perm.id AS perm_id, perm.name AS perm_name
FROM perm
WHERE perm.name = %(name_1)s
"""
result = orm_json_search(
    self.db_session,  # type: ignore
    module=models,
    query=['Perm'],
    filter_by={
        'field': 'Perm.name',
        'op': 'eq',  # {'eq', '==', 'equal', 'equals'}
        'value': 'admin'
    }
)
```

* [ge](https://docs.sqlalchemy.org/en/14/core/sqlelement.html#sqlalchemy.sql.expression.ColumnElement.__ge__)

```python
"""
SELECT perm.id AS perm_id, perm.name AS perm_name
FROM perm
WHERE perm.id >= %(id_1)s
"""
result = orm_json_search(
    self.db_session,  # type: ignore
    module=models,
    query=['Perm'],
    filter_by={
        'field': 'Perm.id',
        'op': 'ge',  # {'>=', 'ge', 'gte', 'greater_than_equal', 'greater_than_equals'}
        'value': 1
    }
)
```

* [gt](https://docs.sqlalchemy.org/en/14/core/sqlelement.html#sqlalchemy.sql.expression.ColumnOperators.__gt__)

```python
"""
SELECT perm.id AS perm_id, perm.name AS perm_name
FROM perm
WHERE perm.id > %(id_1)s
"""
result = orm_json_search(
    self.db_session,  # type: ignore
    module=models,
    query=['Perm'],
    filter_by={
        'field': 'Perm.id',
        'op': 'gt',  # {'>', 'gt', 'greater_than'}
        'value': 1
    }
)
```

* [has](https://docs.sqlalchemy.org/en/14/orm/internals.html#sqlalchemy.orm.RelationshipProperty.Comparator.has)

```python

```

* [icontains](https://docs.sqlalchemy.org/en/14/core/sqlelement.html#sqlalchemy.sql.expression.ColumnOperators.contains)

```python
"""
SELECT perm.id AS perm_id, perm.name AS perm_name
FROM perm
WHERE lower(perm.name) LIKE lower(%(name_1)s)
"""
result = orm_json_search(
    self.db_session,  # type: ignore
    module=models,
    query=['Perm'],
    filter_by={
        'field': 'Perm.name',
        'op': 'icontains',
        'value': 'admin'
    }
)
```

* [iendswith](https://docs.sqlalchemy.org/en/14/core/sqlelement.html#sqlalchemy.sql.expression.ColumnOperators.endswith)

```python
"""
SELECT perm.id AS perm_id, perm.name AS perm_name
FROM perm
WHERE lower(perm.name) LIKE lower(%(name_1)s)
"""
result = orm_json_search(
    self.db_session,  # type: ignore
    module=models,
    query=['Perm'],
    filter_by={
        'field': 'Perm.name',
        'op': 'iendswith',
        'value': 'view'
    }
)
```

* [ilike](https://docs.sqlalchemy.org/en/14/core/sqlelement.html#sqlalchemy.sql.expression.ColumnOperators.ilike)

```python
"""
SELECT perm.id AS perm_id, perm.name AS perm_name
FROM perm
WHERE lower(perm.name) LIKE lower(%(name_1)s)
"""
result = orm_json_search(
    self.db_session,  # type: ignore
    module=models,
    query=['Perm'],
    filter_by={
        'field': 'Perm.name',
        'op': 'ilike',
        'value': 'can%'
    }
)
```

* [in](https://docs.sqlalchemy.org/en/14/core/sqlelement.html#sqlalchemy.sql.expression.ColumnOperators.in_)

```python
"""
SELECT perm.id AS perm_id, perm.name AS perm_name
FROM perm
WHERE perm.id IN ([POSTCOMPILE_id_1])
"""
result = orm_json_search(
    self.db_session,  # type: ignore
    module=models,
    query=['Perm'],
    filter_by={
        'field': 'Perm.id',
        'op': 'in',
        'value': [1, 2]
    }
)
```

* [is](https://docs.sqlalchemy.org/en/14/core/sqlelement.html#sqlalchemy.sql.expression.ColumnOperators.is_)

```python
"""
SELECT perm.id AS perm_id, perm.name AS perm_name
FROM perm
WHERE perm.name IS NULL
"""
result = orm_json_search(
    self.db_session,  # type: ignore
    module=models,
    query=['Perm'],
    filter_by={
        'field': 'Perm.name',
        'op': 'is',
        'value': None
    }
)
```

* [is_not](https://docs.sqlalchemy.org/en/14/core/sqlelement.html#sqlalchemy.sql.expression.ColumnOperators.is_not)

```python
"""
SELECT perm.id AS perm_id, perm.name AS perm_name
FROM perm
WHERE perm.name IS NOT NULL
"""
result = orm_json_search(
    self.db_session,  # type: ignore
    module=models,
    query=['Perm'],
    filter_by={
        'field': 'Perm.name',
        'op': 'isnot',  # {'isnot', 'is_not'}
        'value': None
    }
)
```

* [is_not_null](https://docs.sqlalchemy.org/en/14/core/sqlelement.html#sqlalchemy.sql.expression.ColumnOperators.is_not)

```python
"""
SELECT perm.id AS perm_id, perm.name AS perm_name
FROM perm
WHERE perm.name IS NOT NULL
"""
result = orm_json_search(
    self.db_session,  # type: ignore
    module=models,
    query=['Perm'],
    filter_by={
        'field': 'Perm.name',
        'op': 'isnotnull',  # {'isnotnull', 'is_not_null'}
        'value': None
    }
)
```

* [is_null](https://docs.sqlalchemy.org/en/14/core/sqlelement.html#sqlalchemy.sql.expression.ColumnOperators.is_)

```python
"""
SELECT perm.id AS perm_id, perm.name AS perm_name
FROM perm
WHERE perm.name IS NULL
"""
result = orm_json_search(
    self.db_session,  # type: ignore
    module=models,
    query=['Perm'],
    filter_by={
        'field': 'Perm.name',
        'op': 'isnull',  # {'isnull', 'is_null'}
        'value': None
    }
)
```

* [istartswith](https://docs.sqlalchemy.org/en/14/core/sqlelement.html#sqlalchemy.sql.expression.ColumnElement.ilike)

```python
"""
SELECT perm.id AS perm_id, perm.name AS perm_name
FROM perm
WHERE lower(perm.name) LIKE lower(%(name_1)s)
"""
result = orm_json_search(
    self.db_session,  # type: ignore
    module=models,
    query=['Perm'],
    filter_by={
        'field': 'Perm.name',
        'op': 'istartswith',
        'value': 'can'
    }
)
```

* [le](https://docs.sqlalchemy.org/en/14/core/sqlelement.html#sqlalchemy.sql.expression.ColumnElement.__le__)

```python
"""
SELECT perm.id AS perm_id, perm.name AS perm_name
FROM perm
WHERE perm.id <= %(id_1)s
"""
result = orm_json_search(
    self.db_session,  # type: ignore
    module=models,
    query=['Perm'],
    filter_by={
        'field': 'Perm.id',
        'op': 'le',  # {'<=', 'le', 'lte', 'less_than_equal', 'less_than_equals'}
        'value': 1
    }
)
```

* [like](https://docs.sqlalchemy.org/en/14/core/sqlelement.html#sqlalchemy.sql.expression.ColumnOperators.like)

```python
"""
SELECT perm.id AS perm_id, perm.name AS perm_name
FROM perm
WHERE perm.name LIKE %(name_1)s
"""
result = orm_json_search(
    self.db_session,  # type: ignore
    module=models,
    query=['Perm'],
    filter_by={
        'field': 'Perm.name',
        'op': 'like',
        'value': 'can%'
    }
)
```

* [lt](https://docs.sqlalchemy.org/en/14/core/sqlelement.html#sqlalchemy.sql.expression.ColumnElement.__lt__)

```python
"""
SELECT perm.id AS perm_id, perm.name AS perm_name
FROM perm
WHERE perm.id < %(id_1)s
"""
result = orm_json_search(
    self.db_session,  # type: ignore
    module=models,
    query=['Perm'],
    filter_by={
        'field': 'Perm.id',
        'op': 'lt',  # {'<', 'lt', 'less_than'}
        'value': 1
    }
)
```

* [ne](https://docs.sqlalchemy.org/en/14/core/sqlelement.html#sqlalchemy.sql.expression.ColumnElement.__ne__)

```python
"""
SELECT perm.id AS perm_id, perm.name AS perm_name
FROM perm
WHERE perm.name != %(name_1)s 
"""
result = orm_json_search(
    self.db_session,  # type: ignore
    module=models,
    query=['Perm'],
    filter_by={
        'field': 'Perm.name',
        'op': 'ne',  # {'ne', '!=', 'notequal', 'not_equal', 'notequals', 'not_equals'}
        'value': 'admin'
    }
)
```

* [not_in](https://docs.sqlalchemy.org/en/14/core/sqlelement.html#sqlalchemy.sql.expression.ColumnOperators.notin_)

```python
"""
SELECT perm.id AS perm_id, perm.name AS perm_name
FROM perm
WHERE (perm.id NOT IN ([POSTCOMPILE_id_1]))
"""
result = orm_json_search(
    self.db_session,  # type: ignore
    module=models,
    query=['Perm'],
    filter_by={
        'field': 'Perm.id',
        'op': 'notin',  # {'notin', 'not_in'}
        'value': [1]
    }
)
```

* [startswith](https://docs.sqlalchemy.org/en/14/core/sqlelement.html#sqlalchemy.sql.expression.ColumnOperators.startswith)

```python
"""
SELECT perm.id AS perm_id, perm.name AS perm_name
FROM perm
WHERE (perm.name LIKE concat(%(name_1)s, '%%'))
"""
result = orm_json_search(
    self.db_session,  # type: ignore
    module=models,
    query=['Perm'],
    filter_by={
        'field': 'Perm.name',
        'op': 'startswith',  # {'notin', 'not_in'}
        'value': 'can'
    }
)
```

* and

```python
"""
SELECT perm.id AS perm_id, perm.name AS perm_name
FROM perm
WHERE perm.id = %(id_1)s AND perm.name IS NOT NULL AND perm.name != %(name_1)s
"""
result = orm_json_search(
    self.db_session,  # type: ignore
    module=models,
    query=['Perm'],
    filter_by=[
        {
            'field': 'Perm.id',
            'op': 'eq',
            'value': 1
        },
        'and',
        [
            {
                'field': 'Perm.name',
                'op': 'isnot',
                'value': None
            },
            'and',
            {
                'field': 'Perm.name',
                'op': 'ne',
                'value': ''
            },
        ]
    ]
)
```

* or

```python
"""
SELECT perm.id AS perm_id, perm.name AS perm_name
FROM perm
WHERE perm.name IS NULL OR perm.name = %(name_1)s
"""
result = orm_json_search(
    self.db_session,  # type: ignore
    module=models,
    query=['Perm'],
    filter_by=[
        {
            'field': 'Perm.name',
            'op': 'is',
            'value': None
        },
        'or',
        {
            'field': 'Perm.name',
            'op': 'eq',
            'value': ''
        },
    ]
)
```
