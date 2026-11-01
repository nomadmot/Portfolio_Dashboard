"""
Create and initialize the portfolio DuckDB database (default:
tools/data/portfolio.db) by executing the DDL scripts in tools/DDL in
their declared run sequence. The accounts table is created empty; after
initialization the script offers to add accounts interactively using the
add logic from manage_accounts.py.
"""
import argparse
import re
import sys
from pathlib import Path

import duckdb

from common import DDL_DIR, MANAGE_ACCOUNTS_HINT, REPO_ROOT, initialize_database, load_ddl_scripts
from manage_accounts import cmd_add

DEFAULT_DB = REPO_ROOT / "tools" / "data" / "portfolio.db"

CREATE_TABLE_RE = re.compile(
    r"CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?([A-Za-z_][A-Za-z0-9_]*)", re.IGNORECASE)


def parse_args(argv=None):
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Create and initialize the portfolio database from tools/DDL.")
    parser.add_argument("--db", type=Path, default=DEFAULT_DB,
                        help=f"path to the DuckDB database file (default: {DEFAULT_DB})")
    parser.add_argument("--force", action="store_true",
                        help="re-initialize an existing database, dropping all tables")
    return parser.parse_args(argv)


def drop_existing_tables(con, scripts):
    """Drop tables created by the DDL scripts in reverse run-sequence order."""
    for path in reversed(scripts):
        match = CREATE_TABLE_RE.search(path.read_text())
        if match:
            con.execute(f'DROP TABLE IF EXISTS "{match.group(1)}"')


def offer_add_accounts(con):
    """
    Interactively offer to add accounts to a database with an empty
    accounts table, looping until the user declines. On non-interactive
    stdin, print a pointer to manage_accounts.py instead.
    """
    print("No accounts in the database.")
    if not sys.stdin.isatty():
        print(f"Add one with: {MANAGE_ACCOUNTS_HINT}")
        return

    first = True
    while True:
        prompt = "Add an account now? [y/N]: " if first else "Add another account? [y/N]: "
        first = False
        try:
            answer = input(prompt).strip().lower()
        except EOFError:
            return
        if answer not in ("y", "yes"):
            return
        try:
            name = input("Account name: ").strip()
        except EOFError:
            print("Aborted.")
            return
        if not name:
            print("No name given; skipping.")
            continue
        cmd_add(con, name, None)


def main(argv=None):
    """Entry point."""
    args = parse_args(argv)
    if args.db.exists() and not args.force:
        raise SystemExit(
            f"Database {args.db} already exists. Re-initializing drops all tables; "
            "pass --force to override.")

    con = duckdb.connect(str(args.db))
    try:
        scripts = load_ddl_scripts()
        drop_existing_tables(con, scripts)
        initialize_database(con, scripts)

        tables = [r[0] for r in con.execute(
            "SELECT table_name FROM information_schema.tables "
            "WHERE table_schema = 'main' ORDER BY table_name").fetchall()]
        accounts = con.execute("SELECT account_id, account_name FROM accounts").fetchall()

        print(f"Database: {args.db}")
        print(f"Initialized {len(scripts)} DDL scripts from {DDL_DIR}")
        for account_id, name in accounts:
            print(f"Account {account_id}: {name}")
        if not accounts:
            offer_add_accounts(con)
    finally:
        con.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
