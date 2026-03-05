"""
configuration module for the Portfolio Dashboard project
"""
# package-level exports
from config.settings import (
    SETTINGS,
)
from config.database import DATABASE_ENGINE

__all__= [
    "SETTINGS",
    "DATABASE_ENGINE",
]
