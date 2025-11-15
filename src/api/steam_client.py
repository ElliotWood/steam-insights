"""
Steam Web API integration module.
"""

import logging
from typing import Dict, Optional, List, Any
import requests
from config.settings import settings

logger = logging.getLogger(__name__)


class SteamAPIClient:
    """Client for interacting with Steam Web API."""
    
    BASE_URL = "https://api.steampowered.com"
    STORE_API_URL = "https://store.steampowered.com/api"
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Steam API client.
        
        Args:
            api_key: Steam Web API key. If not provided, uses config settings.
        """
        self.api_key = api_key or settings.steam_api_key
        if not self.api_key:
            logger.warning("Steam API key not configured. Some features may not work.")
    
    def get_app_details(self, app_id: int) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a Steam app.
        
        Args:
            app_id: Steam application ID
            
        Returns:
            Dictionary containing app details, or None if not found
        """
        url = f"{self.STORE_API_URL}/appdetails"
        params = {'appids': app_id}
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if str(app_id) in data and data[str(app_id)]['success']:
                return data[str(app_id)]['data']
            return None
        except requests.RequestException as e:
            logger.error(f"Error fetching app details for {app_id}: {e}")
            return None
    
    def get_current_players(self, app_id: int) -> Optional[int]:
        """
        Get current number of players for a game.
        
        Args:
            app_id: Steam application ID
            
        Returns:
            Current player count, or None if unavailable
        """
        url = f"{self.BASE_URL}/ISteamUserStats/GetNumberOfCurrentPlayers/v1"
        params = {'appid': app_id}
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data['response']['result'] == 1:
                return data['response']['player_count']
            return None
        except requests.RequestException as e:
            logger.error(f"Error fetching player count for {app_id}: {e}")
            return None
    
    def get_global_achievement_percentages(self, app_id: int) -> Optional[List[Dict[str, Any]]]:
        """
        Get global achievement percentages for a game.
        
        Args:
            app_id: Steam application ID
            
        Returns:
            List of achievements with completion percentages, or None if unavailable
        """
        url = f"{self.BASE_URL}/ISteamUserStats/GetGlobalAchievementPercentagesForApp/v2"
        params = {'gameid': app_id}
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if 'achievementpercentages' in data:
                return data['achievementpercentages']['achievements']
            return None
        except requests.RequestException as e:
            logger.error(f"Error fetching achievements for {app_id}: {e}")
            return None
    
    def get_schema_for_game(self, app_id: int) -> Optional[Dict[str, Any]]:
        """
        Get the schema for a game (stats, achievements).
        
        Args:
            app_id: Steam application ID
            
        Returns:
            Game schema data, or None if unavailable
        """
        if not self.api_key:
            logger.error("API key required for GetSchemaForGame endpoint")
            return None
        
        url = f"{self.BASE_URL}/ISteamUserStats/GetSchemaForGame/v2"
        params = {
            'key': self.api_key,
            'appid': app_id
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if 'game' in data:
                return data['game']
            return None
        except requests.RequestException as e:
            logger.error(f"Error fetching schema for {app_id}: {e}")
            return None
    
    def get_app_list(self) -> Optional[List[Dict[str, Any]]]:
        """
        Get list of all Steam apps.
        
        Returns:
            List of all apps with IDs and names, or None if unavailable
        """
        url = f"{self.BASE_URL}/ISteamApps/GetAppList/v2"
        
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            if 'applist' in data and 'apps' in data['applist']:
                return data['applist']['apps']
            return None
        except requests.RequestException as e:
            logger.error(f"Error fetching app list: {e}")
            return None
