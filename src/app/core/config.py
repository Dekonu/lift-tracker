import os
from enum import Enum

from pydantic import SecretStr
from pydantic_settings import BaseSettings
from starlette.config import Config

current_file_dir = os.path.dirname(os.path.realpath(__file__))
env_path = os.path.join(current_file_dir, "..", "..", ".env")
config = Config(env_path)


def get_config(key: str, default: str | None = None, cast=None):
    """Safely get config value with default fallback."""
    try:
        if cast:
            return config(key, cast=cast, default=default)
        return config(key, default=default)
    except KeyError:
        # If key is missing and no default provided, return None or cast default
        if default is None:
            return None
        if cast:
            # Handle boolean casting
            if cast == bool:
                return default.lower() in ('true', '1', 'yes', 'on') if isinstance(default, str) else bool(default)
            return cast(default)
        return default
    except Exception:
        # For any other error (like file not found), return the default
        if default is None:
            return None
        if cast:
            # Handle boolean casting
            if cast == bool:
                return default.lower() in ('true', '1', 'yes', 'on') if isinstance(default, str) else bool(default)
            return cast(default)
        return default


class AppSettings(BaseSettings):
    APP_NAME: str = config("APP_NAME", default="FastAPI app")
    APP_DESCRIPTION: str | None = config("APP_DESCRIPTION", default=None)
    APP_VERSION: str | None = config("APP_VERSION", default=None)
    LICENSE_NAME: str | None = config("LICENSE", default=None)
    CONTACT_NAME: str | None = config("CONTACT_NAME", default=None)
    CONTACT_EMAIL: str | None = config("CONTACT_EMAIL", default=None)


