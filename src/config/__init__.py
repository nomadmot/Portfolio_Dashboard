"""
configuration module for the Portfolio Dashboard project
"""
# package-level exports
from config.app_settings import SETTINGS
from config.env_setup import ENVIRONMENT
from config.database import DATABASE_ENGINE

__all__= [
    "ENVIRONMENT",
    "DATABASE_ENGINE",
    "SETTINGS"
]
