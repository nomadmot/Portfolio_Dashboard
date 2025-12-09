"""
Configuration settings for the application.
"""
# import standard libraries
import logging
from os import environ

#import 3rd-party libraries
import streamlit as st
import streamlit.logger
from sqlalchemy import create_engine
import yfinance as yf

# logging configuration
LOGLEVEL_STREAMLIT = logging.INFO
LOGLEVEL_SQLALCHEMY = logging.WARN

# Initialize logging
logger = streamlit.logger.get_logger(st.__name__)
logger.setLevel(LOGLEVEL_STREAMLIT)

#YFinance configuration
YFINANCE_DEBUG = False
if YFINANCE_DEBUG:
    logger.info("Enabling YFinance debug mode")
    yf.enable_debug_mode()

# database configuration
# DATABASE_URI = \
#     "sqlite://///Users/nomadmot/Library/CloudStorage/Dropbox/Apps/Investing/DATA/portfolio-test.db"
DATABASE_URI = environ["DATABASE_URI"]
if not DATABASE_URI:
    raise ValueError("DATABASE_URI not found in environment variables")
logger.info("Using database URI: %s", DATABASE_URI)

DB_ENGINE = create_engine(DATABASE_URI, echo=False)
