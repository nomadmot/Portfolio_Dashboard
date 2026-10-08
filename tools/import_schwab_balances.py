"""
Import a Schwab daily balances CSV (e.g. tools/data/Schwab_Balances.CSV)
into the daily_balances table of a DuckDB database
(default: tools/data/portfolio.db). If the database file does not exist,
it is created and initialized by executing the DDL scripts in tools/DDL
in their declared run sequence.
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
DDL_DIR = REPO_ROOT / "tools" / "DDL"

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


def load_ddl_scripts():
    """Return the DDL scripts in tools/DDL sorted by their declared run sequence."""
    if not DDL_DIR.is_dir():
        raise SystemExit(f"DDL directory not found: {DDL_DIR}")
    scripts = []
    for path in sorted(DDL_DIR.glob("*.sql")):
        match = re.search(r"Run sequence:\s*(\d+)", path.read_text())
        if not match:
            raise SystemExit(f"No 'Run sequence' header found in {path}; cannot order DDL scripts.")
        scripts.append((int(match.group(1)), path))
    scripts.sort(key=lambda item: (item[0], item[1].name))
    return [path for _, path in scripts]


def initialize_database(con, scripts):
    """Create all tables by executing each DDL script directly from tools/DDL."""
    for path in scripts:
        con.execute(path.read_text())


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

    is_new_db = not args.db.exists()
    args.db.parent.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(str(args.db))
    try:
        if is_new_db:
            scripts = load_ddl_scripts()
            initialize_database(con, scripts)
            print(f"Created {args.db} and initialized {len(scripts)} tables from {DDL_DIR}")
        else:
            if not table_exists(con, "daily_balances"):
                raise SystemExit(
                    f"Database {args.db} exists but is missing the daily_balances table")

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
