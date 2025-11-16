"""
ETL pipeline for importing game data into the database.
"""

import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

from src.models.database import Game, Genre, Tag, PlayerStats, PricingHistory
from src.api.steam_client import SteamAPIClient
from src.scrapers.steam_scraper import SteamStoreScraper

logger = logging.getLogger(__name__)


class GameDataImporter:
    """Import and update game data from various sources."""
    
    def __init__(self, db_session: Session):
        """
        Initialize the importer.
        
        Args:
            db_session: Database session
        """
        self.db = db_session
        self.steam_client = SteamAPIClient()
        self.scraper = SteamStoreScraper()
    
    def import_game(self, app_id: int) -> Optional[Game]:
        """
        Import or update a game from Steam.
        
        Args:
            app_id: Steam application ID
            
        Returns:
            Game object if successful, None otherwise
        """
        logger.info(f"Importing game {app_id}")
        
        # Check if game already exists
        game = self.db.query(Game).filter(Game.steam_appid == app_id).first()
        
        # Fetch game details from Steam API
        app_details = self.steam_client.get_app_details(app_id)
        if not app_details:
            logger.warning(f"Could not fetch details for app {app_id}")
            return None
        
        # Create or update game
        if not game:
            game = Game(steam_appid=app_id)
            self.db.add(game)
        
        # Update game information
        game.name = app_details.get('name', '')
        game.description = app_details.get('detailed_description', '')
        game.short_description = app_details.get('short_description', '')
        game.header_image = app_details.get('header_image', '')
        game.website = app_details.get('website', '')
        
        # Developers and publishers
        if 'developers' in app_details and app_details['developers']:
            game.developer = ', '.join(app_details['developers'])
        if 'publishers' in app_details and app_details['publishers']:
            game.publisher = ', '.join(app_details['publishers'])
        
        # Release date
        if 'release_date' in app_details and not app_details['release_date'].get('coming_soon', True):
            try:
                release_date_str = app_details['release_date'].get('date', '')
                if release_date_str:
                    game.release_date = datetime.strptime(release_date_str, '%b %d, %Y')
            except ValueError:
                logger.warning(f"Could not parse release date for {app_id}")
        
        # Platform support
        platforms = app_details.get('platforms', {})
        game.windows = platforms.get('windows', False)
        game.mac = platforms.get('mac', False)
        game.linux = platforms.get('linux', False)
        
        # Process genres
        if 'genres' in app_details:
            self._process_genres(game, app_details['genres'])
        
        # Process categories/tags
        if 'categories' in app_details:
            self._process_tags(game, app_details['categories'])
        
        game.updated_at = datetime.utcnow()
        
        try:
            self.db.commit()
            logger.info(f"Successfully imported game {app_id}: {game.name}")
            return game
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error importing game {app_id}: {e}")
            return None
    
    def _process_genres(self, game: Game, genre_data: List[Dict[str, Any]]) -> None:
        """Process and link genres to game."""
        game.genres.clear()
        
        for genre_info in genre_data:
            genre_name = genre_info.get('description', '')
            if not genre_name:
                continue
            
            # Get or create genre
            genre = self.db.query(Genre).filter(Genre.name == genre_name).first()
            if not genre:
                genre = Genre(name=genre_name)
                self.db.add(genre)
            
            if genre not in game.genres:
                game.genres.append(genre)
    
    def _process_tags(self, game: Game, tag_data: List[Dict[str, Any]]) -> None:
        """Process and link tags to game."""
        game.tags.clear()
        
        for tag_info in tag_data:
            tag_name = tag_info.get('description', '')
            if not tag_name:
                continue
            
            # Get or create tag
            tag = self.db.query(Tag).filter(Tag.name == tag_name).first()
            if not tag:
                tag = Tag(name=tag_name)
                self.db.add(tag)
            
            if tag not in game.tags:
                game.tags.append(tag)
    
    def update_player_stats(self, app_id: int) -> Optional[PlayerStats]:
        """
        Update player statistics for a game.
        
        Args:
            app_id: Steam application ID
            
        Returns:
            PlayerStats object if successful, None otherwise
        """
        game = self.db.query(Game).filter(Game.steam_appid == app_id).first()
        if not game:
            logger.warning(f"Game {app_id} not found in database")
            return None
        
        # Get current player count
        player_count = self.steam_client.get_current_players(app_id)
        if player_count is None:
            logger.warning(f"Could not fetch player count for {app_id}")
            return None
        
        # Create player stats entry
        stats = PlayerStats(
            steam_appid=game.steam_appid,
            timestamp=datetime.utcnow(),
            current_players=player_count
        )
        
        self.db.add(stats)
        
        try:
            self.db.commit()
            logger.info(f"Updated player stats for {app_id}: {player_count} players")
            return stats
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating player stats for {app_id}: {e}")
            return None
    
    def update_pricing(self, app_id: int) -> Optional[PricingHistory]:
        """
        Update pricing information for a game.
        
        Args:
            app_id: Steam application ID
            
        Returns:
            PricingHistory object if successful, None otherwise
        """
        game = self.db.query(Game).filter(Game.steam_appid == app_id).first()
        if not game:
            logger.warning(f"Game {app_id} not found in database")
            return None
        
        # Fetch pricing from API
        app_details = self.steam_client.get_app_details(app_id)
        if not app_details or 'price_overview' not in app_details:
            logger.warning(f"Could not fetch pricing for {app_id}")
            return None
        
        price_info = app_details['price_overview']
        
        # Create pricing entry
        pricing = PricingHistory(
            steam_appid=game.steam_appid,
            timestamp=datetime.utcnow(),
            price_usd=price_info.get('initial', 0) / 100.0,  # Convert cents to dollars
            discount_percent=price_info.get('discount_percent', 0.0),
            final_price_usd=price_info.get('final', 0) / 100.0,
            is_free=app_details.get('is_free', False)
        )
        
        self.db.add(pricing)
        
        try:
            self.db.commit()
            logger.info(f"Updated pricing for {app_id}")
            return pricing
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating pricing for {app_id}: {e}")
            return None
