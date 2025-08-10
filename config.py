"""
Configuration settings for the application.
"""
from sqlalchemy import create_engine

DATABASE_URI = "sqlite://///Users/nomadmot/Library/CloudStorage/Dropbox/Apps/Investing/DATA/portfolio-test.db"
DB_ENGINE = create_engine(DATABASE_URI, echo=True)
