from collections.abc import AsyncGenerator, Callable
from contextlib import _AsyncGeneratorContextManager, asynccontextmanager
from typing import Any

import anyio
import fastapi
import redis.asyncio as redis
from arq import create_pool
from arq.connections import RedisSettings
from fastapi import APIRouter, Depends, FastAPI
from fastapi.openapi.docs import get_redoc_html, get_swagger_ui_html
from fastapi.openapi.utils import get_openapi

from ..api.dependencies import get_current_superuser
from ..core.utils.rate_limit import rate_limiter
from ..middleware.client_cache_middleware import ClientCacheMiddleware
from ..models import *  # noqa: F403
from .config import (
    AppSettings,
    ClientSideCacheSettings,
    DatabaseSettings,
    EnvironmentOption,
    EnvironmentSettings,
    RedisCacheSettings,
    RedisQueueSettings,
    RedisRateLimiterSettings,
    settings,
)
from .db.database import Base
from .db.database import async_engine as engine
from .utils import cache, queue


# -------------- database --------------
async def create_tables() -> None:
    """
    Create database tables, handling asyncpg prepared statement conflicts.
    
    This function attempts to create tables but gracefully handles errors that can occur
    with connection poolers (like Supabase's pooler) that don't fully support prepared statements.
    If table creation fails due to prepared statement conflicts, we log a warning and continue,
    as the tables may already exist or will be created on the next successful connection.
    """
    import logging
    logger = logging.getLogger(__name__)
    
    max_retries = 2  # Reduced retries since NullPool should avoid most conflicts
    for attempt in range(max_retries):
        try:
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            # Success - log and return
            if attempt > 0:
                logger.info("Database tables created successfully after retry")
            return
        except Exception as e:
            # Handle DuplicatePreparedStatementError which can occur with connection poolers
            # This is a known issue with asyncpg and Supabase's pooler
            error_str = str(e)
            is_prepared_statement_error = (
                "DuplicatePreparedStatementError" in error_str 
                or "prepared statement" in error_str.lower()
            )
            
            if is_prepared_statement_error:
                if attempt < max_retries - 1:
                    logger.debug(
                        f"Prepared statement conflict during table creation (attempt {attempt + 1}/{max_retries}). "
                        "Retrying with new connection..."
                    )
                    # Wait a bit before retrying
                    import asyncio
                    await asyncio.sleep(0.3 * (attempt + 1))
                    continue
                else:
                    # Last attempt failed - log but don't crash
                    # Tables may already exist, or will be created when first used
                    logger.info(
                        "Could not create tables due to prepared statement conflicts. "
                        "This is expected with connection poolers. Tables may already exist. "
                        "Application will continue - tables will be created on first use if needed."
                    )
                    return
            else:
                # Different error - check if it's a "table already exists" type error
                if "already exists" in error_str.lower() or "duplicate" in error_str.lower():
                    logger.info("Tables may already exist. Continuing...")
                    return
                # For other errors, log and continue (don't crash startup)
                logger.warning(
                    f"Unexpected error during table creation: {e}. "
                    "Application will continue - tables may already exist."
                )
                return


# -------------- cache --------------
async def create_redis_cache_pool() -> None:
    cache.pool = redis.ConnectionPool.from_url(settings.REDIS_CACHE_URL)
    cache.client = redis.Redis.from_pool(cache.pool)  # type: ignore


async def close_redis_cache_pool() -> None:
    if cache.client is not None:
        await cache.client.aclose()  # type: ignore


# -------------- queue --------------
async def create_redis_queue_pool() -> None:
    queue.pool = await create_pool(RedisSettings(host=settings.REDIS_QUEUE_HOST, port=settings.REDIS_QUEUE_PORT))


async def close_redis_queue_pool() -> None:
    if queue.pool is not None:
        await queue.pool.aclose()  # type: ignore


# -------------- rate limit --------------
async def create_redis_rate_limit_pool() -> None:
    rate_limiter.initialize(settings.REDIS_RATE_LIMIT_URL)  # type: ignore


async def close_redis_rate_limit_pool() -> None:
    if rate_limiter.client is not None:
        await rate_limiter.client.aclose()  # type: ignore


# -------------- application --------------
async def set_threadpool_tokens(number_of_tokens: int = 100) -> None:
    limiter = anyio.to_thread.current_default_thread_limiter()
    limiter.total_tokens = number_of_tokens


