from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncEngine
from sqlalchemy.ext.asyncio.session import AsyncSession
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
async_engine: AsyncEngine = create_async_engine(DATABASE_URL, echo=False, future=True)
local_session = async_sessionmaker(bind=async_engine, class_=AsyncSession, expire_on_commit=False)


async def async_get_db() -> AsyncGenerator[AsyncSession, None]:
    async with local_session() as db:
        yield db
