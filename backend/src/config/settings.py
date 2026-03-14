from pathlib import Path
from typing import Literal, List

from pydantic import Field, PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).parent.parent.parent


class DatabaseSettings(BaseSettings):
    db: str = Field("lifetime_db", alias='POSTGRES_DB')
    host: str = Field("localhost", alias='POSTGRES_HOST')
    port: int = Field(5432, alias='POSTGRES_PORT')
    user: str = Field("postgres", alias='POSTGRES_USER')
    password: str = Field("12345678", alias='POSTGRES_PASSWORD')

    @property
    def dsn(self) -> PostgresDsn:
        return PostgresDsn.build(
            scheme="postgresql+asyncpg",
            username=self.user,
            password=self.password,
            host=self.host,
            port=self.port,
            path=self.db,
            query="async_fallback=True"
        )

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        extra="ignore",
    )


class AuthSettings(BaseSettings):
    secret_key: str = Field("secret", alias='AUTH_SECRET_KEY')
    algorithm: str = Field("RS256", alias='AUTH_ALGORITHM')
    access_token_expire_minutes: int = Field(15, alias='AUTH_ACCESS_TOKEN_EXPIRE_MINUTES')
    refresh_token_expire_days: int = Field(30, alias='AUTH_REFRESH_TOKEN_EXPIRE_DAYS')

    private_key_path: Path = BASE_DIR / 'src' / 'jwt-certs' / 'jwt-private.pem'
    public_key_path: Path = BASE_DIR / 'src' / 'jwt-certs' / 'jwt-public.pem'

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        extra="ignore",
    )


class AppSettings(BaseSettings):
    port: int = Field(8000, alias='APP_PORT')
    host: str = Field("localhost", alias='APP_HOST')
    name: str = Field("Life Time", alias='APP_NAME')
    mode: Literal['DEV', 'PROD'] = Field("DEV", alias='APP_MODE')
    ALLOWED_HOSTS: List[str] = Field(default_factory=list, alias='APP_ALLOWED_HOSTS', )

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        extra="ignore",
    )

class S3Settings(BaseSettings):
    access_key: str = Field(alias="S3_ACCESS_KEY")
    secret_key: str = Field(alias="S3_SECRET_KEY")
    endpoint_url: str = Field(alias="S3_ENDPOINT_URL")

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        extra="ignore",
    )


class RedisSettings(BaseSettings):
    host: str = Field("localhost", alias="REDIS_HOST")
    port: int = Field(6379, alias="REDIS_PORT")

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        extra="ignore",
    )


class WorkerSettings(BaseSettings):
    check_interval_seconds: int = Field(300, alias="WORKER_CHECK_INTERVAL_SECONDS")
    request_timeout_seconds: int = Field(10, alias="WORKER_REQUEST_TIMEOUT_SECONDS")
    max_concurrent_checks: int = Field(20, alias="WORKER_MAX_CONCURRENT_CHECKS")

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        extra="ignore",
    )


class Settings(BaseSettings):
    app: AppSettings = AppSettings()
    auth: AuthSettings = AuthSettings()
    db: DatabaseSettings = DatabaseSettings()
    s3: S3Settings = S3Settings()
    redis: RedisSettings = RedisSettings()
    worker: WorkerSettings = WorkerSettings()

    model_config = SettingsConfigDict(
        env_nested_delimiter="__",
        env_file=BASE_DIR / ".env",
        extra="ignore",
    )


settings = Settings()
IS_DEBUG = settings.app.mode == "DEV"
