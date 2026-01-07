"""
Configuration settings for the application.
"""
# import standard libraries
import logging
import sys
from os import environ, path

#import 3rd-party libraries
from sqlalchemy import create_engine
import yfinance as yf

# get logging configuration from the environment
LOGLEVEL_APPLICATION = environ.get("LOGLEVEL_APPLICATION", "INFO")
match(LOGLEVEL_APPLICATION.upper()):
    case "DEBUG":
        LOGLEVEL_APPLICATION = logging.DEBUG
    case "INFO":
        LOGLEVEL_APPLICATION = logging.INFO
    case "WARN":
        LOGLEVEL_APPLICATION = logging.WARN
    case "ERROR":
        LOGLEVEL_APPLICATION = logging.ERROR
    case _:
        LOGLEVEL_APPLICATION = logging.INFO

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
logging.basicConfig(
    #level=LOGLEVEL_APPLICATION,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stdout)
logger = logging.getLogger(__name__)
logger.setLevel(LOGLEVEL_APPLICATION)
logger.info(
    "Application logger initialized at level: %s",
    logging.getLevelName(LOGLEVEL_APPLICATION)
    )

# set the sqlalchemy logging level
sqlalchemy_logger = logging.getLogger("sqlalchemy.engine")
sqlalchemy_logger.setLevel(LOGLEVEL_SQLALCHEMY)
logger.info("SQLAlchemy logger initialized at level: %s", logging.getLevelName(LOGLEVEL_SQLALCHEMY))

#YFinance configuration
YFINANCE_DEBUG = environ.get("YFINANCE_DEBUG", "FALSE").upper()
if YFINANCE_DEBUG == "TRUE":
    logger.info("Enabling YFinance debug mode")
    yf.enable_debug_mode()

# database configuration
#DATABASE_URI = \
#"sqlite://///Users/nomadmot/Library/CloudStorage/Dropbox/Apps/Investing/DATA/portfolio-test.db"
# DATABASE_URI = \
# "sqlite://///home/devuser/investorlab/DATA/portfolio-test.db"
DATABASE_URI = environ.get("DATABASE_URI", None)

# test to be sure the DATABASE_URI is valid
if  DATABASE_URI:
    logger.info("Using database URI: %s", DATABASE_URI)
else:
    raise ValueError("DATABASE_URI not found in environment variables")
DATABASE_FILENAME = DATABASE_URI.split("////")[1]
logger.info("Using database file: %s", DATABASE_FILENAME)
assert path.isfile(DATABASE_FILENAME), f"Database file {DATABASE_FILENAME} does not exist."

# create the SQLAlchemy engine
DB_ENGINE = create_engine(DATABASE_URI, echo=False)