class CryptSettings(BaseSettings):
    SECRET_KEY: SecretStr = get_config("SECRET_KEY", default="_iKGN8PWR4WcQU4EoCRXzjjGNMcYT1GjPaahCtEm0bI", cast=SecretStr)
    ALGORITHM: str = get_config("ALGORITHM", default="HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = get_config("ACCESS_TOKEN_EXPIRE_MINUTES", default=30)
    REFRESH_TOKEN_EXPIRE_DAYS: int = get_config("REFRESH_TOKEN_EXPIRE_DAYS", default=7)


class DatabaseSettings(BaseSettings):
    pass


class SQLiteSettings(DatabaseSettings):
    SQLITE_URI: str = config("SQLITE_URI", default="./sql_app.db")
    SQLITE_SYNC_PREFIX: str = config("SQLITE_SYNC_PREFIX", default="sqlite:///")
    SQLITE_ASYNC_PREFIX: str = config("SQLITE_ASYNC_PREFIX", default="sqlite+aiosqlite:///")


class MySQLSettings(DatabaseSettings):
    MYSQL_USER: str = config("MYSQL_USER", default="username")
    MYSQL_PASSWORD: str = config("MYSQL_PASSWORD", default="password")
    MYSQL_SERVER: str = config("MYSQL_SERVER", default="localhost")
    MYSQL_PORT: int = config("MYSQL_PORT", default=5432)
    MYSQL_DB: str = config("MYSQL_DB", default="dbname")
    MYSQL_URI: str = f"{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_SERVER}:{MYSQL_PORT}/{MYSQL_DB}"
    MYSQL_SYNC_PREFIX: str = config("MYSQL_SYNC_PREFIX", default="mysql://")
    MYSQL_ASYNC_PREFIX: str = config("MYSQL_ASYNC_PREFIX", default="mysql+aiomysql://")
    MYSQL_URL: str | None = config("MYSQL_URL", default=None)


class SupabaseSettings(DatabaseSettings):
    SUPABASE_URL: str = config("SUPABASE_URL", default="")
    SUPABASE_DB_PASSWORD: str = config("SUPABASE_DB_PASSWORD", default="")
    SUPABASE_DB_HOST: str = config("SUPABASE_DB_HOST", default="")
    SUPABASE_DB_PORT: int = config("SUPABASE_DB_PORT", default=5432)
    SUPABASE_DB_NAME: str = config("SUPABASE_DB_NAME", default="postgres")
    SUPABASE_DB_USER: str = config("SUPABASE_DB_USER", default="postgres")
    POSTGRES_SYNC_PREFIX: str = config("POSTGRES_SYNC_PREFIX", default="postgresql://")
    POSTGRES_ASYNC_PREFIX: str = config("POSTGRES_ASYNC_PREFIX", default="postgresql+asyncpg://")
    POSTGRES_URI: str | None = config("POSTGRES_URI", default=None)
    POSTGRES_URL: str | None = config("POSTGRES_URL", default=None)
    
    @property
    def database_uri(self) -> str:
        """Get database URI, preferring direct URL or constructing from components."""
        if self.POSTGRES_URL:
            return self.POSTGRES_URL.replace("postgresql://", "").replace("postgresql+asyncpg://", "")
        if self.POSTGRES_URI:
            return self.POSTGRES_URI
        return f"{self.SUPABASE_DB_USER}:{self.SUPABASE_DB_PASSWORD}@{self.SUPABASE_DB_HOST}:{self.SUPABASE_DB_PORT}/{self.SUPABASE_DB_NAME}"


class FirstUserSettings(BaseSettings):
    ADMIN_NAME: str = config("ADMIN_NAME", default="admin")
    ADMIN_EMAIL: str = config("ADMIN_EMAIL", default="admin@admin.com")
    ADMIN_PASSWORD: str = config("ADMIN_PASSWORD", default="!Ch4ng3Th1sP4ssW0rd!")


class TestSettings(BaseSettings): ...


class RedisCacheSettings(BaseSettings):
    REDIS_CACHE_ENABLED: bool = False
    REDIS_CACHE_HOST: str = config("REDIS_CACHE_HOST", default="localhost")
    REDIS_CACHE_PORT: int = config("REDIS_CACHE_PORT", default=6379)
    REDIS_CACHE_URL: str = f"redis://{REDIS_CACHE_HOST}:{REDIS_CACHE_PORT}"
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Check if Redis is enabled in config, default to False
        try:
            enabled = config("REDIS_CACHE_ENABLED", default="false")
            self.REDIS_CACHE_ENABLED = str(enabled).lower() in ('true', '1', 'yes', 'on')
        except Exception:
            self.REDIS_CACHE_ENABLED = False


class ClientSideCacheSettings(BaseSettings):
    CLIENT_CACHE_MAX_AGE: int = config("CLIENT_CACHE_MAX_AGE", default=60)


class RedisQueueSettings(BaseSettings):
    REDIS_QUEUE_ENABLED: bool = False
    REDIS_QUEUE_HOST: str = config("REDIS_QUEUE_HOST", default="localhost")
    REDIS_QUEUE_PORT: int = config("REDIS_QUEUE_PORT", default=6379)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Check if Redis is enabled in config, default to False
        try:
            enabled = config("REDIS_QUEUE_ENABLED", default="false")
            self.REDIS_QUEUE_ENABLED = str(enabled).lower() in ('true', '1', 'yes', 'on')
        except Exception:
            self.REDIS_QUEUE_ENABLED = False


class RedisRateLimiterSettings(BaseSettings):
    REDIS_RATE_LIMIT_ENABLED: bool = False
    REDIS_RATE_LIMIT_HOST: str = config("REDIS_RATE_LIMIT_HOST", default="localhost")
    REDIS_RATE_LIMIT_PORT: int = config("REDIS_RATE_LIMIT_PORT", default=6379)
    REDIS_RATE_LIMIT_URL: str = f"redis://{REDIS_RATE_LIMIT_HOST}:{REDIS_RATE_LIMIT_PORT}"
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Check if Redis is enabled in config, default to False
        try:
            enabled = config("REDIS_RATE_LIMIT_ENABLED", default="false")
            self.REDIS_RATE_LIMIT_ENABLED = str(enabled).lower() in ('true', '1', 'yes', 'on')
        except Exception:
            self.REDIS_RATE_LIMIT_ENABLED = False


class DefaultRateLimitSettings(BaseSettings):
    DEFAULT_RATE_LIMIT_LIMIT: int = config("DEFAULT_RATE_LIMIT_LIMIT", default=10)
    DEFAULT_RATE_LIMIT_PERIOD: int = config("DEFAULT_RATE_LIMIT_PERIOD", default=3600)


class CRUDAdminSettings(BaseSettings):
    CRUD_ADMIN_ENABLED: bool = False
    CRUD_ADMIN_MOUNT_PATH: str = config("CRUD_ADMIN_MOUNT_PATH", default="/admin")

    CRUD_ADMIN_ALLOWED_IPS_LIST: list[str] | None = None
    CRUD_ADMIN_ALLOWED_NETWORKS_LIST: list[str] | None = None
    CRUD_ADMIN_MAX_SESSIONS: int = config("CRUD_ADMIN_MAX_SESSIONS", default=10)
    CRUD_ADMIN_SESSION_TIMEOUT: int = config("CRUD_ADMIN_SESSION_TIMEOUT", default=1440)
    SESSION_SECURE_COOKIES: bool = config("SESSION_SECURE_COOKIES", default=True)

    CRUD_ADMIN_TRACK_EVENTS: bool = config("CRUD_ADMIN_TRACK_EVENTS", default=True)
    CRUD_ADMIN_TRACK_SESSIONS: bool = config("CRUD_ADMIN_TRACK_SESSIONS", default=True)

    CRUD_ADMIN_REDIS_ENABLED: bool = config("CRUD_ADMIN_REDIS_ENABLED", default=False)
    CRUD_ADMIN_REDIS_HOST: str = config("CRUD_ADMIN_REDIS_HOST", default="localhost")
    CRUD_ADMIN_REDIS_PORT: int = config("CRUD_ADMIN_REDIS_PORT", default=6379)
    CRUD_ADMIN_REDIS_DB: int = config("CRUD_ADMIN_REDIS_DB", default=0)
    CRUD_ADMIN_REDIS_PASSWORD: str | None = config("CRUD_ADMIN_REDIS_PASSWORD", default="None")
    CRUD_ADMIN_REDIS_SSL: bool = config("CRUD_ADMIN_REDIS_SSL", default=False)


class EnvironmentOption(Enum):
    LOCAL = "local"
    STAGING = "staging"
    PRODUCTION = "production"


class EnvironmentSettings(BaseSettings):
    ENVIRONMENT: EnvironmentOption = config("ENVIRONMENT", default=EnvironmentOption.LOCAL)


class Settings(
    AppSettings,
    SQLiteSettings,
    SupabaseSettings,
    CryptSettings,
    FirstUserSettings,
    TestSettings,
    RedisCacheSettings,
    ClientSideCacheSettings,
    RedisQueueSettings,
    RedisRateLimiterSettings,
    DefaultRateLimitSettings,
    CRUDAdminSettings,
    EnvironmentSettings,
):
    pass


settings = Settings()
