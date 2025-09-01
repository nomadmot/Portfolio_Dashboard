"""
Configuration settings for the application.
"""
import logging
from sqlalchemy import create_engine

# logging configuration
LOGLEVEL_STREAMLIT = logging.DEBUG
LOGLEVEL_SQLALCHEMY = logging.WARN

# database configuration
DATABASE_URI = \
    "sqlite://///Users/nomadmot/Library/CloudStorage/Dropbox/Apps/Investing/DATA/portfolio-test.db"
DB_ENGINE = create_engine(DATABASE_URI, echo=False)
