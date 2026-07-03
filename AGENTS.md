# Portfolio Dashboard - Agent Instructions

## Development Commands

- **Run the app**: `./run_app.sh` (activates venv and runs Streamlit)
- **Build Docker image**: `./docker/build.sh`

## Architecture

- **Main entry point**: `src/app.py` - Streamlit navigation and page routing
- **Pages**: Individual Streamlit pages in `src/pages/`
- **Core logic**: Portfolio operations in `src/core/`
- **Configuration**: Settings loaded from `src/.settings/app_config.yml`
- **Database**: DuckDB integration in `src/utility/database.py`

## Environment Setup

- USE THE PYTHON ENVIRONMENT LOCATED AT /home/dev/Github/Portfolio-Dashboard/.venv FOR ALL ACTIVITIES
- DO NOT MODIFY EXISTING PYTHON ENVIRONMENTS OR ADD ANY LIBRARIES

## Testing

- Test files are in `src/tests/` (not at root)
- No CI/CD workflows configured

## Docker Notes

- Database path must be mounted to `/home/appuser/investorlab`
- Environment variables configured in `docker/compose.yaml`

## Key Files

- `src/app.py`: Main Streamlit application with navigation
- `src/.settings/app_config.yml`: Configuration file
- `docker/Dockerfile`: Build configuration

## Important Constraints

- Database connection requires both `DATABASE_URI` and `DUCK_PUDLE` environment variables
- `.env` file must be in `src/.settings/` directory
- Database path must be mounted to `/home/appuser/investorlab` for Docker
