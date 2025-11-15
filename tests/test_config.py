"""
Tests for configuration settings.
"""

import os
from config.settings import Settings


def test_settings_defaults():
    """Test default settings values."""
    settings = Settings()
    
    # Should have default values
    assert settings.app_env in ['development', 'production']
    assert settings.log_level in ['DEBUG', 'INFO', 'WARNING', 'ERROR']
    assert settings.api_port > 0
    assert settings.dashboard_port > 0


def test_settings_from_env():
    """Test loading settings from environment."""
    # Set some environment variables
    os.environ['APP_ENV'] = 'test'
    os.environ['API_PORT'] = '9000'
    
    settings = Settings()
    
    assert settings.app_env == 'test'
    assert settings.api_port == 9000
    
    # Cleanup
    del os.environ['APP_ENV']
    del os.environ['API_PORT']


def test_settings_database_url():
    """Test database URL configuration."""
    settings = Settings()
    assert settings.database_url is not None
    assert isinstance(settings.database_url, str)
