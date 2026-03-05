"""Database configuration module."""
# import standard libraries
from os import path

# import 3rd-party libraries
from sqlalchemy import create_engine

# import local libraries
# from utility import get_logger
from config import ENVIRONMENT

# # mark entry into the module
# logger = get_logger(__name__)
# logger.debug("In module %s", __name__)

def _database_engine():
    """
    Returns the SQLAlchemy database engine for the application.
    """
    database_uri = ENVIRONMENT.database_uri

    # test to be sure the DATABASE_URI is valid
    if  database_uri:
        pass
        #logger.info("Using database URI: %s", database_uri)
    else:
        raise ValueError("DATABASE_URI not found in settings")
    database_filename = database_uri.split("////")[1]
    #logger.info("Using database file: %s", database_filename)
    assert path.isfile(database_filename), f"Database file {database_filename} does not exist."

    # create the SQLAlchemy engine
    return create_engine(database_uri, echo=False)

# create the database engine instance
DATABASE_ENGINE = _database_engine()
