"""
Configuration settings for the application.
"""
# logging configuration
import logging
LOGLEVEL_STREAMLIT = logging.WARN
LOGLEVEL_SQLALCHEMY = logging.WARN

# database configuration
from sqlalchemy import create_engine
DATABASE_URI = "sqlite://///var/investorlab/DATA/portfolio.db"
DB_ENGINE = create_engine(DATABASE_URI, echo=False)
