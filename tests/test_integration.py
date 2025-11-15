"""
Integration tests for complete workflows.
"""

from unittest.mock import patch, Mock
from src.database.connection import get_db, init_db
from src.etl.game_importer import GameDataImporter
from src.models.database import Game, Genre, Tag, PlayerStats, PricingHistory


def test_complete_game_import_workflow(test_db):
    """Test complete workflow of importing a game with all data."""
    # Mock Steam API responses
    with patch('src.api.steam_client.requests.get') as mock_get:
        # Mock app details response
        app_details_response = Mock()
        app_details_response.json.return_value = {
            '730': {
                'success': True,
                'data': {
                    'name': 'Counter-Strike 2',
                    'detailed_description': 'A popular FPS game',
                    'short_description': 'FPS game',
                    'header_image': 'http://example.com/cs2.jpg',
                    'website': 'http://example.com',
                    'developers': ['Valve'],
                    'publishers': ['Valve'],
                    'release_date': {'coming_soon': False, 'date': 'Sep 27, 2023'},
                    'platforms': {'windows': True, 'mac': True, 'linux': True},
                    'genres': [{'description': 'Action'}, {'description': 'FPS'}],
                    'categories': [{'description': 'Multiplayer'}],
                    'price_overview': {
                        'initial': 0,
                        'final': 0,
                        'discount_percent': 0
                    },
                    'is_free': True
                }
            }
        }
        app_details_response.raise_for_status = Mock()
        
        # Mock player count response
        player_count_response = Mock()
        player_count_response.json.return_value = {
            'response': {
                'result': 1,
                'player_count': 500000
            }
        }
        player_count_response.raise_for_status = Mock()
        
        # Setup mock to return different responses based on URL
        def get_side_effect(url, *args, **kwargs):
            if 'appdetails' in url:
                return app_details_response
            elif 'GetNumberOfCurrentPlayers' in url:
                return player_count_response
            return Mock()
        
        mock_get.side_effect = get_side_effect
        
        # Create importer and import game
        importer = GameDataImporter(test_db)
        game = importer.import_game(730)
        
        # Verify game was imported
        assert game is not None
        assert game.name == 'Counter-Strike 2'
        assert game.developer == 'Valve'
        assert game.publisher == 'Valve'
        assert game.windows is True
        assert game.mac is True
        assert game.linux is True
        
        # Verify genres were created
        assert len(game.genres) == 2
        genre_names = [g.name for g in game.genres]
        assert 'Action' in genre_names
        assert 'FPS' in genre_names
        
        # Verify tags were created
        assert len(game.tags) == 1
        assert game.tags[0].name == 'Multiplayer'
        
        # Update player stats
        stats = importer.update_player_stats(730)
        assert stats is not None
        assert stats.current_players == 500000
        
        # Update pricing
        pricing = importer.update_pricing(730)
        assert pricing is not None
        assert pricing.is_free is True
        assert pricing.price_usd == 0.0


def test_query_games_by_genre(test_db):
    """Test querying games by genre."""
    # Create test data
    action_genre = Genre(name='Action')
    adventure_genre = Genre(name='Adventure')
    
    game1 = Game(steam_appid=1, name='Action Game')
    game1.genres.append(action_genre)
    
    game2 = Game(steam_appid=2, name='Adventure Game')
    game2.genres.append(adventure_genre)
    
    game3 = Game(steam_appid=3, name='Action Adventure')
    game3.genres.extend([action_genre, adventure_genre])
    
    test_db.add_all([game1, game2, game3])
    test_db.commit()
    
    # Query action games
    action_games = test_db.query(Game).join(Game.genres).filter(
        Genre.name == 'Action'
    ).all()
    
    assert len(action_games) == 2
    game_names = [g.name for g in action_games]
    assert 'Action Game' in game_names
    assert 'Action Adventure' in game_names


