from typing import ClassVar, Self

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config: ClassVar[SettingsConfigDict] = SettingsConfigDict(
        env_file='.env', env_file_encoding='utf-8', case_sensitive=False, extra='ignore'
    )

    host: str = '0.0.0.0'
    port: int = 8000

    mongo_uri: str = ''
    mongo_db_name: str = ''

    @model_validator(mode='after')
    def validate_required_fields(self) -> Self:
        if not self.mongo_uri:
            raise ValueError('MONGO_URI is required in the .env file.')
        if not self.mongo_db_name:
            raise ValueError('MONGO_DB_NAME is required in the .env file.')
        return self


settings: Settings = Settings()
