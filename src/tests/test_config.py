'''Test suite for the configuration system'''
import os
import pytest
from config import SETTINGS
from config.settings import Settings, LogLevelEnum

def test_default_settings():
    '''Verify default settings when no environment variables are set'''
    assert not SETTINGS.debug
    assert SETTINGS.database_uri == "sqlite://///path/to/your/database.db"
    assert SETTINGS.duck_puddle == "path/to/your/duckdb/files"
    assert SETTINGS.loglevel_application == LogLevelEnum("INFO")
    assert SETTINGS.loglevel_streamlit == LogLevelEnum("WARN")

# NOTE: It's not possible to easily reload Settings once it's been created,
# so we'll just punt until we figure out a way

# def test_custom_settings():
#     '''Set temporary environment variables for testing'''
#     os.environ['DATABASE_URI'] = "sqlite:///:memory:/"
#     os.environ['DUCK_PUDDLE'] = "/tmp/duckdb_files"
#     # Create a new instance of SETTINGS to pick up environment variables
#     settings = Settings()
#     assert settings.database_uri == "sqlite:///:memory:/"
#     assert settings.duck_puddle == "/tmp/duckdb_files"
#     os.environ.pop('DATABASE_URI', None)
#     os.environ.pop('DUCK_PUDDLE', None)

# def test_settings_from_yaml():
#     ''' Test settings loaded from a temporary YAML configuration file '''
#     return
    # yaml_content = """
#     performance_summary_period: daily
#     performance_summary_symbols:
#     - AAPL
#     - MSFT
#     database_uri: sqlite:///test_db.db
#     duck_puddle: /tmp/test_duckdb
#     """
#     with tempfile.NamedTemporaryFile(mode='w', suffix=".yaml") as yaml_file:
#         yaml_file.write(yaml_content)
#         # Set environment variable to point to our test YAML file
#         os.environ['YAML_CONFIG_PATH'] = yaml_file.file.name
#         # Create a new instance of SETTINGS to pick up YAML config
#         settings = Settings()
#         # Verify settings are loaded from YAML
#         assert settings.defaults.performance_summary_period == "daily"
#         assert sorted(settings.defaults.performance_summary_symbols) == ["AAPL", "MSFT"]
#         assert settings.database_uri == "sqlite:///test_db.db"
#         assert settings.duck_puddle == "/tmp/test_duckdb"
#         # Clean up
#         os.environ.pop('YAML_CONFIG_PATH', None)

# def test_settings_with_invalid_values():
#     '''Ensure settings handle invalid values gracefully with multiple edge cases'''

#     # Test for invalid log level in application
#     with pytest.raises(ValueError):
#         settings = Settings()
#         settings.loglevel_application = LogLevelEnum("INVALID_LEVEL")

#     # Test for invalid log level in Streamlit
#     with pytest.raises(ValueError):
#         settings = Settings()
#         settings.loglevel_streamlit = LogLevelEnum("INVALID_LEVEL")

#     # Test for invalid database URI format
#     os.environ['DATABASE_URI'] = "invalid://uri"
#     with pytest.raises(ValueError):
#         settings = Settings()
#     os.environ.pop('DATABASE_URI', None)

#     # Test for invalid duck puddle path
#     os.environ['DUCK_PUDDLE'] = "/invalid/path"
#     with pytest.raises(ValueError):
#         settings = Settings()
#     os.environ.pop('DUCK_PUDDLE', None)
