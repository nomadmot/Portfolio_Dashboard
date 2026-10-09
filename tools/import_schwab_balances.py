"""
Import a Schwab daily balances CSV (e.g. tools/data/Schwab_Balances.CSV)
into the daily_balances table of a DuckDB database
(default: tools/data/portfolio.db). The database must already exist;
create it with tools/initialize_database.py.
"""
import argparse
import csv
import re
import sys
from datetime import date
from decimal import Decimal
from pathlib import Path

import duckdb

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CSV = REPO_ROOT / "tools" / "data" / "Schwab_Balances.CSV"
DEFAULT_DB = REPO_ROOT / "tools" / "data" / "portfolio.db"

ACCOUNT_ID = 1

BALANCE_DATE_RE = re.compile(r"^(\d{1,2})/(\d{1,2})/(\d{4})$")


def parse_args(argv=None):
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Import a Schwab daily balances CSV into the portfolio database.")
    parser.add_argument("--csv", type=Path, default=DEFAULT_CSV,
                        help=f"path to the Schwab balances CSV (default: {DEFAULT_CSV})")
    parser.add_argument("--db", type=Path, default=DEFAULT_DB,
                        help=f"path to the DuckDB database file (default: {DEFAULT_DB})")
    return parser.parse_args(argv)


def table_exists(con, name):
    """Return True if the given table exists in the connected database."""
    row = con.execute(
        "SELECT 1 FROM information_schema.tables WHERE table_name = ?", [name]
    ).fetchone()
    return row is not None


def parse_money(value):
    """Parse a CSV money field ('$1,234.56', '-$0.07') into a Decimal."""
    cleaned = (value or "").strip().replace("$", "").replace(",", "")
    if not cleaned:
        raise ValueError("Empty amount field")
    return Decimal(cleaned)


def parse_balance_date(value, line_no):
    """Parse an 'M/D/YYYY' date field into a date."""
    match = BALANCE_DATE_RE.match((value or "").strip())
    if not match:
        raise ValueError(f"Line {line_no}: unrecognized date format: {value!r}")
    return date(int(match.group(3)), int(match.group(1)), int(match.group(2)))


def read_csv(path):
    """Read and normalize every row of the balances CSV into (date, balance) pairs."""
    rows = []
    with open(path, newline="") as handle:
        reader = csv.DictReader(handle)
        for line_no, row in enumerate(reader, start=2):
            balance_date = parse_balance_date(row["Date"], line_no)
            balance = float(parse_money(row["Amount"]))
            rows.append((balance_date, balance))
    return rows


def main(argv=None):
    """Entry point."""
    args = parse_args(argv)
    if not args.csv.is_file():
        raise SystemExit(f"CSV file not found: {args.csv}")

    rows = read_csv(args.csv)

    if not args.db.exists():
        raise SystemExit(
            f"Database {args.db} does not exist. Run tools/initialize_database.py first.")
    con = duckdb.connect(str(args.db))
    try:
        if not table_exists(con, "daily_balances"):
            raise SystemExit(
                f"Database {args.db} is missing the daily_balances table. "
                "Run tools/initialize_database.py first.")

        existing = set(con.execute(
            "SELECT account_id, balance_date FROM daily_balances").fetchall())
        seen = set()
        new_rows = []
        skipped = 0
        for balance_date, balance in rows:
            key = (ACCOUNT_ID, balance_date)
            if key in existing or key in seen:
                skipped += 1
                continue
            seen.add(key)
            new_rows.append((balance_date, ACCOUNT_ID, balance))
        if new_rows:
            con.executemany("INSERT INTO daily_balances VALUES (?, ?, ?)", new_rows)

        print(f"CSV: {args.csv}")
        print(f"Database: {args.db}")
        print(f"Rows read: {len(rows)}")
        print(f"Balances inserted: {len(new_rows)}, skipped as duplicates: {skipped}")
        if new_rows:
            dates = [row[0] for row in new_rows]
            print(f"Date range imported: {min(dates)} to {max(dates)}")
    finally:
        con.close()


if __name__ == "__main__":
    sys.exit(main())
