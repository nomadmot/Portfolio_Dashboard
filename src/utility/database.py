"""Database configuration module."""

# import 3rd-party libraries
import duckdb

# import local libraries
from config import SETTINGS
from utility import get_logger

# mark entry into the module
_logger = get_logger(__name__)
_logger.debug("In module %s", __name__)

def _database_engine():
    """
    Returns the DuckDB connection object for the application.
    This replaces the SQLAlchemy engine for direct, high-speed analytical access.
    """
    database_uri = SETTINGS.database_uri

    # 1. Validation Check
    if not database_uri:
        raise ValueError("DATABASE_URI not found in settings")

    # 2. Path Logging
    # DuckDB typically uses the file path directly.
    database_filename = database_uri.rsplit("://",maxsplit=1)[-1]
    _logger.info("Using database file: %s", database_filename)

    # 3. Connection and Engine Creation
    try:
        # This connection object will be used to execute raw SQL queries.
        con = duckdb.connect(database_uri)
        _logger.info("Successfully connected to DuckDB database.")
        return con
    except Exception as e:
        _logger.error("Failed to connect to DuckDB:", exc_info=True)
        raise RuntimeError(f"Failed to initialize the DuckDB connection: {e}") from e

# create the database connection instance
DATABASE_CONNECTION = _database_engine()
