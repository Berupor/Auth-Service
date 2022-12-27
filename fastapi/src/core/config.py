"""Настройки"""

import os
from logging import config as logging_config

from pydantic import BaseModel, BaseSettings

from src.core.logger import LOGGING


logging_config.dictConfig(LOGGING)


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV_DIR = os.path.join(BASE_DIR, "..", "..")


class FlaskSettings(BaseModel):
    host: str
    port: int


class JaegerSettings(BaseModel):
    host: str
    port: int


class Settings(BaseSettings):
    project_name: str
    enable_tracer: bool

    flask: FlaskSettings
    jaeger: FlaskSettings

    class Config:
        #  Для локальной разработки вне docker
        env_file = (
            os.path.join(ENV_DIR, ".env.prod"),
            os.path.join(ENV_DIR, ".env.dev"),
        )
        env_nested_delimiter = "__"


settings = Settings()
