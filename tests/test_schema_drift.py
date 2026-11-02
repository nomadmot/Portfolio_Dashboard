"""
Drift test: assert the polars dtypes returned by the core query functions match
the column types the DuckDB database actually reports.

Because the query routines now derive their result schema from the live database,
the only remaining drift risk is a *change* to a column's type (for example,
re-running a DDL script that alters ``daily_balances.balance`` from ``DOUBLE`` to
``DECIMAL``). Such a change would otherwise flow silently into the performance
math. This test pins the mapping by comparing each function's returned dtypes
against ``information_schema``.

The test reuses the application's own database connection (opened read-write)
so it exercises the exact connection the query functions use, and so it avoids
opening a second connection to the same file (which DuckDB forbids when the two
connections have different configurations).

The test is skipped when the configured database file is not present, so it
contributes real coverage on a machine with the database and is a no-op in a
bare checkout.
"""
# import standard libraries
from datetime import date
from pathlib import Path

# 3rd party
import polars as pl
import pytest


def _configured_database_file() -> str:
    """Return the configured database file path, or an empty string."""
    try:
        # importing config.settings is safe: it only reads settings, not the DB
        from config import SETTINGS
        return SETTINGS.database_file or ""
    except Exception:
        return ""


_DATABASE_FILE = _configured_database_file()


def _available() -> bool:
    """True when the configured database file exists on this machine."""
    return bool(_DATABASE_FILE) and Path(_DATABASE_FILE).exists()


# Skip the entire module when no database is present, so a bare checkout still
# runs the rest of the suite green.
pytestmark = pytest.mark.skipif(
    not _available(),
    reason="configured database file is not present on this machine",
)


def _information_schema_types() -> dict:
    """Map a DuckDB data-type keyword to its polars counterpart."""
    return {
        "INTEGER": pl.Int32,
        "BIGINT": pl.Int64,
        "SMALLINT": pl.Int16,
        "TINYINT": pl.Int8,
        "BOOLEAN": pl.Boolean,
        "DOUBLE": pl.Float64,
        "FLOAT": pl.Float32,
        "DECIMAL": pl.Float64,
        "REAL": pl.Float32,
        "VARCHAR": pl.String,
        "TEXT": pl.String,
        "DATE": pl.Date,
        "TIMESTAMP": pl.Datetime,
        "DATETIME": pl.Datetime,
        "BLOB": pl.Binary,
    }


def _table_dtypes(table: str) -> dict:
    """
    Return ``{column_name: polars dtype}`` for ``table`` by querying
    information_schema through the application's own database connection.
    """
    # The connection the query functions actually use. Importing ``utility``
    # opens it; using the same object (rather than a second one) avoids DuckDB's
    # "same file, different configuration" restriction.
    from utility import DATABASE_CONNECTION

    mapping = _information_schema_types()
    rows = DATABASE_CONNECTION.execute(
        "SELECT column_name, data_type FROM information_schema.columns "
        "WHERE table_name = ? ORDER BY ordinal_position",
        (table,),
    ).fetchall()

    dtypes = {}
    for column_name, data_type in rows:
        # DuckDB may report a parameterized type (e.g. DECIMAL(10, 2)); match on
        # the leading keyword.
        base = data_type.split("(")[0].strip().upper()
        dtypes[column_name] = mapping.get(base, pl.Object)
    return dtypes


def test_get_balance_history_dtypes_match_database():
    """The balance history frame's dtypes must match the daily_balances table."""
    from core import get_balance_history

    expected = _table_dtypes("daily_balances")

    frame = get_balance_history(
        account_id=1,
        begin_date=date(2000, 1, 1),
        end_date=date(2100, 1, 1),
        ascending=True,
    )

    assert "balance_date" in frame.columns
    assert "balance" in frame.columns
    assert frame.schema["balance_date"] == expected["balance_date"]
    assert frame.schema["balance"] == expected["balance"]


def test_get_cash_flows_dtypes_match_database():
    """The cash-flow frame's dtypes must match the trades table it aggregates."""
    from core import get_cash_flows

    trade_dtypes = _table_dtypes("trades")

    frame = get_cash_flows(
        account_id=1,
        begin_date=date(2000, 1, 1),
        end_date=date(2100, 1, 1),
        trade_types=["DEP", "WDL"],
    )

    assert "trade_date" in frame.columns
    assert "cash_flow" in frame.columns
    # cash_flow is a SUM of the trades price/quantity columns, so it is a
    # floating point type; pin it to Float64 regardless of the source type.
    assert frame.schema["trade_date"] == trade_dtypes["trade_date"]
    assert frame.schema["cash_flow"] == pl.Float64
