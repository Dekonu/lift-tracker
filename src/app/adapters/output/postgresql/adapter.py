"""PostgreSQL adapter: implements DatabaseSessionPort for async SQLAlchemy sessions."""

import logging
from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from ....core.config import get_async_database_url
from ...ports.database import DatabaseSessionPort

logger = logging.getLogger(__name__)

DATABASE_URL = get_async_database_url()

_connect_args: dict = {}
if not DATABASE_URL.startswith("sqlite"):
    _connect_args = {
        "server_settings": {"application_name": "lift_tracker"},
        "statement_cache_size": 0,
        "command_timeout": 60,
    }

async_engine: AsyncEngine = create_async_engine(
    DATABASE_URL,
    echo=False,
    future=True,
    connect_args=_connect_args,
    poolclass=NullPool if not DATABASE_URL.startswith("sqlite") else None,
    pool_pre_ping=not DATABASE_URL.startswith("sqlite"),
)

postgres_session_factory = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Yield a scoped async session (implements DatabaseSessionPort)."""
    async with postgres_session_factory() as session:
        yield session


def get_postgres_session_port() -> DatabaseSessionPort:
    """Return the PostgreSQL adapter as the database session port (for dependency injection)."""
    return _PostgresSessionAdapter()


async def async_get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency: yield a database session. Re-exports get_session for backward compatibility."""
    async for session in get_session():
        yield session


class _PostgresSessionAdapter:
    """Implements DatabaseSessionPort using PostgreSQL."""

    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        async with postgres_session_factory() as session:
            yield session
