"""Database configuration module."""
# import 3rd-party libraries
import duckdb

# import local libraries
from config import SETTINGS
from . import get_logger

# initialize loggr
_logger = get_logger(__name__)
_logger.debug("In module %s", __name__)

def _database_engine():
    """
    Initializes the DuckDB connection to the database file.
    """

    if not SETTINGS.database_file:
        raise ValueError("DATABASE_FILE must be configured.")

    try:
        con = duckdb.connect(SETTINGS.database_file)
        _logger.info("Successfully connected to the DuckDB file at %s",
                     SETTINGS.database_file)
        return con
    except Exception as e:
        _logger.error("Failed to connect to the DuckDB file:", exc_info=True)
        raise RuntimeError(f"Failed to initialize the DuckDB file: {e}") from e

# create the database connection instance
DATABASE_CONNECTION = _database_engine()
