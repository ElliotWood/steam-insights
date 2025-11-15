"""
Import ALL Steam games using SteamSpy API with pagination.
Fetches 50,000+ games by requesting multiple pages.
"""
from src.database.connection import get_db
from src.utils.kaggle_importer import KaggleDatasetImporter
from datetime import datetime
import logging
import requests
import time

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def fetch_all_steamspy_games():
    """Fetch all games from SteamSpy using pagination."""
    all_games = {}
    page = 0
    
    logger.info("📥 Fetching games from SteamSpy (paginated)...")
    
    while True:
        try:
            url = f"https://steamspy.com/api.php?request=all&page={page}"
            response = requests.get(url, timeout=60)
            response.raise_for_status()
            data = response.json()
            
            if not data or len(data) == 0:
                break
            
            all_games.update(data)
            logger.info(f"Page {page}: +{len(data):,} games (Total: {len(all_games):,})")
            page += 1
            time.sleep(1)  # Rate limiting
            
        except Exception as e:
            logger.error(f"Error on page {page}: {e}")
            break
    
    return all_games


def main():
    """Import all Steam games with progress tracking."""
    start_time = datetime.now()
    
    logger.info("=" * 60)
    logger.info("IMPORTING ALL STEAM GAMES (50K+)")
    logger.info("=" * 60)
    
    # Fetch all games with pagination
    all_games = fetch_all_steamspy_games()
    
    if not all_games:
        logger.error("❌ No games fetched")
        return
    
    logger.info(f"✓ Retrieved {len(all_games):,} total games")
    
    # Get database session
    db = next(get_db())
    importer = KaggleDatasetImporter(db)
    
    # Process in batches
    batch_size = 1000
    total = len(all_games)
    items = list(all_games.items())
    
    try:
        for i in range(0, total, batch_size):
            batch_num = (i // batch_size) + 1
            batch = dict(items[i:i + batch_size])
            
            logger.info(
                f"Batch {batch_num}: "
                f"Games {i+1:,}-{min(i+batch_size, total):,}"
            )
            
            for app_id, game_data in batch.items():
                try:
                    importer._import_steamspy_game(int(app_id), game_data)
                except Exception:
                    pass
            
            db.commit()
        
        # Final report
        duration = (datetime.now() - start_time).total_seconds()
        imported = importer.import_stats['games_imported']
        updated = importer.import_stats['games_updated']
        
        logger.info("\n" + "=" * 60)
        logger.info("✅ IMPORT COMPLETE!")
        logger.info(f"Duration: {duration/60:.1f} min ({duration:.0f}s)")
        logger.info(f"Imported: {imported:,} | Updated: {updated:,}")
        logger.info(f"Total: {imported + updated:,} games")
        logger.info("=" * 60)
        logger.info("🎮 Refresh http://localhost:8502")
        
    except KeyboardInterrupt:
        logger.warning("\n⚠️  Interrupted - saving progress")
        db.commit()
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
