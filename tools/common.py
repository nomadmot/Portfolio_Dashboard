"""
Shared helpers for the portfolio database tools: opening and initializing
the DuckDB database from the DDL scripts in tools/DDL, and resolving the
target account for import scripts (via --account or an interactive prompt).
"""
import re
import sys
from pathlib import Path

import duckdb

REPO_ROOT = Path(__file__).resolve().parent.parent
DDL_DIR = REPO_ROOT / "tools" / "DDL"

MANAGE_ACCOUNTS_HINT = 'python tools/manage_accounts.py add "<name>"'


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


def open_database(db_path):
    """Open the database, creating and initializing it from tools/DDL if new."""
    is_new_db = not db_path.exists()
    db_path.parent.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(str(db_path))
    if is_new_db:
        scripts = load_ddl_scripts()
        initialize_database(con, scripts)
        print(f"Created {db_path} and initialized {len(scripts)} tables from {DDL_DIR}")
    return con


def fetch_accounts(con):
    """Return (account_id, account_name) pairs ordered by account_id."""
    if not table_exists(con, "accounts"):
        raise SystemExit(
            "Database has no accounts table. Run tools/initialize_database.py first.")
    return con.execute(
        "SELECT account_id, account_name FROM accounts ORDER BY account_id"
    ).fetchall()


def resolve_account_id(con, cli_account_id):
    """
    Determine the target account ID: validate a CLI-supplied ID or prompt
    interactively with a menu of the available accounts. Exits if the
    accounts table is empty, the CLI ID is unknown, or no selection can be
    made (non-interactive stdin without --account).
    """
    accounts = fetch_accounts(con)
    if not accounts:
        raise SystemExit(
            "No accounts found in the accounts table.\n"
            f"Add one first, e.g.:\n    {MANAGE_ACCOUNTS_HINT}")

    ids = {account_id for account_id, _ in accounts}
    if cli_account_id is not None:
        if cli_account_id not in ids:
            raise SystemExit(
                f"Account ID {cli_account_id} not found in the accounts table.\n"
                "Run tools/manage_accounts.py list to see available accounts.")
        return cli_account_id

    if not sys.stdin.isatty():
        raise SystemExit(
            "No account given via --account and no interactive terminal is available.")

    print("Available accounts:")
    for account_id, account_name in accounts:
        print(f"  [{account_id}] {account_name}")
    default_id = 1 if 1 in ids else accounts[0][0]
    while True:
        try:
            raw = input(f"Enter account ID ({default_id}): ").strip()
        except EOFError:
            raise SystemExit("Aborted.")
        if not raw:
            raw = str(default_id)
        if not raw.isdigit():
            print(f"Not a valid account ID: {raw}")
            continue
        account_id = int(raw)
        if account_id not in ids:
            print(f"Account ID {account_id} not found.")
            continue
        return account_id
