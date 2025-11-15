"""Configuration management for Steam Insights."""

import os
from typing import Optional
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    """Application settings."""
    
    # Steam API
    steam_api_key: str = os.getenv('STEAM_API_KEY', '')
    
    # Database
    database_url: str = os.getenv('DATABASE_URL', 'sqlite:///steam_insights.db')
    db_host: str = os.getenv('DB_HOST', 'localhost')
    db_port: int = int(os.getenv('DB_PORT', '5432'))
    db_name: str = os.getenv('DB_NAME', 'steam_insights')
    db_user: str = os.getenv('DB_USER', 'user')
    db_password: str = os.getenv('DB_PASSWORD', 'password')
    
    # Application
    app_env: str = os.getenv('APP_ENV', 'development')
    debug: bool = os.getenv('DEBUG', 'False').lower() == 'true'
    log_level: str = os.getenv('LOG_LEVEL', 'INFO')
    
    # API
    api_host: str = os.getenv('API_HOST', '0.0.0.0')
    api_port: int = int(os.getenv('API_PORT', '8000'))
    
    # Dashboard
    dashboard_port: int = int(os.getenv('DASHBOARD_PORT', '8501'))
    
    class Config:
        env_file = '.env'
        case_sensitive = False


# Global settings instance
settings = Settings()
