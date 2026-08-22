# Analysis — Removing DuckLake (Issue #185)

## Background
The Portfolio Dashboard originally used **DuckLake** as a cataloging layer over a Parquet
"Data Lake" (the *Duck Puddle*). DuckLake was adopted in commit `8bd406e`
("remove duck puddle data path from settings, change database uri to database catalog,
use database catalog to determine duck puddle data path"), which:
- renamed the `database_uri` setting to `database_catalog` and dropped the separate `duck_puddle` data-path setting,
- changed the engine to `LOAD ducklake; ATTACH '<path>'` the catalog + data lake,
- derived the data path by reading the `data_path` key from DuckLake's `ducklake_metadata` table.

Issue #185 reverts this: the app runs on a **single, self-contained DuckDB file**
with no DuckLake and no separate Parquet directory.

## Before vs After

| Concern | Before (DuckLake) | After |
| --- | --- | --- |
| Catalog | `ducklake:<path>.duckdb` + `LOAD ducklake; ATTACH ...` | plain `duckdb.connect(<path>.db)` |
| Market holidays | Parquet file read by path via `duckdb.sql()` | `market_holidays` table in the database file, queried via `DATABASE_CONNECTION` |
| Data path | `DUCKDB_DATA_PATH` (separate Parquet dir) | **removed** — no separate data path |
| Env var | `DATABASE_URI` + `DUCK_PUDDLE` | `DATABASE_FILE` only |
| `ducklake` dependency | `LOAD ducklake` at runtime | not needed (no DuckLake extension, no Python dep) |

## Design Decision
Everything — the app's mutable tables **and** the market calendar — lives in one
`.db` file. The market-calendar Parquet is imported into a `market_holidays` table, so the
separate `DUCK_PUDDLE*/DATA` directory is no longer needed and `DUCKDB_DATA_PATH` is
deleted. The market calendar now uses the same shared `DATABASE_CONNECTION` the rest of
the app uses.

## Changes
- `src/utility/database.py` — engine is a plain `duckdb.connect(SETTINGS.database_catalog)`;
  removed `_data_path()` / `DUCKDB_DATA_PATH` and all DuckLake blocks.
- `src/utility/market_calendar.py` — `get_closed_count` / `market_is_open` query the
  `market_holidays` table through `DATABASE_CONNECTION` using parameterized `?` bindings
  (was string-interpolated dates against a parquet path).
- `src/utility/__init__.py`, `src/utility/system_info.py` — dropped `DUCKDB_DATA_PATH`.
- `src/.settings/.env-example`, `docker/env-prod`, `docker/compose.yaml` —
  `DATABASE_URI=ducklake:…` / `DUCK_PUDDLE=…` → `DATABASE_CATALOG=…`.
- `tests/test_config.py` — fixed the default-catalog assertion; removed stale commented tests.
- `tests/test_market_calendar.py` — mock `DATABASE_CONNECTION` instead of the removed `sql`.
- `AGENTS.md` — updated the stale env-var, mount, venv, and `load-env.sh` references.

## Precondition (data, not code)
The database file (e.g. `DUCK_PUDDLE_TEST/portfolio_test.db`) must contain a
**`market_holidays`** table with `Status` and `Date` columns — import the old
`market_holidays.parquet` into it. The app performs no `CREATE TABLE`; it expects tables
to pre-exist.

## Verification
- `31 passed` via `./.venv/bin/python -m pytest --ignore=tests/test_obsidian.py`
  (`test_obsidian.py` makes a live HTTP call at collection time and is unrelated to this change).
- Functional check against a temp database file with a `market_holidays` table:
  `market_is_open` and `get_closed_count` behave correctly (weekends short-circuit; table
  drives the open/closed result; counts are right).
- `import utility` succeeds cleanly; **zero** `ducklake` references remain in
  `src/`, `docker/`, or `tests/`.

## Open Notes / Follow-ups
- The `database_catalog` setting was renamed to `database_file` (env var `DATABASE_FILE`)
  after this analysis, and the `.db` extension is the norm. Historical references to
  `database_catalog` / `DATABASE_CATALOG` above record the original #185 work.
- `docker/compose.yaml` still mounts to `/home/appuser/investorlab` while `docker/Dockerfile`
  and `docker/run.sh` use `/var/investorlab`. Reconcile to a single path.
- The `DUCK_PUDDLE*` strings remaining in the `.env` / `compose.yaml` files are directory
  **names** (kept by decision), not DuckLake references.
- The `.db` file itself is user-managed (gitignored / not in the repo); create the
  `market_holidays` table in it before running.
