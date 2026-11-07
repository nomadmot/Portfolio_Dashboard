"""
Create and populate the market_holidays table in the portfolio database
(default: tools/data/portfolio.db) with NYSE market holidays beginning ten
calendar years ago through five years in the future. The table schema is
read directly from tools/DDL/market_holidays.sql. Closed holidays are stored
with Status 'Closed'; early-close trading days are stored with Status 'Open'
and a Close_Time, so the app's open/closed lookups stay correct.
"""
import argparse
import sys
from datetime import date, timedelta
from pathlib import Path

import duckdb

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DB = REPO_ROOT / "tools" / "data" / "portfolio.db"
DDL_FILE = REPO_ROOT / "tools" / "DDL" / "market_holidays.sql"

YEARS_PAST = 10
YEARS_FUTURE = 5
EARLY_CLOSE_TIME = "13:00 ET"


def parse_args(argv=None):
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Create and populate the market_holidays table with NYSE holidays.")
    parser.add_argument("--db", type=Path, default=DEFAULT_DB,
                        help=f"path to the DuckDB database file (default: {DEFAULT_DB})")
    return parser.parse_args(argv)


def easter_sunday(year):
    """Return the date of Easter Sunday for the given year (Gregorian computus)."""
    a = year % 19
    b, c = divmod(year, 100)
    d, e = divmod(b, 4)
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i, k = divmod(c, 4)
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    month = (h + l - 7 * m + 114) // 31
    day = ((h + l - 7 * m + 114) % 31) + 1
    return date(year, month, day)


def nth_weekday(year, month, weekday, n):
    """Return the n-th (1-based) given weekday (Monday=0) of the given month."""
    first = date(year, month, 1)
    offset = (weekday - first.weekday()) % 7
    return first + timedelta(days=offset + 7 * (n - 1))


def observed(fixed_day):
    """Return the observed date when a fixed holiday falls on a weekend."""
    if fixed_day.weekday() == 5:
        return fixed_day - timedelta(days=1)
    if fixed_day.weekday() == 6:
        return fixed_day + timedelta(days=1)
    return fixed_day


def market_days_for_year(year):
    """Return NYSE holiday and early-close rows nominally belonging to the year.

    Each row is (date, holiday, status, close_time, note). A New Year's Day
    observed on December 31 may carry the previous calendar year's date.
    """
    rows = []

    def add(day, name, status="Closed", close_time=None, note=""):
        rows.append((day, name, status, close_time, note))

    jan_1 = date(year, 1, 1)
    if jan_1.weekday() == 5:
        add(date(year - 1, 12, 31), "New Year's Day",
            note="Observed (Jan 1 falls on a Saturday)")
    elif jan_1.weekday() == 6:
        add(date(year, 1, 2), "New Year's Day",
            note="Observed (Jan 1 falls on a Sunday)")
    else:
        add(jan_1, "New Year's Day")

    add(nth_weekday(year, 1, 0, 3), "Martin Luther King Jr. Day")
    add(nth_weekday(year, 2, 0, 3), "Washington's Birthday")
    add(easter_sunday(year) - timedelta(days=2), "Good Friday")

    for fixed, name in ((date(year, 6, 19), "Juneteenth National Independence Day"),
                        (date(year, 7, 4), "Independence Day"),
                        (date(year, 12, 25), "Christmas Day")):
        day = observed(fixed)
        note = "" if day == fixed else f"Observed ({name} falls on a {fixed:%A})"
        add(day, name, note=note)

    add(nth_weekday(year, 9, 0, 1), "Labor Day")

    thanksgiving = nth_weekday(year, 11, 3, 4)
    add(thanksgiving, "Thanksgiving Day")
    add(thanksgiving + timedelta(days=1), "Day After Thanksgiving",
        status="Open", close_time=EARLY_CLOSE_TIME, note="Early close")

    christmas_eve = date(year, 12, 24)
    if christmas_eve.weekday() < 5 and christmas_eve != observed(date(year, 12, 25)):
        add(christmas_eve, "Christmas Eve",
            status="Open", close_time=EARLY_CLOSE_TIME, note="Early close")

    return rows


def table_exists(con, name):
    """Return True if the given table exists in the connected database."""
    row = con.execute(
        "SELECT 1 FROM information_schema.tables WHERE table_name = ?", [name]
    ).fetchone()
    return row is not None


def main(argv=None):
    """Entry point."""
    args = parse_args(argv)
    if not args.db.exists():
        raise SystemExit(
            f"Database {args.db} does not exist. Run tools/initialize_database.py first.")
    if not DDL_FILE.is_file():
        raise SystemExit(f"DDL file not found: {DDL_FILE}")

    start_year = date.today().year - YEARS_PAST
    end_year = date.today().year + YEARS_FUTURE
    range_start = date(start_year, 1, 1)
    range_end = date(end_year, 12, 31)

    entries = {}
    for year in range(start_year, end_year + 2):
        for day, name, status, close_time, note in market_days_for_year(year):
            if range_start <= day <= range_end:
                entries.setdefault(day, (day.year, day, name, status, close_time, note))
    rows = [entries[day] for day in sorted(entries)]

    con = duckdb.connect(str(args.db))
    try:
        if table_exists(con, "market_holidays"):
            con.execute("DROP TABLE market_holidays")
        con.execute(DDL_FILE.read_text())
        con.executemany("INSERT INTO market_holidays VALUES (?, ?, ?, ?, ?, ?)", rows)

        closed = sum(1 for row in rows if row[3] == "Closed")
        print(f"Database: {args.db}")
        print(f"Holidays inserted: {len(rows)} ({closed} closed, {len(rows) - closed} early close)")
        print(f"Date range: {rows[0][1]} to {rows[-1][1]}")
    finally:
        con.close()


if __name__ == "__main__":
    sys.exit(main())
