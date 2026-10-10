"""
Import a Schwab transactions CSV (e.g. tools/data/Schwab_Transactions.csv)
into the trades and securities tables of a DuckDB database
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
DEFAULT_CSV = REPO_ROOT / "tools" / "data" / "Schwab_Transactions.csv"
DEFAULT_DB = REPO_ROOT / "tools" / "data" / "portfolio.db"

CASH_SYMBOL = "$CASH"
ACCOUNT_ID = 1

OPTION_ACTIONS = {"Buy to Open", "Sell to Open", "Buy to Close",
                  "Sell to Close", "Expired"}

ACTION_TO_TRADE_TYPE = {
    "Buy": "BUY",
    "Sell": "SELL",
    "Buy to Open": "BUY",
    "Sell to Open": "SELL",
    "Buy to Close": "BUY",
    "Sell to Close": "SELL",
    "Expired": "EXPR",
    "Security Transfer": "TRAN",
    "Journal": "JRNL",
    "Stock Split": "SPLT",
    "Qualified Dividend": "DIV",
    "Cash Dividend": "DIV",
    "Credit Interest": "INT",
    "Margin Interest": "INT",
    "Interest Adj": "INT",
    "Foreign Tax Paid": "TAX",
    "Service Fee": "FEE",
    "Funds Received": "DEP",
    "MoneyLink Transfer": "DEP",
    "Returned Check": "WDL",
}

OPTION_SYMBOL_RE = re.compile(r"^([A-Z][A-Z.\-]*) (\d{2}/\d{2}/\d{4}) ([\d.]+) (C|P)$")


def parse_args(argv=None):
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Import a Schwab transactions CSV into the portfolio database.")
    parser.add_argument("--csv", type=Path, default=DEFAULT_CSV,
                        help=f"path to the Schwab transactions CSV (default: {DEFAULT_CSV})")
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
    """Parse a CSV money field ('$1,234.56', '-$0.07') into a Decimal, or None if empty."""
    cleaned = (value or "").strip().replace("$", "").replace(",", "")
    if not cleaned:
        return None
    return Decimal(cleaned)


def parse_trade_date(value):
    """Parse 'MM/DD/YYYY' (tolerating an 'as of ...' suffix) into a date."""
    match = re.match(r"^(\d{2})/(\d{2})/(\d{4})", value.strip())
    if not match:
        raise ValueError(f"Unrecognized date format: {value!r}")
    return date(int(match.group(3)), int(match.group(1)), int(match.group(2)))


def to_occ_symbol(symbol):
    """Convert a Schwab option symbol ('QQQ 11/21/2025 612.00 P') to OCC format."""
    match = OPTION_SYMBOL_RE.match(symbol.strip())
    if not match:
        raise ValueError(f"Unrecognized option symbol: {symbol!r}")
    root, exp, strike, opt_type = match.groups()
    month, day, year = (int(part) for part in exp.split("/"))
    exp_date = date(year, month, day)
    strike_milli = int(Decimal(strike) * 1000)
    return f"{root}{exp_date:%y%m%d}{opt_type}{strike_milli:08d}", root


def security_type_for(action, symbol, description):
    """Determine the securities.security_type value for an imported row."""
    if action in OPTION_ACTIONS:
        return "O"
    if symbol == CASH_SYMBOL:
        return "C"
    if "ETF" in description.upper():
        return "E"
    return "S"


def position_effect_for(action, symbol, quantity):
    """Determine the trades.position_effect value for an imported row."""
    if symbol == CASH_SYMBOL:
        return None
    if action in ("Buy", "Buy to Open", "Sell to Open"):
        return "To Open"
    if action in ("Sell", "Buy to Close", "Sell to Close", "Expired"):
        return "To Close"
    if action in ("Journal", "Security Transfer") and quantity != 0:
        return "To Open" if quantity > 0 else "To Close"
    return None


def normalize_row(row, line_no):
    """Convert one raw CSV row into normalized trade and security data."""
    action = row["Action"].strip()
    trade_type = ACTION_TO_TRADE_TYPE.get(action)
    if trade_type is None:
        raise ValueError(f"Line {line_no}: unmapped action {action!r}")

    symbol_raw = row["Symbol"].strip()
    description = row["Description"].strip()
    associated_symbol = None
    if action in OPTION_ACTIONS:
        symbol, associated_symbol = to_occ_symbol(symbol_raw)
    elif symbol_raw:
        symbol = symbol_raw
    else:
        symbol = CASH_SYMBOL

    quantity = parse_money(row["Quantity"])
    price = parse_money(row["Price"])
    fees = parse_money(row["Fees & Comm"])
    amount = parse_money(row["Amount"])

    if action == "MoneyLink Transfer":
        trade_type = "DEP" if (amount or Decimal(0)) >= 0 else "WDL"

    if quantity is None and price is None:
        price = amount if amount is not None else Decimal(0)
        quantity = Decimal(0)
    quantity = quantity if quantity is not None else Decimal(0)
    price = price if price is not None else Decimal(0)
    fees = fees if fees is not None else Decimal(0)

    security_name = "Cash" if symbol == CASH_SYMBOL else (description or symbol)
    security_type = security_type_for(action, symbol, description)
    position_effect = position_effect_for(action, symbol, quantity)

    return {
        "trade": (ACCOUNT_ID, symbol, parse_trade_date(row["Date"]), trade_type,
                  position_effect, float(quantity), float(price), float(fees)),
        "security": (symbol, security_name, security_type, associated_symbol),
    }


def read_csv(path):
    """Read and normalize every row of the transactions CSV."""
    rows = []
    with open(path, newline="") as handle:
        reader = csv.DictReader(handle)
        for line_no, row in enumerate(reader, start=2):
            rows.append(normalize_row(row, line_no))
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
        missing = [t for t in ("securities", "trades") if not table_exists(con, t)]
        if missing:
            raise SystemExit(
                f"Database {args.db} is missing tables: {', '.join(missing)}. "
                "Run tools/initialize_database.py first.")

        securities_map = {}
        for row in rows:
            securities_map.setdefault(row["security"][0], row["security"])

        existing_symbols = {r[0] for r in con.execute("SELECT symbol FROM securities").fetchall()}
        new_securities = [sec for sym, sec in securities_map.items() if sym not in existing_symbols]
        if new_securities:
            con.executemany("INSERT INTO securities VALUES (?, ?, ?, ?)", new_securities)

        existing_trades = set(con.execute(
            "SELECT account_id, symbol, trade_date, trade_type, position_effect, "
            "quantity, price, fees FROM trades").fetchall())
        next_id = con.execute("SELECT COALESCE(MAX(id), 0) + 1 FROM trades").fetchone()[0]

        new_trades = []
        skipped = 0
        for row in rows:
            if row["trade"] in existing_trades:
                skipped += 1
                continue
            new_trades.append((next_id, *row["trade"]))
            next_id += 1
        if new_trades:
            con.executemany(
                "INSERT INTO trades (id, account_id, symbol, trade_date, trade_type, "
                "position_effect, quantity, price, fees) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                new_trades)

        type_counts = {}
        for trade in (t[1:] for t in new_trades):
            type_counts[trade[3]] = type_counts.get(trade[3], 0) + 1

        print(f"CSV: {args.csv}")
        print(f"Database: {args.db}")
        print(f"Rows read: {len(rows)}")
        print(f"Securities inserted: {len(new_securities)} (of {len(securities_map)} distinct)")
        print(f"Trades inserted: {len(new_trades)}, skipped as duplicates: {skipped}")
        for trade_type in sorted(type_counts):
            print(f"  {trade_type}: {type_counts[trade_type]}")
    finally:
        con.close()


if __name__ == "__main__":
    sys.exit(main())
