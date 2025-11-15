"""
Tests for Steam API client.
"""

from unittest.mock import Mock, patch
from src.api.steam_client import SteamAPIClient


def test_steam_client_initialization():
    """Test Steam API client initialization."""
    client = SteamAPIClient(api_key="test_key")
    assert client.api_key == "test_key"


@patch('src.api.steam_client.requests.get')
def test_get_current_players(mock_get):
    """Test getting current player count."""
    # Mock successful response
    mock_response = Mock()
    mock_response.json.return_value = {
        'response': {
            'result': 1,
            'player_count': 500000
        }
    }
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response
    
    client = SteamAPIClient()
    player_count = client.get_current_players(730)
    
    assert player_count == 500000
    mock_get.assert_called_once()


@patch('src.api.steam_client.requests.get')
def test_get_app_details(mock_get):
    """Test getting app details."""
    # Mock successful response
    mock_response = Mock()
    mock_response.json.return_value = {
        '730': {
            'success': True,
            'data': {
                'name': 'Counter-Strike 2',
                'developers': ['Valve'],
                'publishers': ['Valve']
            }
        }
    }
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response
    
    client = SteamAPIClient()
    details = client.get_app_details(730)
    
    assert details is not None
    assert details['name'] == 'Counter-Strike 2'
    assert 'Valve' in details['developers']
