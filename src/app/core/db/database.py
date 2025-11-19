from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncEngine
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.pool import NullPool
from sqlalchemy.orm import DeclarativeBase, MappedAsDataclass

from ..config import settings


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
    },
    # Use NullPool to avoid prepared statement conflicts with Supabase's pooler
    # This creates a new connection for each request, avoiding prepared statement caching issues
    poolclass=NullPool,
)

local_session = async_sessionmaker(bind=async_engine, class_=AsyncSession, expire_on_commit=False)


async def async_get_db() -> AsyncGenerator[AsyncSession, None]:
    async with local_session() as db:
        yield db
