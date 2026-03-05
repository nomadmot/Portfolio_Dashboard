"""
Initialize logging for the application.
"""
# import standard libraries
import logging
import sys

# import 3rd-party libraries
from streamlit import logger as litlog
import yfinance as yf

# import local libraries
from config import ENVIRONMENT

def get_logger(name: str) -> logging.Logger:
    """
    get a pre-configured logger with the specified name

    Arguments:
        name -- The name to use for the logger

    Returns:
        A pre-configured logger using the input name
    """
    # create a pre-configured logger
    ret_logger = logging.getLogger(name)
    ret_logger.setLevel(ENVIRONMENT.loglevel_application.to_logging_level())

    # return the pre-configured logger
    return ret_logger

# mark entry into the module
logger = get_logger(__name__)
logger.debug("Initialize logging")

# Initialize logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stdout)
logger.info(
    "Application logger initialized at level: %s",
    ENVIRONMENT.loglevel_application.value
    )

# set the sqlalchemy logging level
sqlalchemy_logger = logging.getLogger("sqlalchemy.engine")
sqlalchemy_logger.setLevel(ENVIRONMENT.loglevel_sqlalchemy.to_logging_level())
logger.info(
    "SQLAlchemy logger initialized at level: %s",
    ENVIRONMENT.loglevel_sqlalchemy.value
    )

# set the Streamlit logging level
litlog.set_log_level(ENVIRONMENT.loglevel_streamlit.to_logging_level())
logger.info(
    "Streamlit logger initialized at level: %s",
    ENVIRONMENT.loglevel_streamlit.value
    )

# YFinance logging configuration
logger.info("YFinance debug mode is %s", ENVIRONMENT.yfinance_debug)
yf.config.debug.logging = ENVIRONMENT.yfinance_debug
