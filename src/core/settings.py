from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='.env', env_file_encoding='utf-8'
    )
    ENVIRONMENT: str = 'development'

    DB_USER: str
    DB_PASSWORD: str
    DB_DATABASE: str
    DB_ADDRESS: str
    DB_PORT: int = 5432

    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = 'HS256'
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 15

    OTLP_ENDPOINT: Optional[str] = None

    @property
    def DATABASE_URL(self) -> str:
        return f'postgresql+psycopg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_ADDRESS}:{self.DB_PORT}/{self.DB_DATABASE}'
