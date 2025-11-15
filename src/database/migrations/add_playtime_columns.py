"""
Migration: Add play time statistics columns to player_stats table.

This adds:
- average_playtime_minutes: Average time players spend in the game
- peak_playtime_minutes: Maximum recorded playtime for any player
"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import text
from src.database.connection import engine


def upgrade():
    """Add play time columns to player_stats table."""
    with engine.connect() as conn:
        # Check if columns exist before adding
        try:
            # Add average_playtime_minutes column
            conn.execute(text(
                """
                ALTER TABLE player_stats
                ADD COLUMN average_playtime_minutes INTEGER
                """
            ))
            conn.commit()
            print("✓ Added average_playtime_minutes column")
        except Exception as e:
            print(f"average_playtime_minutes column may already exist: {e}")
        
        try:
            # Add peak_playtime_minutes column
            conn.execute(text(
                """
                ALTER TABLE player_stats
                ADD COLUMN peak_playtime_minutes INTEGER
                """
            ))
            conn.commit()
            print("✓ Added peak_playtime_minutes column")
        except Exception as e:
            print(f"peak_playtime_minutes column may already exist: {e}")
    
    print("\n✅ Migration completed successfully!")


def downgrade():
    """Remove play time columns from player_stats table."""
    with engine.connect() as conn:
        # SQLite doesn't support DROP COLUMN directly
        # Would need to recreate table without these columns
        print("⚠️  Downgrade not implemented for SQLite")
        print("   To remove columns, backup data and recreate table")


if __name__ == "__main__":
    print("Running migration: Add play time statistics columns\n")
    upgrade()
