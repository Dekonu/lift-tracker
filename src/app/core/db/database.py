from collections.abc import AsyncGenerator, Callable
from typing import Any, TypeVar
import asyncio
import logging

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncEngine
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.pool import NullPool
from sqlalchemy.orm import DeclarativeBase, MappedAsDataclass

from ..config import settings

logger = logging.getLogger(__name__)
T = TypeVar('T')


class Base(DeclarativeBase, MappedAsDataclass):
    pass


def get_database_url() -> str:
    """Get database URL with validation."""
    try:
        database_uri = settings.database_uri
        database_prefix = settings.POSTGRES_ASYNC_PREFIX
        return f"{database_prefix}{database_uri}"
    except ValueError as e:
        raise ValueError(
            f"{e}\n\n"
            "To fix this, add one of the following to your src/.env file:\n"
            "  POSTGRES_URL=postgresql+asyncpg://postgres:[PASSWORD]@[HOST]:5432/postgres\n"
            "  OR\n"
            "  SUPABASE_DB_HOST=[YOUR-PROJECT-REF].supabase.co\n"
            "  SUPABASE_DB_PASSWORD=[YOUR-PASSWORD]\n"
            "  SUPABASE_DB_USER=postgres\n"
        ) from e


DATABASE_URL = get_database_url()

# Configure asyncpg to disable prepared statements to avoid conflicts with connection pooling
# This is especially important when using Supabase's pooler
# The DuplicatePreparedStatementError occurs because prepared statements are connection-specific
# and can conflict when using connection poolers
# 
# Solution: Use NullPool to avoid connection pooling conflicts with prepared statements.
# NullPool creates a new connection for each request, which avoids prepared statement caching
# conflicts. This is a workaround for Supabase's pooler which doesn't fully support prepared statements.
# 
# Note: For production, consider using Supabase's direct connection (not pooler) or
# implementing your own connection pooling that's compatible with prepared statements.
async_engine: AsyncEngine = create_async_engine(
    DATABASE_URL,
    echo=False,
    future=True,
    connect_args={
        "server_settings": {
            "application_name": "lift_tracker",
        },
        # Disable prepared statement cache to avoid DuplicatePreparedStatementError
        # This prevents asyncpg from caching prepared statements which conflict with poolers
        "statement_cache_size": 0,
        "command_timeout": 60,
    },
    # Use NullPool to avoid prepared statement conflicts with Supabase's pooler
    # This creates a new connection for each request, avoiding prepared statement caching issues
    poolclass=NullPool,
    pool_pre_ping=True,
)

# Note: The statement_cache_size=0 in connect_args should disable prepared statements
# However, if errors still occur, they will be caught and retried in the setup.py retry logic
# For runtime errors, we rely on NullPool creating fresh connections for each request

local_session = async_sessionmaker(bind=async_engine, class_=AsyncSession, expire_on_commit=False)


async def async_get_db() -> AsyncGenerator[AsyncSession, None]:
    async with local_session() as db:
        yield db


async def retry_on_prepared_statement_error(
    func: Callable[..., Any], 
    max_retries: int = 3,
    *args: Any,
    **kwargs: Any
) -> Any:
    """
    Retry a database operation if it encounters DuplicatePreparedStatementError.
    
    This is a workaround for Supabase's connection pooler which doesn't fully support
    prepared statements. When this error occurs, we retry with a fresh connection.
    """
    for attempt in range(max_retries):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            error_str = str(e)
            is_prepared_statement_error = (
                "DuplicatePreparedStatementError" in error_str 
                or "prepared statement" in error_str.lower()
            )
            
            if is_prepared_statement_error and attempt < max_retries - 1:
                wait_time = 0.1 * (attempt + 1)
                logger.debug(
                    f"Prepared statement error (attempt {attempt + 1}/{max_retries}). "
                    f"Retrying in {wait_time}s..."
                )
                await asyncio.sleep(wait_time)
                continue
            else:
                # Either not a prepared statement error, or we've exhausted retries
                raise