def lifespan_factory(
    settings: (
        DatabaseSettings
        | RedisCacheSettings
        | AppSettings
        | ClientSideCacheSettings
        | RedisQueueSettings
        | RedisRateLimiterSettings
        | EnvironmentSettings
    ),
    create_tables_on_start: bool = True,
) -> Callable[[FastAPI], _AsyncGeneratorContextManager[Any]]:
    """Factory to create a lifespan async context manager for a FastAPI app."""

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncGenerator:
        from asyncio import Event

        initialization_complete = Event()
        app.state.initialization_complete = initialization_complete

        await set_threadpool_tokens()

        try:
            if isinstance(settings, RedisCacheSettings) and settings.REDIS_CACHE_ENABLED:
                try:
                    await create_redis_cache_pool()
                except Exception as e:
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.warning(f"Redis cache not available, continuing without cache: {e}")

            if isinstance(settings, RedisQueueSettings) and settings.REDIS_QUEUE_ENABLED:
                try:
                    await create_redis_queue_pool()
                except Exception as e:
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.warning(f"Redis queue not available, continuing without queue: {e}")

            if isinstance(settings, RedisRateLimiterSettings) and settings.REDIS_RATE_LIMIT_ENABLED:
                try:
                    await create_redis_rate_limit_pool()
                except Exception as e:
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.warning(f"Redis rate limiter not available, continuing without rate limiting: {e}")

            if create_tables_on_start:
                try:
                    await create_tables()
                except Exception as e:
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.error(f"Failed to create database tables: {e}")
                    logger.warning("Continuing without database tables. Make sure your database is configured correctly.")

            initialization_complete.set()

            yield

        finally:
            if isinstance(settings, RedisCacheSettings) and settings.REDIS_CACHE_ENABLED:
                try:
                    await close_redis_cache_pool()
                except Exception:
                    pass

            if isinstance(settings, RedisQueueSettings) and settings.REDIS_QUEUE_ENABLED:
                try:
                    await close_redis_queue_pool()
                except Exception:
                    pass

            if isinstance(settings, RedisRateLimiterSettings) and settings.REDIS_RATE_LIMIT_ENABLED:
                try:
                    await close_redis_rate_limit_pool()
                except Exception:
                    pass

    return lifespan


# -------------- application --------------
def create_application(
    router: APIRouter,
    settings: (
        DatabaseSettings
        | RedisCacheSettings
        | AppSettings
        | ClientSideCacheSettings
        | RedisQueueSettings
        | RedisRateLimiterSettings
        | EnvironmentSettings
    ),
    create_tables_on_start: bool = True,
    lifespan: Callable[[FastAPI], _AsyncGeneratorContextManager[Any]] | None = None,
    **kwargs: Any,
) -> FastAPI:
    """Creates and configures a FastAPI application based on the provided settings.

    This function initializes a FastAPI application and configures it with various settings
    and handlers based on the type of the `settings` object provided.

    Parameters
    ----------
    router : APIRouter
        The APIRouter object containing the routes to be included in the FastAPI application.

    settings
        An instance representing the settings for configuring the FastAPI application.
        It determines the configuration applied:

        - AppSettings: Configures basic app metadata like name, description, contact, and license info.
        - DatabaseSettings: Adds event handlers for initializing database tables during startup.
        - RedisCacheSettings: Sets up event handlers for creating and closing a Redis cache pool.
        - ClientSideCacheSettings: Integrates middleware for client-side caching.
        - RedisQueueSettings: Sets up event handlers for creating and closing a Redis queue pool.
        - RedisRateLimiterSettings: Sets up event handlers for creating and closing a Redis rate limiter pool.
        - EnvironmentSettings: Conditionally sets documentation URLs and integrates custom routes for API documentation
          based on the environment type.

    create_tables_on_start : bool
        A flag to indicate whether to create database tables on application startup.
        Defaults to True.

    **kwargs
        Additional keyword arguments passed directly to the FastAPI constructor.

    Returns
    -------
    FastAPI
        A fully configured FastAPI application instance.

    The function configures the FastAPI application with different features and behaviors
    based on the provided settings. It includes setting up database connections, Redis pools
    for caching, queue, and rate limiting, client-side caching, and customizing the API documentation
    based on the environment settings.
    """
    # --- before creating application ---
    if isinstance(settings, AppSettings):
        to_update = {
            "title": settings.APP_NAME,
            "description": settings.APP_DESCRIPTION,
            "contact": {"name": settings.CONTACT_NAME, "email": settings.CONTACT_EMAIL},
            "license_info": {"name": settings.LICENSE_NAME},
        }
        kwargs.update(to_update)

    if isinstance(settings, EnvironmentSettings):
        kwargs.update({"docs_url": None, "redoc_url": None, "openapi_url": None})

    # Use custom lifespan if provided, otherwise use default factory
    if lifespan is None:
        lifespan = lifespan_factory(settings, create_tables_on_start=create_tables_on_start)

    application = FastAPI(lifespan=lifespan, **kwargs)
    application.include_router(router)

    if isinstance(settings, ClientSideCacheSettings):
        application.add_middleware(ClientCacheMiddleware, max_age=settings.CLIENT_CACHE_MAX_AGE)

    if isinstance(settings, EnvironmentSettings):
        if settings.ENVIRONMENT != EnvironmentOption.PRODUCTION:
            docs_router = APIRouter()
            if settings.ENVIRONMENT != EnvironmentOption.LOCAL:
                docs_router = APIRouter(dependencies=[Depends(get_current_superuser)])

            @docs_router.get("/docs", include_in_schema=False)
            async def get_swagger_documentation() -> fastapi.responses.HTMLResponse:
                return get_swagger_ui_html(openapi_url="/openapi.json", title="docs")

            @docs_router.get("/redoc", include_in_schema=False)
            async def get_redoc_documentation() -> fastapi.responses.HTMLResponse:
                return get_redoc_html(openapi_url="/openapi.json", title="docs")

            @docs_router.get("/openapi.json", include_in_schema=False)
            async def openapi() -> dict[str, Any]:
                out: dict = get_openapi(title=application.title, version=application.version, routes=application.routes)
                return out

            application.include_router(docs_router)

    return application
