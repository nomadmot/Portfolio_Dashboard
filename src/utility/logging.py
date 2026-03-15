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
from config import SETTINGS

def get_logger(name: str) -> logging.Logger:
    """
    Get a pre-configured logger with the specified name. The loglevel will be initialized
    to DEBUG for any modules listed in SETTINGS.debug, or the default selected in
    SETTING.loglevel_application

    Arguments:
        name -- The name to use for the logger

    Returns:
        A pre-configured logger using the input name and specified loglevel
    """
    # create a pre-configured logger
    ret_logger = logging.getLogger(name)
    if name in SETTINGS.debug:
        logger.info("Set logging for module %s to DEBUG", name)
        ret_logger.setLevel(logging.DEBUG)
    else:
        ret_logger.setLevel(SETTINGS.loglevel_application.to_logging_level())

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
    SETTINGS.loglevel_application.value
    )

# set the sqlalchemy logging level
logger.info(
    "SQLAlchemy logger initialized at level: %s",
    SETTINGS.loglevel_sqlalchemy.value
    )
logging.getLogger("sqlalchemy.engine").setLevel(SETTINGS.loglevel_sqlalchemy.to_logging_level())
logging.getLogger("sqlalchemy.pool").setLevel(SETTINGS.loglevel_sqlalchemy.to_logging_level())
logging.getLogger("sqlalchemy.dialects").setLevel(SETTINGS.loglevel_sqlalchemy.to_logging_level())
logging.getLogger("sqlalchemy.orm").setLevel(SETTINGS.loglevel_sqlalchemy.to_logging_level())

# set the Streamlit logging level
litlog.set_log_level(SETTINGS.loglevel_streamlit.to_logging_level())
logger.info(
    "Streamlit logger initialized at level: %s",
    SETTINGS.loglevel_streamlit.value
    )

# YFinance logging configuration
logger.info("YFinance debug mode is %s", SETTINGS.yfinance_debug)
yf.config.debug.logging = SETTINGS.yfinance_debug
