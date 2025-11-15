"""
Data export utilities for Steam Insights.
"""

import pandas as pd
import json
from typing import List, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session

from src.models.database import Game, Genre, PlayerStats, PricingHistory


class DataExporter:
    """Handle data export in various formats."""
    
    def __init__(self, db: Session):
        """Initialize with database session."""
        self.db = db
    
    def export_games_to_csv(self, filters: Dict[str, Any] = None) -> pd.DataFrame:
        """
        Export games to CSV format.
        
        Args:
            filters: Optional filters (genre, release_date, etc.)
            
        Returns:
            DataFrame ready for CSV export
        """
        query = self.db.query(Game)
        
        # Apply filters
        if filters:
            if 'genre' in filters:
                query = query.join(Game.genres).filter(Genre.name == filters['genre'])
            if 'developer' in filters and filters['developer']:
                query = query.filter(Game.developer.ilike(f"%{filters['developer']}%"))
            if 'min_date' in filters and filters['min_date']:
                query = query.filter(Game.release_date >= filters['min_date'])
        
        games = query.all()
        
        # Build data
        data = []
        for game in games:
            data.append({
                'Steam App ID': game.steam_appid,
                'Name': game.name,
                'Developer': game.developer or 'Unknown',
                'Publisher': game.publisher or 'Unknown',
                'Release Date': game.release_date.strftime('%Y-%m-%d') if game.release_date else 'N/A',
                'Genres': ', '.join([g.name for g in game.genres]) if game.genres else 'N/A',
                'Tags': ', '.join([t.name for t in game.tags[:5]]) if game.tags else 'N/A',
                'Windows': 'Yes' if game.windows else 'No',
                'Mac': 'Yes' if game.mac else 'No',
                'Linux': 'Yes' if game.linux else 'No',
                'Description': (game.short_description or '')[:200] if game.short_description else 'N/A',
                'Added Date': game.created_at.strftime('%Y-%m-%d %H:%M') if game.created_at else 'N/A'
            })
        
        return pd.DataFrame(data)
    
    def export_player_stats_to_csv(
        self,
        app_id: int = None,
        start_date: datetime = None,
        end_date: datetime = None
    ) -> pd.DataFrame:
        """
        Export player statistics to CSV.
        
        Args:
            app_id: Optional Steam App ID to filter
            start_date: Optional start date
            end_date: Optional end date
            
        Returns:
            DataFrame ready for CSV export
        """
        query = self.db.query(
            Game.name,
            Game.steam_appid,
            PlayerStats.timestamp,
            PlayerStats.current_players,
            PlayerStats.peak_players_24h,
            PlayerStats.estimated_owners,
            PlayerStats.estimated_revenue
        ).join(PlayerStats)
        
        # Apply filters
        if app_id:
            query = query.filter(Game.steam_appid == app_id)
        if start_date:
            query = query.filter(PlayerStats.timestamp >= start_date)
        if end_date:
            query = query.filter(PlayerStats.timestamp <= end_date)
        
        stats = query.order_by(PlayerStats.timestamp.desc()).all()
        
        # Build data
        data = []
        for stat in stats:
            data.append({
                'Game': stat.name,
                'Steam App ID': stat.steam_appid,
                'Timestamp': stat.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                'Current Players': stat.current_players or 0,
                'Peak Players (24h)': stat.peak_players_24h or 0,
                'Estimated Owners': stat.estimated_owners or 0,
                'Estimated Revenue': f"${stat.estimated_revenue:.2f}" if stat.estimated_revenue else 'N/A'
            })
        
        return pd.DataFrame(data)
    
    def export_genres_to_json(self) -> str:
        """
        Export genres with game counts to JSON.
        
        Returns:
            JSON string
        """
        genres = self.db.query(Genre).all()
        
        data = []
        for genre in genres:
            data.append({
                'id': genre.id,
                'name': genre.name,
                'description': genre.description or '',
                'game_count': len(genre.games),
                'top_games': [g.name for g in genre.games[:5]]
            })
        
        return json.dumps(data, indent=2)
    
    def export_market_report_to_json(
        self,
        game_ids: List[int]
    ) -> str:
        """
        Export market analysis report for selected games.
        
        Args:
            game_ids: List of game IDs to include
            
        Returns:
            JSON string with market report
        """
        games = self.db.query(Game).filter(Game.id.in_(game_ids)).all()
        
        report = {
            'generated_at': datetime.utcnow().isoformat(),
            'games': [],
            'summary': {
                'total_games': len(games),
                'unique_genres': len(set(g.name for game in games for g in game.genres)),
                'unique_developers': len(set(g.developer for g in games if g.developer))
            }
        }
        
        for game in games:
            # Get latest stats
            latest_stats = self.db.query(PlayerStats).filter(
                PlayerStats.game_id == game.id
            ).order_by(PlayerStats.timestamp.desc()).first()
            
            game_data = {
                'steam_appid': game.steam_appid,
                'name': game.name,
                'developer': game.developer,
                'publisher': game.publisher,
                'release_date': game.release_date.isoformat() if game.release_date else None,
                'genres': [g.name for g in game.genres],
                'tags': [t.name for t in game.tags[:10]],
                'platforms': {
                    'windows': game.windows,
                    'mac': game.mac,
                    'linux': game.linux
                }
            }
            
            if latest_stats:
                game_data['latest_stats'] = {
                    'timestamp': latest_stats.timestamp.isoformat(),
                    'current_players': latest_stats.current_players,
                    'estimated_owners': latest_stats.estimated_owners,
                    'estimated_revenue': latest_stats.estimated_revenue
                }
            
            report['games'].append(game_data)
        
        return json.dumps(report, indent=2)
    
    def get_summary_statistics(self) -> Dict[str, Any]:
        """
        Get summary statistics for the entire database.
        
        Returns:
            Dictionary with summary stats
        """
        return {
            'total_games': self.db.query(Game).count(),
            'total_genres': self.db.query(Genre).count(),
            'total_player_stats': self.db.query(PlayerStats).count(),
            'games_with_stats': self.db.query(Game).join(PlayerStats).distinct().count(),
            'date_range': {
                'earliest': self.db.query(PlayerStats.timestamp).order_by(
                    PlayerStats.timestamp.asc()
                ).first(),
                'latest': self.db.query(PlayerStats.timestamp).order_by(
                    PlayerStats.timestamp.desc()
                ).first()
            }
        }
