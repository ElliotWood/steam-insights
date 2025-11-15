"""
Bulk import utilities for Steam Insights.
"""

import time
import logging
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

from src.etl.game_importer import GameDataImporter
from src.models.database import Game

logger = logging.getLogger(__name__)


class BulkImporter:
    """Handle bulk import operations."""
    
    def __init__(self, db: Session):
        """Initialize with database session."""
        self.db = db
        self.importer = GameDataImporter(db)
        self.results = {
            'success': [],
            'failed': [],
            'skipped': [],
            'total': 0
        }
    
    def import_games_batch(
        self,
        app_ids: List[int],
        delay: float = 1.0,
        skip_existing: bool = True,
        update_stats: bool = True
    ) -> Dict[str, Any]:
        """
        Import multiple games in batch.
        
        Args:
            app_ids: List of Steam App IDs
            delay: Delay between imports (seconds) to respect rate limits
            skip_existing: Skip games already in database
            update_stats: Whether to update player stats after import
            
        Returns:
            Dictionary with import results
        """
        self.results = {
            'success': [],
            'failed': [],
            'skipped': [],
            'total': len(app_ids)
        }
        
        for idx, app_id in enumerate(app_ids, 1):
            logger.info(f"Processing {idx}/{len(app_ids)}: App ID {app_id}")
            
            try:
                # Check if exists
                if skip_existing:
                    existing = self.db.query(Game).filter(
                        Game.steam_appid == app_id
                    ).first()
                    if existing:
                        self.results['skipped'].append({
                            'app_id': app_id,
                            'name': existing.name,
                            'reason': 'Already exists'
                        })
                        logger.info(f"Skipping {app_id}: already exists")
                        continue
                
                # Import game
                game = self.importer.import_game(app_id)
                
                if game:
                    self.results['success'].append({
                        'app_id': app_id,
                        'name': game.name,
                        'genres': [g.name for g in game.genres]
                    })
                    logger.info(f"Successfully imported: {game.name}")
                    
                    # Update stats if requested
                    if update_stats:
                        try:
                            stats = self.importer.update_player_stats(app_id)
                            if stats:
                                logger.info(f"Updated stats: {stats.current_players} players")
                        except Exception as e:
                            logger.warning(f"Could not update stats for {app_id}: {e}")
                else:
                    self.results['failed'].append({
                        'app_id': app_id,
                        'reason': 'Import returned None'
                    })
                    logger.error(f"Failed to import {app_id}")
                
                # Rate limiting
                if idx < len(app_ids):
                    time.sleep(delay)
                
            except Exception as e:
                self.results['failed'].append({
                    'app_id': app_id,
                    'reason': str(e)
                })
                logger.error(f"Error importing {app_id}: {e}")
        
        return self.results
    
    def import_top_games(
        self,
        limit: int = 50,
        delay: float = 1.0
    ) -> Dict[str, Any]:
        """
        Import top games from Steam.
        
        This uses a predefined list of popular games since Steam doesn't
        provide a "top games" endpoint directly.
        
        Args:
            limit: Maximum number of games to import
            delay: Delay between imports
            
        Returns:
            Dictionary with import results
        """
        # Popular Steam games (as of 2024)
        popular_app_ids = [
            730,     # Counter-Strike 2
            570,     # Dota 2
            440,     # Team Fortress 2
            252490,  # Rust
            1172470, # Apex Legends
            271590,  # Grand Theft Auto V
            578080,  # PUBG
            1203220, # Naraka: Bladepoint
            413150,  # Stardew Valley
            1938090, # Call of Duty
            292030,  # The Witcher 3
            1245620, # Elden Ring
            1086940, # Baldur's Gate 3
            359550,  # Rainbow Six Siege
            107410,  # Arma 3
            1599340, # Ready or Not
            892970,  # Valheim
            582010,  # Monster Hunter: World
            1145360, # Hades
            427520,  # Factorio
            381210,  # Dead by Daylight
            346110,  # ARK: Survival Evolved
            393380,  # Squad
            255710,  # Cities: Skylines
            281990,  # Stellaris
            1091500, # Cyberpunk 2077
            400,     # Portal 2
            620,     # Portal
            220,     # Half-Life 2
            550,     # Left 4 Dead 2
            72850,   # The Elder Scrolls V: Skyrim
            8930,    # Sid Meier's Civilization V
            289070,  # Sid Meier's Civilization VI
            236390,  # War Thunder
            230410,  # Warframe
            304930,  # Unturned
            594650,  # Hunt: Showdown
            1326470, # Sons of The Forest
            367520,  # Hollow Knight
            648800,  # Raft
            218620,  # PAYDAY 2
            105600,  # Terraria
            244850,  # Space Engineers
            322330,  # Don't Starve Together
            774361,  # GTFO
            242760,  # The Forest
            493520,  # Grounded
            1818750, # Palworld
            976730,  # Halo Infinite
            1811260  # TITANFALL 2
        ]
        
        # Limit to requested amount
        app_ids_to_import = popular_app_ids[:limit]
        
        return self.import_games_batch(
            app_ids_to_import,
            delay=delay,
            skip_existing=True,
            update_stats=True
        )
    
    def import_by_genre(
        self,
        genre_name: str,
        app_ids: List[int],
        delay: float = 1.0
    ) -> Dict[str, Any]:
        """
        Import games for a specific genre.
        
        Args:
            genre_name: Genre to tag games with
            app_ids: List of App IDs in this genre
            delay: Delay between imports
            
        Returns:
            Dictionary with import results
        """
        logger.info(f"Importing {len(app_ids)} games for genre: {genre_name}")
        return self.import_games_batch(app_ids, delay=delay, update_stats=False)
    
    def get_import_report(self) -> str:
        """
        Get formatted import report.
        
        Returns:
            Human-readable report string
        """
        report = f"""
Import Report
=============
Total Processed: {self.results['total']}
Successful: {len(self.results['success'])}
Failed: {len(self.results['failed'])}
Skipped: {len(self.results['skipped'])}

Success Rate: {len(self.results['success']) / max(self.results['total'], 1) * 100:.1f}%
"""
        
        if self.results['failed']:
            report += "\nFailed Imports:\n"
            for fail in self.results['failed'][:10]:  # Show first 10
                report += f"  - App ID {fail['app_id']}: {fail['reason']}\n"
        
        return report
