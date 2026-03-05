"""
configuration module for the Portfolio Dashboard project
"""
# package-level exports
from config.settings import (
    ENVIRONMENT,
)
from config.database import DATABASE_ENGINE

__all__= [
    "ENVIRONMENT",
    "DATABASE_ENGINE",
]
