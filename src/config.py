"""
Configuration settings for the application.
"""
# import standard libraries
import logging
from os import environ, path

#import 3rd-party libraries
import streamlit as st
#import streamlit.logger
from sqlalchemy import create_engine
import yfinance as yf

# get logging configuration from the environment
LOGLEVEL_STREAMLIT = environ.get("LOGLEVEL_STREAMLIT", "INFO")
match(LOGLEVEL_STREAMLIT.upper()):
    case "DEBUG":
        LOGLEVEL_STREAMLIT = logging.DEBUG
    case "INFO":
        LOGLEVEL_STREAMLIT = logging.INFO
    case "WARN":
        LOGLEVEL_STREAMLIT = logging.WARN
    case "ERROR":
        LOGLEVEL_STREAMLIT = logging.ERROR
    case _:
        LOGLEVEL_STREAMLIT = logging.INFO

LOGLEVEL_SQLALCHEMY = environ.get("LOGLEVEL_SQLALCHEMY", "WARN")
match(LOGLEVEL_SQLALCHEMY.upper()):
    case "DEBUG":
        LOGLEVEL_SQLALCHEMY = logging.DEBUG
    case "INFO":
        LOGLEVEL_SQLALCHEMY = logging.INFO
    case "WARN":
        LOGLEVEL_SQLALCHEMY = logging.WARN
    case "ERROR":
        LOGLEVEL_SQLALCHEMY = logging.ERROR
    case _:
        LOGLEVEL_SQLALCHEMY = logging.WARN

# Initialize logging
LOGGER = logging.getLogger(st.__name__)
LOGGER.setLevel(LOGLEVEL_STREAMLIT)
# Create a StreamHandler and attach it to the logger
stream_handler = logging.StreamHandler()
LOGGER.addHandler(stream_handler)
LOGGER.info("Streamlit logger initialized at level: %s", logging.getLevelName(LOGLEVEL_STREAMLIT))

#YFinance configuration
YFINANCE_DEBUG = environ.get("YFINANCE_DEBUG", "FALSE").upper()
if YFINANCE_DEBUG == "TRUE":
    LOGGER.info("Enabling YFinance debug mode")
    yf.enable_debug_mode()

# database configuration
#DATABASE_URI = \
#"sqlite://///Users/nomadmot/Library/CloudStorage/Dropbox/Apps/Investing/DATA/portfolio-test.db"
# DATABASE_URI = \
# "sqlite://///home/devuser/investorlab/DATA/portfolio-test.db"
DATABASE_URI = environ["DATABASE_URI"]
LOGGER.info("Using database URI: %s", DATABASE_URI)

# test to be sure the DATABASE_URI is valid
if not DATABASE_URI:
    raise ValueError("DATABASE_URI not found in environment variables")
DATABASE_FILENAME = DATABASE_URI.split("////")[1]
LOGGER.info("Using database file: %s", DATABASE_FILENAME)
assert path.isfile(DATABASE_FILENAME), f"Database file {DATABASE_FILENAME} does not exist."

# create the SQLAlchemy engine
DB_ENGINE = create_engine(DATABASE_URI, echo=False)

# the key for the detail performance multiselect component
SYMBOL_MULTISELECT_KEY = "detail_performance_selected_symbols"
