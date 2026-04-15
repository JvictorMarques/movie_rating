from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='.env', env_file_encoding='utf-8'
    )

    DB_USER: str
    DB_PASSWORD: str
    DB_DATABASE: str
    DB_ADRESS: str
    DB_PORT: int

    @property
    def DATABASE_URL(self) -> str:
        return f'postgresql+psycopg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_ADRESS}:{self.DB_PORT}/{self.DB_DATABASE}'
