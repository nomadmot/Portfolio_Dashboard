'''Test suite for the configuration system'''
from config import SETTINGS
from config.settings import LogLevelEnum

def test_default_settings():
    '''Verify default settings when no environment variables are set'''
    assert not SETTINGS.debug
    assert SETTINGS.database_file == "/path/to/your/database.db"
    assert SETTINGS.loglevel_application == LogLevelEnum("INFO")
    assert SETTINGS.loglevel_streamlit == LogLevelEnum("WARN")
