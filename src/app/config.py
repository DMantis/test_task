from functools import lru_cache

from pydantic import BaseSettings, PostgresDsn


class Config(BaseSettings):
    DB_DSN: PostgresDsn
    LOG_LEVEL: str = "info"
    HTTP_SERVER_PORT: int = 8080
    JWT_SECRET: str


@lru_cache()
def get_config():
    return Config()

