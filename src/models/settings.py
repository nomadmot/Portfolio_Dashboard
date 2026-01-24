"""
Configuration settings for the application.
"""
# import standard libraries
import logging
import sys
from os import environ, path

#import 3rd-party libraries
from pydantic_settings import BaseSettings
from sqlalchemy import create_engine
from streamlit import logger as litlog
import yfinance as yf

class Settings(BaseSettings):
    loglevel_application: str = "XXX"
    loglevel_streamlit: str = "XXX"
    loglevel_sqlalchemy: str = "XXX"
    yfinance_debug: bool = False
    database_uri: str = "XXX"

print(Settings().model_dump())

# get logging configuration from the environment
LogLevelApplication = environ.get("LOGLEVEL_APPLICATION", "INFO")
match(LogLevelApplication.upper()):
    case "DEBUG":
        LogLevelApplication = logging.DEBUG
    case "INFO":
        LogLevelApplication = logging.INFO
    case "WARN":
        LogLevelApplication = logging.WARN
    case "ERROR":
        LogLevelApplication = logging.ERROR
    case _:
        LogLevelApplication = logging.INFO

LogLevelStreamlit = environ.get("LOGLEVEL_STREAMLIT", "INFO")
match(LogLevelStreamlit.upper()):
    case "DEBUG":
        LogLevelStreamlit = logging.DEBUG
    case "INFO":
        LogLevelStreamlit = logging.INFO
    case "WARN":
        LogLevelStreamlit = logging.WARN
    case "ERROR":
        LogLevelStreamlit = logging.ERROR
    case _:
        LogLevelStreamlit = logging.INFO

LogLevelSQLAlchemy = environ.get("LOGLEVEL_SQLALCHEMY", "WARN")
match(LogLevelSQLAlchemy.upper()):
    case "DEBUG":
        LogLevelSQLAlchemy = logging.DEBUG
    case "INFO":
        LogLevelSQLAlchemy = logging.INFO
    case "WARN":
        LogLevelSQLAlchemy = logging.WARN
    case "ERROR":
        LogLevelSQLAlchemy = logging.ERROR
    case _:
        LogLevelSQLAlchemy = logging.WARN

# Initialize logging
logging.basicConfig(
    #level=LOGLEVEL_APPLICATION,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stdout)
logger = logging.getLogger(__name__)
logger.setLevel(LogLevelApplication)
logger.info(
    "Application logger initialized at level: %s",
    logging.getLevelName(LogLevelApplication)
    )

# set the sqlalchemy logging level
sqlalchemy_logger = logging.getLogger("sqlalchemy.engine")
sqlalchemy_logger.setLevel(LogLevelSQLAlchemy)
logger.info("SQLAlchemy logger initialized at level: %s", logging.getLevelName(LogLevelSQLAlchemy))

# set the Streamlit logging level
litlog.set_log_level(LogLevelStreamlit)
logger.info("Streamlit logger initialized at level: %s", logging.getLevelName(LogLevelStreamlit))

# YFinance logging configuration
YFinanceDebug = environ.get("YFINANCE_DEBUG", "FALSE").upper()
if YFinanceDebug == "TRUE":
    logger.info("Enabling YFinance debug mode")
    yf.enable_debug_mode()

# database configuration
#DATABASE_URI = \
#"sqlite://///Users/nomadmot/Library/CloudStorage/Dropbox/Apps/Investing/DATA/portfolio-test.db"
# DATABASE_URI = \
# "sqlite://///home/devuser/investorlab/DATA/portfolio-test.db"
DatabaseURI = environ.get("DATABASE_URI", None)

# test to be sure the DATABASE_URI is valid
if  DatabaseURI:
    logger.info("Using database URI: %s", DatabaseURI)
else:
    raise ValueError("DATABASE_URI not found in environment variables")
DatabaseFilename = DatabaseURI.split("////")[1]
logger.info("Using database file: %s", DatabaseFilename)
assert path.isfile(DatabaseFilename), f"Database file {DatabaseFilename} does not exist."

# create the SQLAlchemy engine
DatabaseEngine = create_engine(DatabaseURI, echo=False)
