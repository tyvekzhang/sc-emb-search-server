from threading import Lock
from typing import Dict, Union

from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine
from sqlalchemy.pool import NullPool
from sqlmodel import select
from src.main.app.common.config.config_manager import load_config
from src.main.app.common.enums.enum import ResponseCode
from src.main.app.common.exception.exception import SystemException
from src.main.app.common.session.db_session import db_session
from src.main.app.common.util.work_path_util import db_path

# Global engine cache with thread safety
_engine_map: Dict[str, AsyncEngine] = {}
_lock = Lock()

async_engine: AsyncEngine


def get_async_engine():
    global async_engine
    database_config = load_config().database
    if database_config.dialect.lower() == "sqlite":
        async_engine = create_async_engine(
            url=database_config.url,
            echo=database_config.echo_sql,
            pool_recycle=database_config.pool_recycle,
            pool_pre_ping=True,
        )
    else:
        async_engine = create_async_engine(
            url=database_config.url,
            echo=database_config.echo_sql,
            pool_size=database_config.pool_size,
            max_overflow=database_config.max_overflow,
            pool_recycle=database_config.pool_recycle,
            pool_pre_ping=True,
        )
    return async_engine
