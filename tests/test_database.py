"""
Tests for database connection and session management.
"""

from src.database.connection import init_db, get_db, SessionLocal
from src.models.database import Base, Game


def test_init_db(test_db):
    """Test database initialization."""
    # Database should be initialized with all tables
    init_db()
    # If no exception is raised, the test passes


def test_get_db():
    """Test database session generator."""
    db = next(get_db())
    assert db is not None
    
    # Should be able to query
    result = db.query(Game).count()
    assert result >= 0
    
    db.close()


def test_session_local():
    """Test SessionLocal factory."""
    session = SessionLocal()
    assert session is not None
    session.close()


def test_database_transaction_commit(test_db):
    """Test database commit."""
    game = Game(steam_appid=12345, name="Test Game")
    test_db.add(game)
    test_db.commit()
    
    # Verify the game was added
    found = test_db.query(Game).filter(Game.steam_appid == 12345).first()
    assert found is not None
    assert found.name == "Test Game"


def test_database_transaction_rollback(test_db):
    """Test database rollback."""
    game = Game(steam_appid=99999, name="Rollback Test")
    test_db.add(game)
    test_db.rollback()
    
    # Verify the game was not added
    found = test_db.query(Game).filter(Game.steam_appid == 99999).first()
    assert found is None
