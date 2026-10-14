# Portfolio Dashboard - Agent Instructions

## Development Commands
- **Run App**: `./run_app.sh` (activates `./.venv`, enters `src/`, runs Streamlit)
- **Build Docker**: `./docker/build.sh`
- **Run Tests**: `/tmp/environments/Portfolio_Dashboard_DEV/.venv/bin/python -m pytest` (from the repo root; `pythonpath` is set in `pyproject.toml`)

> There is no `load-env.sh`. Environment variables are loaded automatically by
> pydantic-settings from `.settings/.env` (resolved relative to the working directory —
> `src/.settings/.env` when the app runs).

## Critical Constraints
- **Imports**: Python execution path starts in `src/`. Do NOT include `src.` in imports.
- **Env Vars**: The database is a single DuckDB file configured via `DATABASE_FILE` (path to the `.db`); watchlists live in the folder set by `WATCHLIST_FOLDER`. There is **no separate data path and no DuckLake**.
- **Env File**: `.env` must be located in `src/.settings/`.
- **Docker Mount**: Mount the data volume to `/var/data` (the DuckDB file) and the watchlists volume to `/var/watchlists` (see `docker/Dockerfile` and `docker/run.sh`). The layout may still evolve.

## Architecture & Key Files
- **Entry Point**: `src/app.py` (Navigation and routing)
- **Pages**: `src/pages/`
- **Core Logic**: `src/core/`
- **Config**: `src/.settings/app_config.yml`
- **Database**: DuckDB in `src/utility/database.py`. One self-contained database file (`SETTINGS.database_file`) holds the app's tables (accounts/balances/securities) **and** the `market_holidays` table. The shared `DATABASE_CONNECTION` connection is used across `core/*` and `utility/*`; there is no separate parquet data path.
- **Market Calendar**: `src/utility/market_calendar.py` queries the `market_holidays` table through `DATABASE_CONNECTION`.

## Environment Setup

The repository lives on a filesystem **shared between two machines**, so a single in-repo
virtual environment cannot be safely used by both. Each machine keeps its own copy of the
environment in machine-local `/tmp` instead. This pattern applies to all projects:
`/tmp/environments/<project-directory-name>/`.

- **Location**: `/tmp/environments/Portfolio_Dashboard_DEV/`
- **Create it** (on a machine that does not have it yet — e.g. after a reboot clears `/tmp`):
  1. `mkdir -p /tmp/environments/Portfolio_Dashboard_DEV`
  2. Copy `pyproject.toml` and `uv.lock` from the repo root into that directory
  3. Run `uv sync --all-extras` inside it (creates `/tmp/environments/Portfolio_Dashboard_DEV/.venv`)
- USE `/tmp/environments/Portfolio_Dashboard_DEV/.venv` FOR ALL DEVELOPMENT ACTIVITIES (tests, tools, scripts)
- `./run_app.sh` intentionally keeps using the in-repo `./.venv`; leave it as is.
- DO NOT CREATE, SYNC INTO, OR MODIFY THE IN-REPO `./.venv` (or any other existing Python environment).

## Testing
- Tests are located in `tests/` and run via `/tmp/environments/Portfolio_Dashboard_DEV/.venv/bin/python -m pytest` from the repo root.
- `tests/test_obsidian.py` makes a live network call at collection time and requires a running Obsidian server; run the suite with `--ignore=tests/test_obsidian.py` unless that server is up.
