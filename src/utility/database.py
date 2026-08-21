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
    Initializes the DuckDB connection to the catalog database.
    """

    if not SETTINGS.database_catalog:
        raise ValueError("DATABASE_CATALOG must be configured.")

    try:
        con = duckdb.connect(SETTINGS.database_catalog)
        _logger.info("Successfully connected to the DuckDB catalog at %s",
                     SETTINGS.database_catalog)
        return con
    except Exception as e:
        _logger.error("Failed to connect to the DuckDB catalog:", exc_info=True)
        raise RuntimeError(f"Failed to initialize the DuckDB catalog: {e}") from e

# create the database connection instance
DATABASE_CONNECTION = _database_engine()
