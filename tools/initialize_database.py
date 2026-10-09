"""
Create and initialize the portfolio DuckDB database (default:
tools/data/portfolio.db) by executing the DDL scripts in tools/DDL in
their declared run sequence. The seed INSERT for the accounts table is
executed as a parameterized statement using an account name supplied via
--account-name or entered interactively.
"""
import argparse
import re
import sys
from pathlib import Path

import duckdb

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DB = REPO_ROOT / "tools" / "data" / "portfolio.db"
DDL_DIR = REPO_ROOT / "tools" / "DDL"

DEFAULT_ACCOUNT_NAME = "Schwab Trading"
ACCOUNT_ID = 1

ACCOUNTS_INSERT_RE = re.compile(r"INSERT\s+INTO\s+accounts\b", re.IGNORECASE)
STRING_LITERAL_RE = re.compile(r"'[^']*'")
CREATE_TABLE_RE = re.compile(
    r"CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?([A-Za-z_][A-Za-z0-9_]*)", re.IGNORECASE)


def parse_args(argv=None):
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Create and initialize the portfolio database from tools/DDL.")
    parser.add_argument("--db", type=Path, default=DEFAULT_DB,
                        help=f"path to the DuckDB database file (default: {DEFAULT_DB})")
    parser.add_argument("--account-name",
                        help=f"name for account {ACCOUNT_ID}; prompted if omitted "
                             f"(default: {DEFAULT_ACCOUNT_NAME!r})")
    parser.add_argument("--force", action="store_true",
                        help="re-initialize an existing database, dropping all tables")
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


def split_statements(text):
    """Split a DDL script into individual statements, ignoring comment lines."""
    lines = [line for line in text.splitlines() if not line.strip().startswith("--")]
    return [chunk.strip() for chunk in "\n".join(lines).split(";") if chunk.strip()]


def parameterize_account_insert(statement):
    """Replace the string literal in an accounts INSERT statement with a placeholder."""
    literals = STRING_LITERAL_RE.findall(statement)
    if len(literals) != 1:
        raise SystemExit(
            f"Expected exactly one string literal in {statement!r}, found {len(literals)}.")
    return STRING_LITERAL_RE.sub("?", statement)


def drop_existing_tables(con, scripts):
    """Drop tables created by the DDL scripts in reverse run-sequence order."""
    for path in reversed(scripts):
        match = CREATE_TABLE_RE.search(path.read_text())
        if match:
            con.execute(f'DROP TABLE IF EXISTS "{match.group(1)}"')


def initialize_database(con, scripts, account_name):
    """Create all tables by executing each DDL script directly from tools/DDL."""
    for path in scripts:
        text = path.read_text()
        if ACCOUNTS_INSERT_RE.search(text):
            for statement in split_statements(text):
                if ACCOUNTS_INSERT_RE.search(statement):
                    con.execute(parameterize_account_insert(statement), [account_name])
                else:
                    con.execute(statement)
        else:
            con.execute(text)


def main(argv=None):
    """Entry point."""
    args = parse_args(argv)
    if args.db.exists() and not args.force:
        raise SystemExit(
            f"Database {args.db} already exists. Re-initializing drops all tables; "
            "pass --force to override.")

    account_name = args.account_name
    if account_name is None:
        entered = input(f"Account name [{DEFAULT_ACCOUNT_NAME}]: ").strip()
        account_name = entered or DEFAULT_ACCOUNT_NAME

    con = duckdb.connect(str(args.db))
    try:
        scripts = load_ddl_scripts()
        drop_existing_tables(con, scripts)
        initialize_database(con, scripts, account_name)

        count = con.execute("SELECT COUNT(*) FROM accounts").fetchone()[0]
        if count == 0:
            con.execute("INSERT INTO accounts VALUES (?, ?)", [ACCOUNT_ID, account_name])

        tables = [r[0] for r in con.execute(
            "SELECT table_name FROM information_schema.tables "
            "WHERE table_schema = 'main' ORDER BY table_name").fetchall()]
        accounts = con.execute("SELECT account_id, account_name FROM accounts").fetchall()

        print(f"Database: {args.db}")
        print(f"Initialized {len(scripts)} DDL scripts from {DDL_DIR}")
        print(f"Tables: {', '.join(tables)}")
        for account_id, name in accounts:
            print(f"Account {account_id}: {name}")
    finally:
        con.close()


if __name__ == "__main__":
    sys.exit(main())
