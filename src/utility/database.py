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
    Initializes the DuckLake connection. This function handles:
    1. Connecting to the Catalog Database (metadata).
    2. Attaching the Data Lake path (Parquet files).
    """

    # build the paths
    catalog_uri = SETTINGS.database_uri
    duck_puddle_path = SETTINGS.duck_puddle

    if not catalog_uri or not duck_puddle_path:
        raise ValueError("Both DATABASE_URI (Catalog) and ",
                         "DUCK_PUDDLE (Data Lake Path) must be configured.")

    # connect to the Catalog Database
    # try:
        # Connect to the catalog database first. This DB holds the metadata.
    #     con = duckdb.connect(catalog_uri)
    #     _logger.info("Successfully connected to the DuckLake Catalog Database.")
    # except Exception as e:
    #     _logger.error("Failed to connect to the DuckLake Catalog:", exc_info=True)
    #     raise RuntimeError(f"Failed to initialize the DuckLake Catalog: {e}") from e

    # attach the Data Lake
    _logger.info("Attaching ducklake %s with data %s", catalog_uri, duck_puddle_path)
    try:
        # This command tells DuckDB where the raw data resides.
        # We attach the data lake path as a virtual table source.
        sql_attach = f"""
                    LOAD ducklake;
                    ATTACH '{catalog_uri}'
                    AS duck_puddle (DATA_PATH '{duck_puddle_path}', OVERRIDE_DATA_PATH true);
                    USE duck_puddle;
                    """
        con = duckdb.execute(sql_attach)
        _logger.info("Successfully attached the Data Lake at path: %s", duck_puddle_path)

        return con
    except duckdb.Error as e:
        _logger.error("Failed to attach the Data Lake:", exc_info=True)
        # If attaching the data lake fails, we must raise an error.
        raise RuntimeError(f"Failed to initialize the Data Lake connection: {e}") from e

# create the database connection instance
DATABASE_CONNECTION = _database_engine()
