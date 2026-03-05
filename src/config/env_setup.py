"""
Configuration settings for the application.
"""
# import standard libraries
import logging
import sys
from enum import Enum
from typing import Type, Tuple, ClassVar
from pathlib import Path

# import 3rd-party libraries
from streamlit import logger as litlog
import yfinance as yf
from pydantic_settings import (
                               BaseSettings,
                               SettingsConfigDict,
                               YamlConfigSettingsSource,
                               PydanticBaseSettingsSource
                              )

# import local libraries
from .app_settings import AppDefaults

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

# class EnvSettings(BaseSettings):
#     """
#     Use Pydantic BaseSettings to define application environment
#     """
#     #from .app_settings import PageDefaults
#     model_config = SettingsConfigDict(
#         env_file='.settings/.env', env_file_encoding='utf-8',
#         )
#     loglevel_application: LogLevelEnum = LogLevelEnum.INFO
#     loglevel_streamlit: LogLevelEnum = LogLevelEnum.WARN
#     loglevel_sqlalchemy: LogLevelEnum = LogLevelEnum.WARN
#     yfinance_debug: bool = False
#     database_uri: str = "sqlite://///path/to/your/database.db"
#     duck_database: str = "path/to/your/duckdb"
# ENVIRONMENT = EnvSettings()

# Initialize logging
logging.basicConfig(
    #level=LOGLEVEL_APPLICATION,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stdout)
logger = logging.getLogger(__name__)
logger.setLevel(ENVIRONMENT.loglevel_application.to_logging_level())
logger.info(
    "Application logger initialized at level: %s",
    ENVIRONMENT.loglevel_application.value
    )

# set the sqlalchemy logging level
sqlalchemy_logger = logging.getLogger("sqlalchemy.engine")
sqlalchemy_logger.setLevel(ENVIRONMENT.loglevel_sqlalchemy.to_logging_level())
logger.info(
    "SQLAlchemy logger initialized at level: %s",
    ENVIRONMENT.loglevel_sqlalchemy.value
    )

# set the Streamlit logging level
litlog.set_log_level(ENVIRONMENT.loglevel_streamlit.to_logging_level())
logger.info(
    "Streamlit logger initialized at level: %s",
    ENVIRONMENT.loglevel_streamlit.value
    )

# YFinance logging configuration
logger.info("YFinance debug mode is %s", ENVIRONMENT.yfinance_debug)
yf.config.debug.logging = ENVIRONMENT.yfinance_debug
