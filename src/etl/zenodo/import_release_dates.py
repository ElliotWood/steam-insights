"""
Import release dates from Zenodo applications.csv.
"""
import pandas as pd
from sqlalchemy import create_engine, text
from datetime import datetime
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
from config.settings import Settings

settings = Settings()
DATABASE_URL = settings.database_url
ZENODO_BASE = Path('data/zenodo_analysis/csv_data/steam_dataset_2025_csv')


def import_release_dates(resume_from=None):
    """
    Import release dates from Zenodo applications.csv.
    
    Args:
        resume_from: Steam AppID to resume from (for fault tolerance)
    """
    print("=" * 70)
    print("IMPORTING RELEASE DATES")
    print("=" * 70)
    
    apps_file = ZENODO_BASE / 'applications.csv'
    print(f"\nReading {apps_file}...")
    
    df = pd.read_csv(apps_file, usecols=['appid', 'release_date'])
    print(f"Total applications: {len(df):,}")
    
    # Filter to valid dates
    df = df[df['release_date'].notna()].copy()
    print(f"Apps with release dates: {len(df):,}")
    
    # Parse dates
    df['parsed_date'] = pd.to_datetime(
        df['release_date'],
        errors='coerce'
    )
    df = df[df['parsed_date'].notna()].copy()
    print(f"Valid date formats: {len(df):,}")
    
    # Connect to database
    engine = create_engine(DATABASE_URL)
    
    with engine.begin() as conn:
        # Get existing games
        result = conn.execute(text("SELECT steam_appid FROM games"))
        existing_games = set(r[0] for r in result)
        print(f"\nGames in database: {len(existing_games):,}")
        
        # Filter to existing games
        df_valid = df[df['appid'].isin(existing_games)].copy()
        print(f"Matching games: {len(df_valid):,}")
        
        # Get games that already have dates
        result = conn.execute(text("""
            SELECT steam_appid FROM games WHERE release_date IS NOT NULL
        """))
        has_dates = set(r[0] for r in result)
        print(f"Games with existing dates: {len(has_dates):,}")
        
        # Filter to games needing updates
        df_update = df_valid[~df_valid['appid'].isin(has_dates)].copy()
        
        # Resume support
        if resume_from:
            df_update = df_update[df_update['appid'] >= resume_from].copy()
            print(f"Resuming from AppID: {resume_from}")
        
        print(f"Games to update: {len(df_update):,}")
        
        if len(df_update) > 0:
            # Batch update with individual commits for fault tolerance
            print("\nUpdating release dates...")
            batch_size = 100
            total_updated = 0
            last_appid = None
            
            try:
                for i in range(0, len(df_update), batch_size):
                    batch = df_update.iloc[i:i + batch_size]
                    
                    for _, row in batch.iterrows():
                        try:
                            last_appid = int(row['appid'])
                            conn.execute(text("""
                                UPDATE games
                                SET release_date = :date,
                                    updated_at = :now
                                WHERE steam_appid = :appid
                            """), {
                                'appid': last_appid,
                                'date': row['parsed_date'].to_pydatetime(),
                                'now': datetime.utcnow()
                            })
                            total_updated += 1
                        except Exception as e:
                            print(f"  Error updating {last_appid}: {e}")
                            continue
                    
                    # Commit every batch
                    conn.commit()
                    
                    if total_updated % 1000 == 0 and total_updated > 0:
                        print(f"  Progress: {total_updated:,}/{len(df_update):,}...")
                
            except KeyboardInterrupt:
                print(f"\n\nInterrupted at AppID {last_appid}")
                print(f"Resume with: resume_from={last_appid}")
                conn.commit()  # Save progress
                return
            
            print(f"\nUpdated {total_updated:,} games")
        
        # Final stats
        result = conn.execute(text("""
            SELECT COUNT(*) as total,
                   COUNT(release_date) as with_dates
            FROM games
        """))
        row = result.fetchone()
        
        print("\n" + "=" * 70)
        print("FINAL RESULTS")
        print("=" * 70)
        print(f"Total games: {row[0]:,}")
        print(f"Games with release dates: {row[1]:,}")
        print(f"Coverage: {row[1] / row[0] * 100:.1f}%")


if __name__ == '__main__':
    import sys
    
    # Support resume from command line
    resume_from = None
    if len(sys.argv) > 1:
        try:
            resume_from = int(sys.argv[1])
            print(f"Resuming from AppID: {resume_from}\n")
        except ValueError:
            print("Usage: python import_release_dates.py [resume_from_appid]")
            sys.exit(1)
    
    import_release_dates(resume_from=resume_from)
