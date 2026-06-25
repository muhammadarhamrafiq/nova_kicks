from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')

    HOST: str = '0.0.0.0'
    PORT: int = 2000


settings = Settings()