def test_player_stats_time_series(test_db):
    """Test tracking player stats over time."""
    from datetime import datetime, timedelta
    
    # Create a game
    game = Game(steam_appid=730, name='Test Game')
    test_db.add(game)
    test_db.commit()
    
    # Add player stats at different times
    base_time = datetime.utcnow()
    for i in range(5):
        stats = PlayerStats(
            game_id=game.id,
            timestamp=base_time - timedelta(hours=i),
            current_players=100000 + (i * 10000)
        )
        test_db.add(stats)
    
    test_db.commit()
    
    # Query stats
    all_stats = test_db.query(PlayerStats).filter(
        PlayerStats.game_id == game.id
    ).order_by(PlayerStats.timestamp).all()
    
    assert len(all_stats) == 5
    assert all_stats[0].current_players == 140000  # Oldest first
    assert all_stats[-1].current_players == 100000  # Newest last


def test_multi_game_comparison(test_db):
    """Test comparing multiple games."""
    from datetime import datetime
    
    # Create multiple games with stats
    games = []
    for i in range(3):
        game = Game(steam_appid=i+1, name=f'Game {i+1}')
        test_db.add(game)
        test_db.flush()
        
        stats = PlayerStats(
            game_id=game.id,
            timestamp=datetime.utcnow(),
            current_players=(i+1) * 50000
        )
        test_db.add(stats)
        games.append(game)
    
    test_db.commit()
    
    # Query top games by player count
    from sqlalchemy import func
    top_games = test_db.query(
        Game.name,
        func.max(PlayerStats.current_players).label('max_players')
    ).join(PlayerStats).group_by(Game.name).order_by(
        func.max(PlayerStats.current_players).desc()
    ).all()
    
    assert len(top_games) == 3
    assert top_games[0][0] == 'Game 3'
    assert top_games[0][1] == 150000


def test_pricing_history_tracking(test_db):
    """Test tracking price changes over time."""
    from datetime import datetime, timedelta
    
    # Create a game
    game = Game(steam_appid=123, name='Test Game')
    test_db.add(game)
    test_db.commit()
    
    # Add pricing history
    base_time = datetime.utcnow()
    prices = [
        (19.99, 0, 19.99),
        (19.99, 25, 14.99),
        (19.99, 50, 9.99)
    ]
    
    for i, (price, discount, final) in enumerate(prices):
        pricing = PricingHistory(
            game_id=game.id,
            timestamp=base_time - timedelta(days=i),
            price_usd=price,
            discount_percent=discount,
            final_price_usd=final,
            is_free=False
        )
        test_db.add(pricing)
    
    test_db.commit()
    
    # Query pricing history
    history = test_db.query(PricingHistory).filter(
        PricingHistory.game_id == game.id
    ).order_by(PricingHistory.timestamp.desc()).all()
    
    assert len(history) == 3
    assert history[0].final_price_usd == 19.99  # Most recent
    assert history[1].discount_percent == 25
    assert history[2].discount_percent == 50  # Oldest


def test_database_relationships_integrity(test_db):
    """Test that database relationships maintain integrity."""
    # Create interconnected data
    genre = Genre(name='Action')
    tag1 = Tag(name='Multiplayer')
    tag2 = Tag(name='FPS')
    
    game = Game(steam_appid=999, name='Test Game')
    game.genres.append(genre)
    game.tags.extend([tag1, tag2])
    
    test_db.add(game)
    test_db.commit()
    
    # Query from different directions
    # Game -> Genres
    assert len(game.genres) == 1
    assert game.genres[0].name == 'Action'
    
    # Genre -> Games
    assert len(genre.games) == 1
    assert genre.games[0].name == 'Test Game'
    
    # Game -> Tags
    assert len(game.tags) == 2
    tag_names = [t.name for t in game.tags]
    assert 'Multiplayer' in tag_names
    assert 'FPS' in tag_names
    
    # Tag -> Games
    assert len(tag1.games) == 1
    assert tag1.games[0].name == 'Test Game'


def test_data_persistence_across_sessions(test_db):
    """Test that data persists across database sessions."""
    # Create and save data in first "session"
    game = Game(steam_appid=456, name='Persistent Game')
    test_db.add(game)
    test_db.commit()
    game_id = game.id
    
    # Clear session to simulate new connection
    test_db.expunge_all()
    
    # Query in "new session"
    retrieved_game = test_db.query(Game).filter(Game.id == game_id).first()
    
    assert retrieved_game is not None
    assert retrieved_game.steam_appid == 456
    assert retrieved_game.name == 'Persistent Game'
