"""
Import tag associations from Zenodo using name-based matching.
Fixes the ID mismatch issue between Zenodo categories and database tags.
"""
import pandas as pd
from sqlalchemy import create_engine, text
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
from config.settings import Settings

settings = Settings()
DATABASE_URL = settings.database_url
ZENODO_BASE = Path('data/zenodo_analysis/csv_data/steam_dataset_2025_csv')


def import_tag_associations_by_name(resume_from=None):
    """
    Import tag associations using name-based matching.
    
    Args:
        resume_from: Batch index to resume from (for fault tolerance)
    """
    print("=" * 70)
    print("IMPORTING TAG ASSOCIATIONS (NAME-BASED)")
    print("=" * 70)
    
    # Load categories
    cat_file = ZENODO_BASE / 'categories.csv'
    print(f"\nReading {cat_file}...")
    categories_df = pd.read_csv(cat_file)
    print(f"Zenodo categories: {len(categories_df):,}")
    
    # Load associations
    assoc_file = ZENODO_BASE / 'application_categories.csv'
    print(f"Reading {assoc_file}...")
    assocs_df = pd.read_csv(assoc_file)
    print(f"Total associations: {len(assocs_df):,}")
    print(f"Unique apps: {assocs_df['appid'].nunique():,}")
    
    # Connect to database
    engine = create_engine(DATABASE_URL)
    
    with engine.begin() as conn:
        # Get existing games
        result = conn.execute(text("SELECT steam_appid FROM games"))
        existing_games = set(r[0] for r in result)
        print(f"\nGames in database: {len(existing_games):,}")
        
        # Get database tags with their names
        result = conn.execute(text("""
            SELECT id, name FROM tags WHERE is_user_tag = false
        """))
        db_tags = {row[1]: row[0] for row in result}
        print(f"Category tags in database: {len(db_tags)}")
        
        # Create mapping: Zenodo category_id -> category name -> db tag_id
        print("\nBuilding name-based mapping...")
        category_to_tag = {}
        unmatched_categories = []
        
        for _, row in categories_df.iterrows():
            zenodo_id = int(row['id'])
            zenodo_name = str(row['name']).strip()
            
            # Try exact match first
            if zenodo_name in db_tags:
                category_to_tag[zenodo_id] = db_tags[zenodo_name]
            else:
                # Try case-insensitive match
                zenodo_lower = zenodo_name.lower()
                matched = False
                for db_name, db_id in db_tags.items():
                    if db_name.lower() == zenodo_lower:
                        category_to_tag[zenodo_id] = db_id
                        matched = True
                        break
                
                if not matched:
                    unmatched_categories.append(
                        (zenodo_id, zenodo_name)
                    )
        
        print(f"Matched categories: {len(category_to_tag)}")
        print(f"Unmatched categories: {len(unmatched_categories)}")
        if len(unmatched_categories) > 0 and len(unmatched_categories) <= 20:
            print("Unmatched category names:")
            for zid, name in unmatched_categories[:20]:
                print(f"  {zid}: {name}")
        
        # Map associations using the category mapping
        print("\nMapping associations...")
        assocs_df['mapped_tag_id'] = assocs_df['category_id'].map(
            category_to_tag
        )
        
        # Filter to valid associations
        valid_assocs = assocs_df[
            assocs_df['appid'].isin(existing_games) &
            assocs_df['mapped_tag_id'].notna()
        ].copy()
        
        valid_assocs['mapped_tag_id'] = valid_assocs[
            'mapped_tag_id'
        ].astype(int)
        
        print(f"Valid associations: {len(valid_assocs):,}")
        print(f"Unique apps: {valid_assocs['appid'].nunique():,}")
        coverage = valid_assocs['appid'].nunique() / len(existing_games)
        print(f"Coverage: {coverage * 100:.1f}%")
        
        if len(valid_assocs) == 0:
            print("\nERROR: No valid associations to import!")
            return
        
        # Get existing associations
        result = conn.execute(text(
            "SELECT steam_appid, tag_id FROM game_tags"
        ))
        existing_assocs = set((r[0], r[1]) for r in result)
        print(f"\nExisting associations: {len(existing_assocs):,}")
        
        # Prepare new associations
        new_assocs = []
        for _, row in valid_assocs.iterrows():
            key = (int(row['appid']), int(row['mapped_tag_id']))
            if key not in existing_assocs:
                new_assocs.append({
                    'steam_appid': key[0],
                    'tag_id': key[1]
                })
        
        print(f"New associations to insert: {len(new_assocs):,}")
        
        if len(new_assocs) > 0:
            # Batch insert with fault tolerance
            batch_size = 5000
            total_inserted = 0
            start_batch = resume_from if resume_from else 0
            
            if start_batch > 0:
                print(f"\nResuming from batch {start_batch}")
            
            print("\nInserting associations...")
            
            try:
                for i in range(start_batch, len(new_assocs), batch_size):
                    batch = new_assocs[i:i + batch_size]
                    batch_num = i // batch_size
                    
                    batch_inserted = 0
                    for assoc in batch:
                        try:
                            conn.execute(text("""
                                INSERT INTO game_tags (steam_appid, tag_id)
                                VALUES (:steam_appid, :tag_id)
                            """), assoc)
                            batch_inserted += 1
                        except Exception:
                            pass  # Skip duplicates
                    
                    # Commit after each batch
                    conn.commit()
                    total_inserted += batch_inserted
                    
                    if total_inserted % 50000 == 0 and total_inserted > 0:
                        print(f"  Progress: {total_inserted:,}...")
                        
            except KeyboardInterrupt:
                print(f"\n\nInterrupted at batch {i // batch_size}")
                print(f"Resume with: resume_from={i}")
                conn.commit()
                return
            
            print(f"\nInserted {total_inserted:,} new associations")
        
        # Final verification
        result = conn.execute(text("""
            SELECT COUNT(*) as total,
                   COUNT(DISTINCT steam_appid) as unique_apps
            FROM game_tags
        """))
        row = result.fetchone()
        
        print("\n" + "=" * 70)
        print("FINAL RESULTS")
        print("=" * 70)
        print(f"Total tag associations: {row[0]:,}")
        print(f"Games with tags: {row[1]:,}")
        final_coverage = row[1] / len(existing_games) * 100
        print(f"Coverage: {final_coverage:.1f}%")




if __name__ == '__main__':
    import sys
    
    # Support resume from command line
    resume_from = None
    if len(sys.argv) > 1:
        try:
            resume_from = int(sys.argv[1])
            print(f"Resuming from batch: {resume_from}\n")
        except ValueError:
            print("Usage: python import_tag_associations.py [resume_batch]")
            sys.exit(1)
    
    import_tag_associations_by_name(resume_from=resume_from)
