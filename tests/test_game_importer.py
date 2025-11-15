"""
Tests for ETL game importer.
"""

from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from src.etl.game_importer import GameDataImporter
from src.models.database import Game, Genre, Tag


def test_game_importer_initialization(test_db):
    """Test GameDataImporter initialization."""
    importer = GameDataImporter(test_db)
    assert importer.db == test_db
    assert importer.steam_client is not None
    assert importer.scraper is not None


@patch('src.etl.game_importer.SteamAPIClient.get_app_details')
def test_import_game_success(mock_get_details, test_db):
    """Test successful game import."""
    # Mock API response
    mock_get_details.return_value = {
        'name': 'Test Game',
        'detailed_description': 'Test description',
        'short_description': 'Short desc',
        'header_image': 'http://example.com/image.jpg',
        'website': 'http://example.com',
        'developers': ['Test Dev'],
        'publishers': ['Test Pub'],
        'release_date': {'coming_soon': False, 'date': 'Jan 1, 2020'},
        'platforms': {'windows': True, 'mac': False, 'linux': True},
        'genres': [{'description': 'Action'}],
        'categories': [{'description': 'Multiplayer'}]
    }
    
    importer = GameDataImporter(test_db)
    game = importer.import_game(12345)
    
    assert game is not None
    assert game.steam_appid == 12345
    assert game.name == 'Test Game'
    assert game.developer == 'Test Dev'
    assert game.publisher == 'Test Pub'
    assert game.windows is True
    assert game.linux is True
    assert len(game.genres) == 1
    assert game.genres[0].name == 'Action'


@patch('src.etl.game_importer.SteamAPIClient.get_app_details')
def test_import_game_duplicate(mock_get_details, test_db):
    """Test importing the same game twice updates it."""
    mock_get_details.return_value = {
        'name': 'Test Game',
        'detailed_description': 'Test description',
        'short_description': 'Short desc',
        'genres': [],
        'categories': [],
        'platforms': {}
    }
    
    importer = GameDataImporter(test_db)
    
    # Import first time
    game1 = importer.import_game(12345)
    assert game1 is not None
    
    # Import second time - should update
    mock_get_details.return_value['name'] = 'Updated Game'
    game2 = importer.import_game(12345)
    
    assert game2 is not None
    assert game2.id == game1.id
    assert game2.name == 'Updated Game'


@patch('src.etl.game_importer.SteamAPIClient.get_current_players')
def test_update_player_stats_success(mock_get_players, test_db):
    """Test updating player statistics."""
    # Create a game first
    game = Game(steam_appid=12345, name='Test Game')
    test_db.add(game)
    test_db.commit()
    
    # Mock player count
    mock_get_players.return_value = 10000
    
    importer = GameDataImporter(test_db)
    stats = importer.update_player_stats(12345)
    
    assert stats is not None
    assert stats.game_id == game.id
    assert stats.current_players == 10000


@patch('src.etl.game_importer.SteamAPIClient.get_current_players')
def test_update_player_stats_game_not_found(mock_get_players, test_db):
    """Test updating player stats for non-existent game."""
    mock_get_players.return_value = 10000
    
    importer = GameDataImporter(test_db)
    stats = importer.update_player_stats(99999)
    
    assert stats is None


@patch('src.etl.game_importer.SteamAPIClient.get_app_details')
def test_update_pricing_success(mock_get_details, test_db):
    """Test updating pricing information."""
    # Create a game first
    game = Game(steam_appid=12345, name='Test Game')
    test_db.add(game)
    test_db.commit()
    
    # Mock pricing data
    mock_get_details.return_value = {
        'price_overview': {
            'initial': 1999,  # $19.99 in cents
            'final': 999,     # $9.99 in cents
            'discount_percent': 50
        },
        'is_free': False
    }
    
    importer = GameDataImporter(test_db)
    pricing = importer.update_pricing(12345)
    
    assert pricing is not None
    assert pricing.game_id == game.id
    assert pricing.price_usd == 19.99
    assert pricing.final_price_usd == 9.99
    assert pricing.discount_percent == 50.0
    assert pricing.is_free is False


def test_process_genres(test_db):
    """Test genre processing."""
    game = Game(steam_appid=12345, name='Test Game')
    test_db.add(game)
    test_db.commit()
    
    importer = GameDataImporter(test_db)
    genre_data = [
        {'description': 'Action'},
        {'description': 'Adventure'}
    ]
    
    importer._process_genres(game, genre_data)
    test_db.commit()
    
    assert len(game.genres) == 2
    genre_names = [g.name for g in game.genres]
    assert 'Action' in genre_names
    assert 'Adventure' in genre_names


def test_process_tags(test_db):
    """Test tag processing."""
    game = Game(steam_appid=12345, name='Test Game')
    test_db.add(game)
    test_db.commit()
    
    importer = GameDataImporter(test_db)
    tag_data = [
        {'description': 'Multiplayer'},
        {'description': 'FPS'}
    ]
    
    importer._process_tags(game, tag_data)
    test_db.commit()
    
    assert len(game.tags) == 2
    tag_names = [t.name for t in game.tags]
    assert 'Multiplayer' in tag_names
    assert 'FPS' in tag_names
