"""
Tests for market analysis features.
"""

from datetime import datetime
from sqlalchemy import func
from src.models.database import Game, Genre, PlayerStats


def test_game_ownership_data(test_db):
    """Test that games can store ownership data."""
    # Create games with ownership data
    game1 = Game(steam_appid=1, name='Game A')
    game2 = Game(steam_appid=2, name='Game B')
    test_db.add_all([game1, game2])
    test_db.commit()
    
    # Add ownership stats
    stats1 = PlayerStats(
        game_id=game1.id,
        timestamp=datetime.utcnow(),
        estimated_owners=1000000,
        current_players=50000
    )
    stats2 = PlayerStats(
        game_id=game2.id,
        timestamp=datetime.utcnow(),
        estimated_owners=500000,
        current_players=25000
    )
    test_db.add_all([stats1, stats2])
    test_db.commit()
    
    # Query games with ownership data
    games_with_owners = test_db.query(
        Game.id,
        Game.name,
        func.max(PlayerStats.estimated_owners).label('owners')
    ).join(PlayerStats).filter(
        PlayerStats.estimated_owners.isnot(None)
    ).group_by(Game.id, Game.name).all()
    
    assert len(games_with_owners) == 2
    assert games_with_owners[0].owners in [1000000, 500000]
    assert games_with_owners[1].owners in [1000000, 500000]


def test_genre_overlap_calculation(test_db):
    """Test calculating genre overlap between games."""
    # Create genres
    action = Genre(name='Action')
    rpg = Genre(name='RPG')
    strategy = Genre(name='Strategy')
    
    # Create games with different genre combinations
    game1 = Game(steam_appid=1, name='Action RPG Game')
    game1.genres.extend([action, rpg])
    
    game2 = Game(steam_appid=2, name='RPG Strategy Game')
    game2.genres.extend([rpg, strategy])
    
    game3 = Game(steam_appid=3, name='Pure Action Game')
    game3.genres.append(action)
    
    test_db.add_all([game1, game2, game3])
    test_db.commit()
    
    # Calculate genre similarities
    game1_genres = set(g.name for g in game1.genres)
    game2_genres = set(g.name for g in game2.genres)
    game3_genres = set(g.name for g in game3.genres)
    
    # Game 1 and 2 share RPG
    intersection_1_2 = len(game1_genres & game2_genres)
    union_1_2 = len(game1_genres | game2_genres)
    jaccard_1_2 = intersection_1_2 / union_1_2
    
    assert intersection_1_2 == 1  # RPG
    assert union_1_2 == 3  # Action, RPG, Strategy
    assert jaccard_1_2 == 1/3
    
    # Game 1 and 3 share Action
    intersection_1_3 = len(game1_genres & game3_genres)
    assert intersection_1_3 == 1  # Action


def test_market_overlap_estimation(test_db):
    """Test market overlap estimation logic."""
    # Create games with ownership data
    game1 = Game(steam_appid=1, name='Popular Game')
    game2 = Game(steam_appid=2, name='Niche Game')
    test_db.add_all([game1, game2])
    test_db.commit()
    
    # Add ownership stats
    stats1 = PlayerStats(
        game_id=game1.id,
        timestamp=datetime.utcnow(),
        estimated_owners=2000000
    )
    stats2 = PlayerStats(
        game_id=game2.id,
        timestamp=datetime.utcnow(),
        estimated_owners=500000
    )
    test_db.add_all([stats1, stats2])
    test_db.commit()
    
    # Simulate overlap calculation
    overlap_factor = 0.20  # Assume 20% overlap
    smaller_audience = min(stats1.estimated_owners, stats2.estimated_owners)
    estimated_overlap = int(smaller_audience * overlap_factor)
    
    # Addressable markets
    addressable_from_game1 = stats2.estimated_owners - estimated_overlap
    addressable_from_game2 = stats1.estimated_owners - estimated_overlap
    
    assert estimated_overlap == 100000  # 20% of 500k
    assert addressable_from_game1 == 400000  # 500k - 100k
    assert addressable_from_game2 == 1900000  # 2M - 100k
    
    # Combined unique audience
    total_unique = stats1.estimated_owners + stats2.estimated_owners - estimated_overlap
    assert total_unique == 2400000  # 2M + 500k - 100k


def test_multi_game_comparison(test_db):
    """Test comparing multiple games for market analysis."""
    # Create 3 games
    games = []
    for i in range(3):
        game = Game(steam_appid=i+1, name=f'Game {i+1}')
        test_db.add(game)
        test_db.flush()
        
        stats = PlayerStats(
            game_id=game.id,
            timestamp=datetime.utcnow(),
            estimated_owners=(i+1) * 500000  # 500k, 1M, 1.5M
        )
        test_db.add(stats)
        games.append(game)
    
    test_db.commit()
    
    # Query all games with ownership
    result = test_db.query(
        Game.id,
        Game.name,
        func.max(PlayerStats.estimated_owners).label('owners')
    ).join(PlayerStats).group_by(Game.id, Game.name).all()
    
    assert len(result) == 3
    total_owners = sum(r.owners for r in result)
    assert total_owners == 3000000  # 500k + 1M + 1.5M
