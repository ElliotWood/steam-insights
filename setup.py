#!/usr/bin/env python3
"""
Setup script for Steam Insights.
Initialize database and perform initial setup.
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.database.connection import init_db
from src.utils.logging_config import setup_logging
from config.settings import settings

def main():
    """Main setup function."""
    print("🎮 Steam Insights Setup")
    print("=" * 50)
    
    # Setup logging
    setup_logging(level=settings.log_level)
    
    # Initialize database
    print("\n📊 Initializing database...")
    try:
        init_db()
        print("✅ Database initialized successfully!")
        
        if settings.database_url.startswith('sqlite'):
            print(f"   Using SQLite: {settings.database_url.replace('sqlite:///', '')}")
        else:
            print(f"   Using database: {settings.database_url}")
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        return 1
    
    # Check Steam API key
    print("\n🔑 Checking Steam API configuration...")
    if settings.steam_api_key:
        print("✅ Steam API key configured")
    else:
        print("⚠️  Steam API key not configured")
        print("   Some features may not work without an API key.")
        print("   Get a free key from: https://steamcommunity.com/dev")
        print("   Add it to your .env file: STEAM_API_KEY=your_key_here")
    
    print("\n" + "=" * 50)
    print("Setup complete! 🎉")
    print("\nNext steps:")
    print("1. Start the dashboard: streamlit run src/dashboard/app.py")
    print("2. Or start the API: python -m uvicorn src.api.main:app --reload")
    print("\nHappy analyzing! 📈")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
