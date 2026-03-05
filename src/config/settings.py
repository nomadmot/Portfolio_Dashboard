"""
Configuration settings for the application.
"""
# import standard libraries
from typing import Type, Tuple, ClassVar
from enum import Enum
from pathlib import Path
import logging

# import 3rd-party libraries
from pydantic import BaseModel
from pydantic_settings import (
                               BaseSettings,
                               SettingsConfigDict,
                               YamlConfigSettingsSource,
                               PydanticBaseSettingsSource
                              )

# import local libraries

class LogLevelEnum(str, Enum):
    """
    define an enumeration for standard logging levels
    """
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARN = "WARN"
    ERROR = "ERROR"


    def to_logging_level(self) -> int:
        """
        convert the LogLevelEnum to a logging module level
        """
        map_loglevel = {
            "DEBUG": logging.DEBUG,
            "INFO": logging.INFO,
            "WARN": logging.WARN,
            "ERROR": logging.ERROR
        }
        return map_loglevel[self.value]

class AppDefaults(BaseModel):
    """
    Model for application default settings
    """
    # The default Period for the Performance Summary page
    performance_summary_period: str
    # The default comparison symbol for the Performance Summary page
    performance_summary_symbol: str

class Settings(BaseSettings):
    """
    Use Pydantic BaseSettings to define application settings
    """
    loglevel_application: LogLevelEnum = LogLevelEnum.INFO
    loglevel_streamlit: LogLevelEnum = LogLevelEnum.WARN
    loglevel_sqlalchemy: LogLevelEnum = LogLevelEnum.WARN
    yfinance_debug: bool = False
    database_uri: str = "sqlite://///path/to/your/database.db"
    duck_database: str = "path/to/your/duckdb"

    defaults: AppDefaults

    model_config: ClassVar[SettingsConfigDict] = SettingsConfigDict(
                                      yaml_file=Path(".settings/app_config.yml"),
                                      yaml_file_encoding="utf-8",
                                      env_file='.settings/.env',
                                      env_file_encoding='utf-8',
                                      extra="ignore",
                                      )

    @classmethod
    def settings_customise_sources(
        cls: Type[BaseSettings],
        settings_cls: Type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> Tuple[PydanticBaseSettingsSource, ...]:
        yaml_source = YamlConfigSettingsSource(settings_cls)
        return (
            init_settings, # Values passed to the constructor
            yaml_source,   # Values from config.yaml
            dotenv_settings, # Values from .env
            env_settings,  # Values from environment variables
            file_secret_settings, # Values from secret files
        )

ENVIRONMENT = Settings() # pyright: ignore[reportCallIssue]

if __name__  == "__main__":
    print(ENVIRONMENT.model_dump())
