# Portfolio Dashboard - Agent Instructions

## Development Commands
- **Run App**: `./run_app.sh` (activates venv, enters `src/`, runs Streamlit)
- **Load Env**: `source ./load-env.sh` (loads `.env` from `src/.settings/`)
- **Build Docker**: `./docker/build.sh`

## Critical Constraints
- **Imports**: Python execution path starts in `src/`. Do NOT include `src.` in imports.
- **Env Vars**: Database requires both `DATABASE_URI` and `DUCK_PUDLE`.
- **Env File**: `.env` must be located in `src/.settings/`.
- **Docker Mount**: Data volume must be mounted to `/home/appuser/investorlab`.

## Architecture & Key Files
- **Entry Point**: `src/app.py` (Navigation and routing)
- **Pages**: `src/pages/`
- **Core Logic**: `src/core/`
- **Config**: `src/.settings/app_config.yml`
- **Database**: DuckDB integration in `src/utility/database.py`

## Environment Setup

- USE THE PYTHON ENVIRONMENT LOCATED AT /home/dev/Github/Portfolio-Dashboard/.venv FOR ALL ACTIVITIES
- DO NOT MODIFY EXISTING PYTHON ENVIRONMENTS OR ADD ANY LIBRARIES

## Testing
- Tests are located in `tests/`.
