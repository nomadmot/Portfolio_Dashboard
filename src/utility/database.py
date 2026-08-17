"""Database configuration module."""
# import 3rd-party libraries
import duckdb

# import local libraries
from config import SETTINGS
from . import get_logger

# initialize loggr
_logger = get_logger(__name__)
_logger.debug("In module %s", __name__)

def _data_path():
    # get the data path from the catalog
    try:
        #Connect to the catalog database first. This DB holds the metadata.
        con = duckdb.connect(SETTINGS.database_catalog)
        _logger.info("Successfully connected to the Duck Puddle Catalog Database at %s",
                     SETTINGS.database_catalog)
    except Exception as e:
        _logger.error("Failed to connect to the Duck Puddle Catalog:", exc_info=True)
        raise RuntimeError(f"Failed to initialize the Duck Puddle Catalog: {e}") from e

    # the data path is the value of key 'data_path' in the ducklake_metadata table
    sql_get_datapath = "SELECT value FROM ducklake_metadata where key = 'data_path';"
    duck_puddle_path = con.execute(sql_get_datapath).fetchone()
    if duck_puddle_path:
        duck_puddle_path = duck_puddle_path[0]
    _logger.info("Duck Puddle data path is %s", duck_puddle_path)
    con.close()

    # return the data path
    return duck_puddle_path

def _database_engine():
    """
    Initializes the DuckLake connection. This function handles:
    1. Connecting to the Catalog Database (metadata).
    2. Attaching the Data Lake path (Parquet files).
    """

    # build the ducklake URI
    if not SETTINGS.database_catalog:
        raise ValueError("DATABASE_CATALOG must be configured.")
    catalog_uri = f"ducklake:{SETTINGS.database_catalog}"

    # attach the Data Lake
    _logger.info("Attaching duck_puddle %s", catalog_uri)
    try:
        # This command tells DuckDB where the raw data resides.
        # We attach the data lake path as a virtual table source.
        sql_attach = f"""
                    LOAD ducklake;
                    ATTACH '{catalog_uri}'
                    AS duck_puddle;
                    USE duck_puddle;
                    """
        con = duckdb.execute(sql_attach)
        _logger.info("Successfully attached the Duck Puddle at path: %s", catalog_uri)

        return con
    except duckdb.Error as e:
        _logger.error("Failed to attach the Data Lake:", exc_info=True)
        # If attaching the data lake fails, we must raise an error.
        raise RuntimeError(f"Failed to initialize the Data Lake connection: {e}") from e

# create the database connection instance
DUCKDB_DATA_PATH = _data_path()
DATABASE_CONNECTION = _database_engine()
