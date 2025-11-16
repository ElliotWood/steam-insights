"""Import genre associations from Zenodo dataset."""
import pandas as pd
from src.database.connection import SessionLocal
from src.models.database import Game
from sqlalchemy import text
from datetime import datetime

def import_genre_associations(resume_from=None):
    """
    Import genre associations from Zenodo dataset.
    
    Args:
        resume_from: Batch index to resume from (for fault tolerance)
    """
    
    # Load Zenodo genre associations
    print("=== Loading Zenodo Genre Associations ===")
    csv_path = (
        r"c:\repo\steam-insights\data\zenodo_analysis\csv_data"
        r"\steam_dataset_2025_csv\application_genres.csv"
    )
    df = pd.read_csv(csv_path)
    print(f"Total associations in Zenodo: {len(df):,}")
    print(f"Unique games: {df['appid'].nunique():,}")
    print(f"Unique genre IDs: {df['genre_id'].nunique()}")
    
    # Database connection
    session = SessionLocal()
    
    try:
        # Get all database game IDs
        print("\n=== Loading Database Game IDs ===")
        db_games_result = session.execute(
            text('SELECT steam_appid FROM games')
        ).fetchall()
        db_game_ids = set(row[0] for row in db_games_result)
        print(f"Games in database: {len(db_game_ids):,}")
        
        # Get valid genre IDs from database
        valid_genre_ids = set(
            row[0] for row in session.execute(text("SELECT id FROM genres")).fetchall()
        )
        print(f"Valid genre IDs in database: {len(valid_genre_ids)}")
        
        # Filter to only games in our database AND valid genre IDs
        print("\n=== Filtering to Database Games and Valid Genres ===")
        df_filtered = df[df['appid'].isin(db_game_ids) & df['genre_id'].isin(valid_genre_ids)]
        print(f"Associations for database games: {len(df_filtered):,}")
        print(f"Games with associations: {df_filtered['appid'].nunique():,}")
        print(f"Coverage: {df_filtered['appid'].nunique() / len(db_game_ids) * 100:.1f}%")
        
        # Get existing associations
        print("\n=== Checking Existing Associations ===")
        existing = session.execute(text(
            'SELECT steam_appid, genre_id FROM game_genres'
        )).fetchall()
        existing_set = set(existing)
        print(f"Existing associations: {len(existing_set):,}")
        
        # Prepare new associations
        print("\n=== Preparing New Associations ===")
        new_associations = []
        for _, row in df_filtered.iterrows():
            pair = (int(row['appid']), int(row['genre_id']))
            if pair not in existing_set:
                new_associations.append(pair)
        
        print(f"New associations to insert: {len(new_associations):,}")
        
        if not new_associations:
            print("No new associations to insert!")
            session.close()
            return
        
        # Insert in batches with fault tolerance
        print("\n=== Inserting New Associations ===")
        batch_size = 5000
        total_inserted = 0
        start_batch = resume_from if resume_from else 0
        
        if start_batch > 0:
            print(f"Resuming from batch {start_batch}")
        
        try:
            for i in range(start_batch, len(new_associations), batch_size):
                batch = new_associations[i:i + batch_size]
                batch_num = i // batch_size
                
                # Build VALUES clause
                values = ','.join(
                    f"({appid}, {genre_id})" 
                    for appid, genre_id in batch
                )
                
                query = text(f"""
                    INSERT INTO game_genres (steam_appid, genre_id)
                    VALUES {values}
                    ON CONFLICT (steam_appid, genre_id) DO NOTHING
                """)
                
                try:
                    session.execute(query)
                    session.commit()
                    total_inserted += len(batch)
                    
                    if total_inserted % 50000 == 0:
                        print(f"Processed {total_inserted:,} associations...")
                        
                except Exception as e:
                    print(f"Error in batch {batch_num}: {e}")
                    session.rollback()
                    continue
                    
        except KeyboardInterrupt:
            print(f"\n\nInterrupted at batch {i // batch_size}")
            print(f"Resume with: resume_from={i}")
            session.commit()
            session.close()
            return


        
        print(f"\nTotal inserted: {total_inserted:,}")
        
        # Verify results
        print("\n=== Verification ===")
        final_count = session.execute(
            text('SELECT COUNT(*) FROM game_genres')
        ).scalar()
        final_games = session.execute(
            text('SELECT COUNT(DISTINCT steam_appid) FROM game_genres')
        ).scalar()
        total_games = session.execute(
            text('SELECT COUNT(*) FROM games')
        ).scalar()
        
        print(f"Total genre associations: {final_count:,}")
        print(f"Games with genres: {final_games:,}")
        print(f"Coverage: {final_games / total_games * 100:.1f}%")
        
    except Exception as e:
        print(f"\nError: {e}")
        session.rollback()
        raise
    finally:
        session.close()

if __name__ == '__main__':
    import sys
    
    # Support resume from command line
    resume_from = None
    if len(sys.argv) > 1:
        try:
            resume_from = int(sys.argv[1])
            print(f"Resuming from batch: {resume_from}\n")
        except ValueError:
            print("Usage: python import_genre_associations.py [resume_batch]")
            sys.exit(1)
    
    start_time = datetime.now()
    import_genre_associations(resume_from=resume_from)
    duration = (datetime.now() - start_time).total_seconds()
    print(f"\nCompleted in {duration:.1f} seconds")
