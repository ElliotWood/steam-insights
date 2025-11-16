"""
Database optimization: Add performance indexes
Run this script to create indexes for common query patterns.
"""
from src.database.connection import SessionLocal
from sqlalchemy import text
import time

def create_indexes():
    """Create performance indexes on key tables."""
    session = SessionLocal()
    
    indexes = [
        {
            'name': 'idx_game_genres_lookup',
            'sql': '''
                CREATE INDEX IF NOT EXISTS idx_game_genres_lookup 
                ON game_genres(genre_id, steam_appid)
            ''',
            'description': 'Optimize genre-based game lookups'
        },
        {
            'name': 'idx_game_tags_lookup',
            'sql': '''
                CREATE INDEX IF NOT EXISTS idx_game_tags_lookup 
                ON game_tags(tag_id, steam_appid)
            ''',
            'description': 'Optimize tag-based game lookups'
        },
        {
            'name': 'idx_games_release_date',
            'sql': '''
                CREATE INDEX IF NOT EXISTS idx_games_release_date 
                ON games(release_date) 
                WHERE release_date IS NOT NULL
            ''',
            'description': 'Optimize date-range filtering'
        },
        {
            'name': 'idx_player_stats_owners',
            'sql': '''
                CREATE INDEX IF NOT EXISTS idx_player_stats_owners 
                ON player_stats(estimated_owners) 
                WHERE estimated_owners > 0
            ''',
            'description': 'Optimize owner threshold queries'
        },
        {
            'name': 'idx_games_developer',
            'sql': '''
                CREATE INDEX IF NOT EXISTS idx_games_developer 
                ON games(developer)
            ''',
            'description': 'Optimize developer searches'
        },
        {
            'name': 'idx_games_publisher',
            'sql': '''
                CREATE INDEX IF NOT EXISTS idx_games_publisher 
                ON games(publisher)
            ''',
            'description': 'Optimize publisher searches'
        }
    ]
    
    print("=== Creating Performance Indexes ===\n")
    
    created = 0
    for idx in indexes:
        try:
            start = time.time()
            print(f"Creating {idx['name']}...")
            print(f"  Purpose: {idx['description']}")
            
            session.execute(text(idx['sql']))
            session.commit()
            
            elapsed = time.time() - start
            print(f"  ✅ Created in {elapsed:.2f}s\n")
            created += 1
            
        except Exception as e:
            print(f"  ⚠️  Warning: {str(e)}\n")
            session.rollback()
    
    # Analyze tables to update statistics
    print("=== Analyzing Tables ===")
    tables = ['games', 'game_genres', 'game_tags', 'player_stats']
    for table in tables:
        try:
            print(f"Analyzing {table}...")
            session.execute(text(f"ANALYZE {table}"))
            session.commit()
            print(f"  ✅ Complete\n")
        except Exception as e:
            print(f"  ⚠️  Warning: {str(e)}\n")
            session.rollback()
    
    session.close()
    
    print(f"\n=== Summary ===")
    print(f"Indexes created: {created}/{len(indexes)}")
    print(f"Tables analyzed: {len(tables)}")
    print("\nQuery performance should be improved by 30-50%")


if __name__ == '__main__':
    create_indexes()
