"""
Advanced analytics module for Steam Insights.
"""

import numpy as np
import pandas as pd
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func

from src.models.database import Game, Genre, PlayerStats, Tag


class AdvancedAnalytics:
    """Advanced analytics and forecasting capabilities."""
    
    def __init__(self, db: Session):
        """Initialize with database session."""
        self.db = db
    
    def get_correlation_matrix(
        self,
        game_ids: List[int],
        days: int = 30
    ) -> pd.DataFrame:
        """
        Calculate correlation matrix for player counts across games.
        
        Args:
            game_ids: List of game IDs to analyze
            days: Number of days of history to use
            
        Returns:
            DataFrame with correlation matrix
        """
        since = datetime.utcnow() - timedelta(days=days)
        
        # Fetch data for each game
        game_data = {}
        for game_id in game_ids:
            game = self.db.query(Game).filter(Game.id == game_id).first()
            if not game:
                continue
            
            stats = self.db.query(
                PlayerStats.timestamp,
                PlayerStats.current_players
            ).filter(
                PlayerStats.game_id == game_id,
                PlayerStats.timestamp >= since,
                PlayerStats.current_players.isnot(None)
            ).order_by(PlayerStats.timestamp).all()
            
            if stats:
                game_data[game.name] = {
                    'timestamps': [s.timestamp for s in stats],
                    'players': [s.current_players for s in stats]
                }
        
        if len(game_data) < 2:
            return pd.DataFrame()
        
        # Create aligned time series
        df_dict = {}
        for game_name, data in game_data.items():
            df_dict[game_name] = pd.Series(
                data['players'],
                index=pd.to_datetime(data['timestamps'])
            )
        
        df = pd.DataFrame(df_dict)
        
        # Resample to hourly to align timestamps
        df = df.resample('1H').mean()
        
        # Calculate correlation
        corr_matrix = df.corr()
        
        return corr_matrix
    
    def forecast_player_count(
        self,
        game_id: int,
        hours_ahead: int = 24,
        method: str = 'moving_average'
    ) -> Dict[str, Any]:
        """
        Forecast future player counts.
        
        Args:
            game_id: Game ID to forecast
            hours_ahead: Hours to forecast into future
            method: Forecasting method ('moving_average', 'linear', 'exponential')
            
        Returns:
            Dictionary with forecast data
        """
        # Get historical data (last 7 days)
        since = datetime.utcnow() - timedelta(days=7)
        
        stats = self.db.query(
            PlayerStats.timestamp,
            PlayerStats.current_players
        ).filter(
            PlayerStats.game_id == game_id,
            PlayerStats.timestamp >= since,
            PlayerStats.current_players.isnot(None)
        ).order_by(PlayerStats.timestamp).all()
        
        if len(stats) < 5:
            return {'error': 'Insufficient data for forecasting'}
        
        # Prepare data
        timestamps = [s.timestamp for s in stats]
        players = [s.current_players for s in stats]
        
        # Create time series
        df = pd.DataFrame({
            'timestamp': timestamps,
            'players': players
        })
        df.set_index('timestamp', inplace=True)
        
        # Resample to hourly
        df_hourly = df.resample('1H').mean().ffill()
        
        # Forecast based on method
        if method == 'moving_average':
            # Simple moving average
            window = min(24, len(df_hourly))
            forecast_value = df_hourly['players'].tail(window).mean()
            
            # Create forecast points
            last_time = df_hourly.index[-1]
            forecast_times = [
                last_time + timedelta(hours=i+1) 
                for i in range(hours_ahead)
            ]
            forecast_values = [forecast_value] * hours_ahead
            
        elif method == 'linear':
            # Linear regression
            x = np.arange(len(df_hourly))
            y = df_hourly['players'].values
            
            # Fit linear model
            coeffs = np.polyfit(x, y, 1)
            
            # Forecast
            last_x = len(df_hourly) - 1
            forecast_x = np.arange(last_x + 1, last_x + hours_ahead + 1)
            forecast_values = np.polyval(coeffs, forecast_x).tolist()
            
            last_time = df_hourly.index[-1]
            forecast_times = [
                last_time + timedelta(hours=i+1) 
                for i in range(hours_ahead)
            ]
            
        else:  # exponential weighted
            # Exponential moving average
            alpha = 0.3
            ewm = df_hourly['players'].ewm(alpha=alpha).mean()
            forecast_value = ewm.iloc[-1]
            
            last_time = df_hourly.index[-1]
            forecast_times = [
                last_time + timedelta(hours=i+1) 
                for i in range(hours_ahead)
            ]
            forecast_values = [forecast_value] * hours_ahead
        
        # Get game name
        game = self.db.query(Game).filter(Game.id == game_id).first()
        
        return {
            'game_name': game.name if game else 'Unknown',
            'method': method,
            'historical': {
                'timestamps': timestamps,
                'players': players
            },
            'forecast': {
                'timestamps': forecast_times,
                'players': [max(0, int(p)) for p in forecast_values]
            },
            'confidence': 'medium'  # Placeholder for confidence intervals
        }
    
    def get_genre_performance_metrics(self) -> pd.DataFrame:
        """
        Calculate performance metrics by genre.
        
        Returns:
            DataFrame with genre metrics
        """
        # Get genres with stats
        genre_stats = self.db.query(
            Genre.name,
            func.count(Game.id.distinct()).label('game_count'),
            func.avg(PlayerStats.current_players).label('avg_players'),
            func.max(PlayerStats.current_players).label('peak_players'),
            func.sum(PlayerStats.estimated_owners).label('total_owners')
        ).join(
            Genre.games
        ).outerjoin(
            PlayerStats, Game.id == PlayerStats.game_id
        ).group_by(
            Genre.name
        ).all()
        
        if not genre_stats:
            return pd.DataFrame()
        
        data = []
        for stat in genre_stats:
            data.append({
                'Genre': stat.name,
                'Games': stat.game_count,
                'Avg Players': int(stat.avg_players or 0),
                'Peak Players': int(stat.peak_players or 0),
                'Total Owners': int(stat.total_owners or 0),
                'Avg Owners per Game': int((stat.total_owners or 0) / max(stat.game_count, 1))
            })
        
        return pd.DataFrame(data)
    
    def get_growth_trends(
        self,
        game_id: int,
        period_days: int = 7
    ) -> Dict[str, Any]:
        """
        Calculate growth trends for a game.
        
        Args:
            game_id: Game ID to analyze
            period_days: Days to analyze
            
        Returns:
            Dictionary with growth metrics
        """
        since = datetime.utcnow() - timedelta(days=period_days)
        
        stats = self.db.query(
            PlayerStats.timestamp,
            PlayerStats.current_players
        ).filter(
            PlayerStats.game_id == game_id,
            PlayerStats.timestamp >= since,
            PlayerStats.current_players.isnot(None)
        ).order_by(PlayerStats.timestamp).all()
        
        if len(stats) < 2:
            return {'error': 'Insufficient data'}
        
        players = [s.current_players for s in stats]
        
        # Calculate metrics
        first_value = players[0]
        last_value = players[-1]
        max_value = max(players)
        min_value = min(players)
        avg_value = sum(players) / len(players)
        
        # Growth rate
        growth_rate = ((last_value - first_value) / first_value * 100) if first_value > 0 else 0
        
        # Volatility (standard deviation)
        volatility = np.std(players)
        
        # Trend direction
        if growth_rate > 5:
            trend = 'Growing'
        elif growth_rate < -5:
            trend = 'Declining'
        else:
            trend = 'Stable'
        
        game = self.db.query(Game).filter(Game.id == game_id).first()
        
        return {
            'game_name': game.name if game else 'Unknown',
            'period_days': period_days,
            'first_value': int(first_value),
            'last_value': int(last_value),
            'max_value': int(max_value),
            'min_value': int(min_value),
            'avg_value': int(avg_value),
            'growth_rate': round(growth_rate, 2),
            'volatility': round(volatility, 2),
            'trend': trend,
            'data_points': len(stats)
        }
    
    def compare_games(
        self,
        game_ids: List[int],
        metrics: List[str] = None
    ) -> pd.DataFrame:
        """
        Compare multiple games across various metrics.
        
        Args:
            game_ids: List of game IDs to compare
            metrics: List of metrics to compare
            
        Returns:
            DataFrame with comparison
        """
        if metrics is None:
            metrics = ['current_players', 'peak_players', 'estimated_owners']
        
        comparison_data = []
        
        for game_id in game_ids:
            game = self.db.query(Game).filter(Game.id == game_id).first()
            if not game:
                continue
            
            # Get latest stats
            latest_stats = self.db.query(PlayerStats).filter(
                PlayerStats.game_id == game_id
            ).order_by(PlayerStats.timestamp.desc()).first()
            
            row = {
                'Game': game.name,
                'Developer': game.developer or 'Unknown',
                'Release': game.release_date.strftime('%Y') if game.release_date else 'N/A',
                'Genres': ', '.join([g.name for g in game.genres[:2]]) if game.genres else 'N/A'
            }
            
            if latest_stats:
                if 'current_players' in metrics:
                    row['Current Players'] = latest_stats.current_players or 0
                if 'peak_players' in metrics:
                    row['Peak (24h)'] = latest_stats.peak_players_24h or 0
                if 'estimated_owners' in metrics:
                    row['Est. Owners'] = latest_stats.estimated_owners or 0
            else:
                for metric in metrics:
                    row[metric] = 0
            
            comparison_data.append(row)
        
        return pd.DataFrame(comparison_data)
    
    def get_platform_distribution(self) -> Dict[str, int]:
        """
        Get distribution of games across platforms.
        
        Returns:
            Dictionary with platform counts
        """
        total_games = self.db.query(Game).count()
        windows_count = self.db.query(Game).filter(Game.windows == True).count()
        mac_count = self.db.query(Game).filter(Game.mac == True).count()
        linux_count = self.db.query(Game).filter(Game.linux == True).count()
        
        # Multi-platform
        all_platforms = self.db.query(Game).filter(
            Game.windows == True,
            Game.mac == True,
            Game.linux == True
        ).count()
        
        return {
            'Total Games': total_games,
            'Windows': windows_count,
            'Mac': mac_count,
            'Linux': linux_count,
            'All Platforms': all_platforms,
            'Windows %': round(windows_count / max(total_games, 1) * 100, 1),
            'Mac %': round(mac_count / max(total_games, 1) * 100, 1),
            'Linux %': round(linux_count / max(total_games, 1) * 100, 1)
        }
