"""Настройки"""

import os

from pydantic import BaseSettings


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV_DIR = os.path.join(BASE_DIR, "..", "..")


class TokenSettings(BaseSettings):
    algo: str
    access_lifetime: int
    refresh_lifetime: int


class SuperUserSettings(BaseSettings):
    username: str
    password: str
    email: str


class ElasticIndexes(BaseSettings):
    genre: str
    person: str
    filmwork: str


class PostgresSettings(BaseSettings):
    host: str
    port: int
    dbname: str
    user: str
    password: str


class RedisSettings(BaseSettings):
    host: str
    port: int


class JaegerSettings(BaseSettings):
    host: str
    port: int


class OAuthProviderSettings(BaseSettings):
    authorization_url: str
    token_url: str
    credentials_url: str
    client_id: str
    client_secret: str
    scope: str


class OAuthSettings(BaseSettings):
    yandex: OAuthProviderSettings
    google: OAuthProviderSettings


class Settings(BaseSettings):
    url: str
    secret_key: str
    page_size: int
    token: TokenSettings
    enable_tracer: bool
    superuser: SuperUserSettings

    postgres: PostgresSettings
    redis: RedisSettings
    jaeger: JaegerSettings
    oauth: OAuthSettings

    class Config:
        #  Для локальной разработки вне docker
        env_file = (
            os.path.join(ENV_DIR, ".env.prod"),
            os.path.join(ENV_DIR, ".env.dev"),
        )
        env_nested_delimiter = "__"


settings = Settings()
