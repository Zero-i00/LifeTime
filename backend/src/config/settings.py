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

class Settings(BaseSettings):
    app: AppSettings = AppSettings()
    auth: AuthSettings = AuthSettings()
    db: DatabaseSettings = DatabaseSettings()

    model_config = SettingsConfigDict(
        env_nested_delimiter="__",
        env_file=BASE_DIR / ".env",
        extra="ignore",
    )


settings = Settings()
IS_DEBUG = settings.app.mode == "DEV"
