"""
Manage the accounts table in the portfolio database
(default: tools/data/portfolio.db): list, add, and delete brokerage
accounts. New accounts are assigned the next available account_id
unless one is supplied explicitly.
"""
import argparse
import sys
from pathlib import Path

import duckdb

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DB = REPO_ROOT / "tools" / "data" / "portfolio.db"


def parse_args(argv=None):
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="List, add, or delete accounts in the portfolio database.")
    parser.add_argument("--db", type=Path, default=DEFAULT_DB,
                        help=f"path to the DuckDB database file (default: {DEFAULT_DB})")
    subparsers = parser.add_subparsers(dest="command")

    # list
    subparsers.add_parser("list", help="list all accounts")

    # add
    add_parser = subparsers.add_parser("add", help="add a new account")
    add_parser.add_argument("name", help="name for the new account")
    add_parser.add_argument("--id", type=int, dest="account_id", default=None,
                            help="account ID to assign (default: next available)")

    # delete
    delete_parser = subparsers.add_parser("delete", help="delete an account")
    delete_parser.add_argument("account_id", type=int,
                               help="ID of the account to delete")
    delete_parser.add_argument("-y", "--yes", action="store_true",
                               help="skip the confirmation prompt")
    return parser.parse_args(argv)


def connect_database(db_path: Path) -> duckdb.DuckDBPyConnection:
    """
    Open the database file, exiting with an actionable message on failure.
    """
    if not db_path.exists():
        raise SystemExit(
            f"Database {db_path} does not exist. "
            "Run tools/initialize_database.py first.")
    try:
        return duckdb.connect(str(db_path))
    except duckdb.Error as e:
        raise SystemExit(
            f"Could not open database {db_path}: {e}\n"
            "Is the Streamlit app running, or is the file being synced?") from e


def table_exists(con, name):
    """Return True if the given table exists in the connected database."""
    row = con.execute(
        "SELECT 1 FROM information_schema.tables WHERE table_name = ?", [name]
    ).fetchone()
    return row is not None


def count_rows(con, table, account_id):
    """Return the number of rows in the given table for the account, or 0 if absent."""
    if not table_exists(con, table):
        return 0
    return con.execute(
        f"SELECT COUNT(*) FROM {table} WHERE account_id = ?", [account_id]
    ).fetchone()[0]


def cmd_list(con):
    """Print all accounts, one per line, ordered by account_id."""
    rows = con.execute(
        "SELECT account_id, account_name FROM accounts ORDER BY account_id"
    ).fetchall()
    if not rows:
        print("No accounts found.")
        return
    width = max(len(str(row[0])) for row in rows)
    print(f"{'ID'.ljust(width)}  NAME")
    for account_id, account_name in rows:
        print(f"{str(account_id).ljust(width)}  {account_name}")


def cmd_add(con, name, account_id):
    """
    Insert a new account. The account_id defaults to the next available
    integer (max + 1) when not supplied.
    """
    if account_id is None:
        account_id = con.execute(
            "SELECT COALESCE(MAX(account_id), 0) + 1 FROM accounts"
        ).fetchone()[0]
    if account_id <= 0:
        raise SystemExit(f"Account ID must be a positive integer, got {account_id}.")

    existing = con.execute(
        "SELECT account_name FROM accounts WHERE account_id = ?", [account_id]
    ).fetchone()
    if existing:
        raise SystemExit(
            f"Account ID {account_id} already exists ({existing[0]!r}). "
            "Choose a different --id.")

    duplicate = con.execute(
        "SELECT account_id FROM accounts WHERE account_name = ?", [name]
    ).fetchone()
    if duplicate:
        print(f"Note: an account named {name!r} already exists (ID {duplicate[0]}).")

    con.execute("INSERT INTO accounts VALUES (?, ?)", [account_id, name])
    print(f"Added account {account_id}: {name}")


def cmd_delete(con, account_id, assume_yes=False):
    """
    Delete the account with the given ID after checking for dependent data.
    Accounts referenced by trades cannot be deleted; associated balances
    and notes would be orphaned and require explicit confirmation.
    """
    account = con.execute(
        "SELECT account_id, account_name FROM accounts WHERE account_id = ?",
        [account_id],
    ).fetchone()
    if account is None:
        raise SystemExit(f"Account {account_id} does not exist.")
    _, account_name = account

    trade_count = count_rows(con, "trades", account_id)
    if trade_count:
        raise SystemExit(
            f"Cannot delete account {account_id} ({account_name!r}): "
            f"{trade_count} trade(s) reference it.")

    balance_count = count_rows(con, "daily_balances", account_id)
    note_count = count_rows(con, "notes", account_id)
    if balance_count or note_count:
        print(f"Account {account_id} ({account_name!r}) has associated data:")
        if balance_count:
            print(f"  {balance_count} daily balance row(s) would be left behind")
        if note_count:
            print(f"  {note_count} note(s) would be left behind")

    if not assume_yes:
        try:
            answer = input(f"Delete account {account_id} ({account_name!r})? [y/N] ")
        except EOFError:
            answer = ""
        if answer.strip().lower() not in ("y", "yes"):
            print("Aborted.")
            return

    con.execute("DELETE FROM accounts WHERE account_id = ?", [account_id])
    print(f"Deleted account {account_id} ({account_name!r}).")
    if balance_count or note_count:
        print("Associated balance/note rows were left in place.")


def main(argv=None):
    """Entry point."""
    args = parse_args(argv)
    con = connect_database(args.db)
    try:
        if not table_exists(con, "accounts"):
            raise SystemExit(
                f"Database {args.db} has no accounts table. "
                "Run tools/initialize_database.py first.")
        command = args.command or "list"
        if command == "list":
            cmd_list(con)
        elif command == "add":
            cmd_add(con, args.name, args.account_id)
        elif command == "delete":
            cmd_delete(con, args.account_id, assume_yes=args.yes)
    finally:
        con.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
