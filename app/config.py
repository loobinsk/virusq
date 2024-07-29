from typing import Type

from pydantic import BaseModel, HttpUrl
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
    TomlConfigSettingsSource,
)


class App(BaseModel):
    telegram_bot_token: str
    jwt_secret: str
    bot_jwt_secret: str
    db_encryption_secret_key: str
    game_checksum_secret_key: str


class Postgres(BaseModel):
    dsn: str


class Redis(BaseModel):
    dsn: str


class Logging(BaseModel):
    level: str
    sentry_dsn: HttpUrl


class Config(BaseSettings):
    postgres: Postgres
    redis: Redis
    logging: Logging
    app: App

    model_config = SettingsConfigDict(toml_file="config.toml")

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: Type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        return (TomlConfigSettingsSource(settings_cls),)

    @property
    def is_dev_mode(self) -> bool:
        return self.logging.level == "DEBUG"


config = Config()  # type: ignore
