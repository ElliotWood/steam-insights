"""
Example script demonstrating how to use Steam Insights programmatically.

This script shows how to:
1. Import a game
2. Query game data
3. Get player statistics
4. Analyze data
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database.connection import get_db, init_db
from src.models.database import Game, Genre, PlayerStats
from src.etl.game_importer import GameDataImporter
from src.api.steam_client import SteamAPIClient


def main():
    """Main example function."""
    print("🎮 Steam Insights - Example Usage")
    print("=" * 50)
    
    # Initialize database
    print("\n1. Initializing database...")
    init_db()
    print("   ✅ Database initialized")
    
    # Get database session
    db = next(get_db())
    
    # Create importer and client
    importer = GameDataImporter(db)
    client = SteamAPIClient()
    
    # Example 1: Import a popular game
    print("\n2. Importing Counter-Strike 2 (App ID: 730)...")
    try:
        game = importer.import_game(730)
        if game:
            print(f"   ✅ Successfully imported: {game.name}")
            print(f"      Developer: {game.developer}")
            print(f"      Publisher: {game.publisher}")
            print(f"      Genres: {', '.join([g.name for g in game.genres])}")
        else:
            print("   ⚠️  Game already exists or could not be imported")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Example 2: Update player statistics
    print("\n3. Fetching current player count...")
    try:
        stats = importer.update_player_stats(730)
        if stats:
            print(f"   ✅ Current players: {stats.current_players:,}")
        else:
            print("   ⚠️  Could not fetch player stats")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Close database connection
    db.close()
    
    print("\n" + "=" * 50)
    print("Example completed! 🎉")
    print("\nNext steps:")
    print("- Start the dashboard: streamlit run src/dashboard/app.py")
    print("- Start the API: python -m uvicorn src.api.main:app --reload")


if __name__ == "__main__":
    main()
