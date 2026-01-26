"""Database configuration module."""
# import standard libraries
import logging
from os import path
# import 3rd-party libraries
from sqlalchemy import create_engine
# import local libraries
from config import SETTINGS

# Initialize logging
logger = logging.getLogger(__name__)
logger.setLevel(SETTINGS.loglevel_application.to_logging_level())
# mark entry into the module
logger.debug("Entering module %s", __name__)

def _database_engine():
    """
    Returns the SQLAlchemy database engine for the application.
    """
    database_uri = SETTINGS.database_uri

    # test to be sure the DATABASE_URI is valid
    if  database_uri:
        logger.info("Using database URI: %s", database_uri)
    else:
        raise ValueError("DATABASE_URI not found in environment variables")
    database_filename = database_uri.split("////")[1]
    logger.info("Using database file: %s", database_filename)
    assert path.isfile(database_filename), f"Database file {database_filename} does not exist."

    # create the SQLAlchemy engine
    return create_engine(database_uri, echo=False)

# create the database engine instance
DATABASE_ENGINE = _database_engine()
