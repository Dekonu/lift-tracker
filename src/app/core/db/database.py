"""Database: declarative Base and session dependency. Persistence is implemented by adapters."""

import asyncio
import logging
from collections.abc import AsyncGenerator, Callable
from typing import Any, TypeVar

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase, MappedAsDataclass

from ...adapters.output.postgresql import async_engine, async_get_db

logger = logging.getLogger(__name__)
T = TypeVar("T")


class Base(DeclarativeBase, MappedAsDataclass):
    """SQLAlchemy declarative base. Metadata is used by Alembic and the PostgreSQL adapter."""


# Re-export for backward compatibility; implementation lives in adapters.output.postgresql
__all__ = ["Base", "async_engine", "async_get_db", "retry_on_prepared_statement_error"]


async def retry_on_prepared_statement_error(
    func: Callable[..., Any], max_retries: int = 3, *args: Any, **kwargs: Any
) -> Any:
    """
    Retry a database operation if it encounters DuplicatePreparedStatementError.
    Useful when using connection poolers that do not fully support prepared statements.
    """
    for attempt in range(max_retries):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            error_str = str(e)
            is_prepared_statement_error = (
                "DuplicatePreparedStatementError" in error_str or "prepared statement" in error_str.lower()
            )

            if is_prepared_statement_error and attempt < max_retries - 1:
                wait_time = 0.1 * (attempt + 1)
                logger.debug(
                    "Prepared statement error (attempt %s/%s). Retrying in %ss...",
                    attempt + 1,
                    max_retries,
                    wait_time,
                )
                await asyncio.sleep(wait_time)
                continue
            raise
