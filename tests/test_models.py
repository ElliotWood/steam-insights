"""
Tests for database models.
"""

from datetime import datetime
from src.models.database import Game, Genre, Tag, PlayerStats


def test_create_game(test_db):
    """Test creating a game."""
    game = Game(
        steam_appid=730,
        name="Counter-Strike 2",
        developer="Valve",
        publisher="Valve"
    )
    
    test_db.add(game)
    test_db.commit()
    
    assert game.id is not None
    assert game.steam_appid == 730
    assert game.name == "Counter-Strike 2"


def test_game_genre_relationship(test_db):
    """Test game-genre many-to-many relationship."""
    game = Game(steam_appid=730, name="Counter-Strike 2")
    genre = Genre(name="Action")
    
    game.genres.append(genre)
    
    test_db.add(game)
    test_db.commit()
    
    assert len(game.genres) == 1
    assert game.genres[0].name == "Action"
    assert len(genre.games) == 1
    assert genre.games[0].name == "Counter-Strike 2"


def test_game_tag_relationship(test_db):
    """Test game-tag many-to-many relationship."""
    game = Game(steam_appid=730, name="Counter-Strike 2")
    tag1 = Tag(name="Multiplayer")
    tag2 = Tag(name="FPS")
    
    game.tags.extend([tag1, tag2])
    
    test_db.add(game)
    test_db.commit()
    
    assert len(game.tags) == 2
    tag_names = [tag.name for tag in game.tags]
    assert "Multiplayer" in tag_names
    assert "FPS" in tag_names


def test_player_stats(test_db):
    """Test player statistics."""
    game = Game(steam_appid=730, name="Counter-Strike 2")
    test_db.add(game)
    test_db.commit()
    
    stats = PlayerStats(
        game_id=game.id,
        timestamp=datetime.utcnow(),
        current_players=1000000
    )
    
    test_db.add(stats)
    test_db.commit()
    
    assert stats.id is not None
    assert stats.current_players == 1000000
    assert game.player_stats[0] == stats
