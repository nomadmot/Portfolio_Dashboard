"""
Configuration settings for the application.
"""
# logging configuration
LOGLEVEL_STREAMLIT = "debug"
LOGLEVEL_SQLALCHEMY = "error"

# database configuration
from sqlalchemy import create_engine
DATABASE_URI = "sqlite://///Users/nomadmot/Library/CloudStorage/Dropbox/Apps/Investing/DATA/portfolio-test.db"
DB_ENGINE = create_engine(DATABASE_URI, echo=False)
