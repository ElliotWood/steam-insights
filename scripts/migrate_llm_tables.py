"""
Database migration script to add LLM enrichment tables.
Run this to add game_enrichments and batch_processing_jobs tables.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import create_engine
from src.models.database import Base, GameEnrichment, BatchProcessingJob
from config.settings import Settings


def run_migration():
    """Create new tables for LLM enrichment."""
    print("Starting database migration...")
    settings = Settings()
    print(f"Database URL: {settings.database_url}")
    
    # Create engine
    engine = create_engine(settings.database_url)
    
    # Create only the new tables
    print("\nCreating tables:")
    print("- game_enrichments")
    print("- batch_processing_jobs")
    
    # Create tables
    GameEnrichment.__table__.create(engine, checkfirst=True)
    BatchProcessingJob.__table__.create(engine, checkfirst=True)
    
    print("\n✅ Migration completed successfully!")
    print("\nNew tables added:")
    print("  - game_enrichments: Stores LLM-extracted game insights")
    print("  - batch_processing_jobs: Tracks batch enrichment jobs")

if __name__ == "__main__":
    try:
        run_migration()
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        sys.exit(1)
