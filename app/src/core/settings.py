import logging
from typing import Optional

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)

_DEFAULT_JWT_KEY = 'supersecretkey'


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

    JWT_SECRET_KEY: str = _DEFAULT_JWT_KEY
    JWT_ALGORITHM: str = 'HS256'
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 15

    OTLP_ENDPOINT: Optional[str] = None

    @model_validator(mode='after')
    def validate_jwt_secret(self) -> 'Settings':
        if (
            self.ENVIRONMENT != 'development'
            and self.JWT_SECRET_KEY == _DEFAULT_JWT_KEY
            or not self.JWT_SECRET_KEY
        ):
            logger.warning(
                'Using default JWT secret key in non-development environment.'
            )
            raise ValueError(
                'JWT_SECRET_KEY must be set in production environment'
            )
        return self

    @property
    def DATABASE_URL(self) -> str:
        return f'postgresql+psycopg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_ADDRESS}:{self.DB_PORT}/{self.DB_DATABASE}'


settings = Settings()
