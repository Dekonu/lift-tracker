"""Port for database session access (outbound / persistence)."""

from collections.abc import AsyncGenerator
from typing import Protocol

from sqlalchemy.ext.asyncio import AsyncSession


class DatabaseSessionPort(Protocol):
    """Port for obtaining an async database session. Implemented by persistence adapters."""

    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Yield a scoped async session. Caller does not own the session lifecycle."""
        ...
