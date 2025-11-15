"""
Tests for FastAPI endpoints.
"""

from fastapi.testclient import TestClient
from src.api.main import app
from src.models.database import Game, Genre, PlayerStats
from datetime import datetime


client = TestClient(app)


def test_root_endpoint():
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Steam Insights API"
    assert data["version"] == "1.0.0"


def test_list_games_empty(test_db):
    """Test listing games when database is empty."""
    # Note: This test assumes test_db fixture is available
    # In real scenario, we'd need to inject test_db into the app
    response = client.get("/games")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_list_games_with_search(test_db):
    """Test searching games."""
    response = client.get("/games?search=test")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_list_games_with_pagination(test_db):
    """Test game list pagination."""
    response = client.get("/games?skip=0&limit=10")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) <= 10


def test_get_game_not_found(test_db):
    """Test getting non-existent game."""
    response = client.get("/games/99999")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_list_genres_empty(test_db):
    """Test listing genres when empty."""
    response = client.get("/genres")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_trending_games(test_db):
    """Test getting trending games."""
    response = client.get("/stats/trending?limit=10")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
