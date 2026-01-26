"""
Configuration settings for the application.
"""
# import standard libraries
#from numpy.f2py.crackfortran import f
from tkinter import SE
import logging
from enum import Enum
import sys
from os import environ, path

#import 3rd-party libraries
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import create_engine
from streamlit import logger as litlog
import yfinance as yf

class LogLevelEnum(str, Enum):
    """
    define an enumeration for standard logging levels
    """
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARN = "WARN"
    ERROR = "ERROR"


    def to_logging_level(self) -> int:
        """
        convert the LogLevelEnum to a logging module level
        """
        map_loglevel = {
            "DEBUG": logging.DEBUG,
            "INFO": logging.INFO,
            "WARN": logging.WARN,
            "ERROR": logging.ERROR
        }
        return map_loglevel[self.value]

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')
    loglevel_application: LogLevelEnum = LogLevelEnum.INFO
    loglevel_streamlit: LogLevelEnum = LogLevelEnum.WARN
    loglevel_sqlalchemy: LogLevelEnum = LogLevelEnum.WARN
    yfinance_debug: bool = False
    database_uri: str = "sqlite://///path/to/your/database.db"

SETTINGS = Settings()

# Initialize logging
logging.basicConfig(
    #level=LOGLEVEL_APPLICATION,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stdout)
logger = logging.getLogger(__name__)
logger.setLevel(SETTINGS.loglevel_application.to_logging_level())
logger.info(
    "Application logger initialized at level: %s",
    SETTINGS.loglevel_application.value
    )

# set the sqlalchemy logging level
sqlalchemy_logger = logging.getLogger("sqlalchemy.engine")
sqlalchemy_logger.setLevel(SETTINGS.loglevel_sqlalchemy.to_logging_level())
logger.info(
    "SQLAlchemy logger initialized at level: %s",
    SETTINGS.loglevel_sqlalchemy.value
    )

# set the Streamlit logging level
litlog.set_log_level(SETTINGS.loglevel_streamlit.to_logging_level())
logger.info(
    "Streamlit logger initialized at level: %s",
    SETTINGS.loglevel_streamlit.value
    )

# YFinance logging configuration
YFinanceDebug = SETTINGS.yfinance_debug
if SETTINGS.yfinance_debug:
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
