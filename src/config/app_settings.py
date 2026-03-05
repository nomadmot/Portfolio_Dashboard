"""
Configuration settings for the application.
"""
# import standard libraries
from typing import Type, Tuple, ClassVar
from pathlib import Path

# import 3rd-party libraries
from pydantic import BaseModel
from pydantic_settings import (
                               BaseSettings,
                               SettingsConfigDict,
                               YamlConfigSettingsSource,
                               PydanticBaseSettingsSource
                              )

# import local libraries
#from core import Periods

class AppDefaults(BaseModel):
    perf_sum_default_period: str
    perf_sum_default_symbol: str

class AppSettings(BaseSettings):
    """
    Use Pydantic BaseSettings to define application settings
    """
    defaults: AppDefaults

    model_config: ClassVar[SettingsConfigDict] = SettingsConfigDict(
                                      yaml_file=Path(".settings/app_config.yml"),
                                      yaml_file_encoding="utf-8",
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

SETTINGS = AppSettings() # pyright: ignore[reportCallIssue]

if __name__  == "__main__":
    print(SETTINGS.model_dump())
