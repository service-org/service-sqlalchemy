#! -*- coding: utf-8 -*-
#
# author: forcemain@163.com

from __future__ import annotations

import sys

from logging import getLogger
from argparse import Namespace
from alembic.config import Config
from argparse import ArgumentParser
from alembic.config import CommandLine
from sqlalchemy_utils import create_database
from sqlalchemy_utils import database_exists
from service_core.cli.subcmds import BaseCommand
from service_core.core.configure import Configure
from service_sqlalchemy.constants import SQLALCHEMY_CONFIG_KEY

logger = getLogger(__name__)


class Alembic(BaseCommand):
    """ 管理sqlalchemy迁移 """

    name = 'alembic'
    help = 'manage sqlalchemy migration'
    desc = 'manage sqlalchemy migration'

    @classmethod
    def init_parser(cls, parser: ArgumentParser, config: Configure) -> None:
        """ 自定义子命令

        @param parser: 解析对象
        @param config: 配置字典
        @return: None
        """
        alembic_cmd_cli = CommandLine(prog=f'core {cls.name}')
        alembic_parsers = alembic_cmd_cli.parser
        parser.__dict__ = alembic_parsers.__dict__

    @classmethod
    def main(cls, namespace: Namespace, *, config: Configure) -> None:
        """ 子命令入口

        @param namespace: 命名空间
        @param config: 配置字典
        @return: None
        """
        alembic_cmd_cli = CommandLine(prog=f'core {cls.name}')
        alembic_parsers = alembic_cmd_cli.parser
        alembic_options = alembic_parsers.parse_args(sys.argv[2:])
        not hasattr(alembic_options, 'cmd') and alembic_parsers.error('too few arguments')
        alembic_configs = Config(file_=alembic_options.config,
                                 ini_section=alembic_options.name, cmd_opts=alembic_options)
        # https://alembic.sqlalchemy.org/en/latest/cookbook.html#run-multiple-alembic-environments-from-one-ini-file
        section_curr_name = alembic_options.name
        migrate_used_urls = config.get(f'{SQLALCHEMY_CONFIG_KEY}.{section_curr_name}.url', default='')
        database_exists(migrate_used_urls) or create_database(migrate_used_urls)
        alembic_configs.set_section_option(section_curr_name, 'sqlalchemy.url', migrate_used_urls)
        migrate_options = config.get(f'{SQLALCHEMY_CONFIG_KEY}.{section_curr_name}.migrate_options', default={})
        migrate_options = migrate_options or {}
        for option_name, option_data in migrate_options.items():
            alembic_configs.set_section_option(section_curr_name, option_name, option_data)
        else:
            logger.debug('sqlalchemy doc https://docs.sqlalchemy.org/en/14/contents.html')
            logger.debug('alembic doc https://alembic.sqlalchemy.org/en/latest/index.html')
            logger.debug('sqlalchemy-utils doc https://sqlalchemy-utils.readthedocs.io/en/latest/')
        alembic_cmd_cli.run_cmd(alembic_configs, alembic_options)
