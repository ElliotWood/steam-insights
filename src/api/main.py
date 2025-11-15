"""
FastAPI backend for Steam Insights.
"""

from typing import List, Optional
from datetime import datetime, timedelta
from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from src.database.connection import get_db, init_db
from src.models.database import Game, Genre, Tag, PlayerStats, PricingHistory
from pydantic import BaseModel

# Initialize FastAPI app
app = FastAPI(
    title="Steam Insights API",
    description="API for Steam game analytics and insights",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Pydantic models for API responses
class GameResponse(BaseModel):
    id: int
    steam_appid: int
    name: str
    developer: Optional[str]
    publisher: Optional[str]
    release_date: Optional[datetime]
    short_description: Optional[str]
    header_image: Optional[str]
    windows: bool
    mac: bool
    linux: bool
    
    class Config:
        from_attributes = True


class GameDetailResponse(GameResponse):
    description: Optional[str]
    website: Optional[str]
    genres: List[str]
    tags: List[str]
    current_players: Optional[int]
    current_price: Optional[float]


class PlayerStatsResponse(BaseModel):
    timestamp: datetime
    current_players: int
    peak_players_24h: Optional[int]
    
    class Config:
        from_attributes = True


class GenreResponse(BaseModel):
    id: int
    name: str
    game_count: int
    
    class Config:
        from_attributes = True


# API Endpoints

@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    init_db()


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Steam Insights API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/games", response_model=List[GameResponse])
async def list_games(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    genre: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    List games with optional filtering.
    
    - **skip**: Number of records to skip (pagination)
    - **limit**: Maximum number of records to return
    - **search**: Search term for game name
    - **genre**: Filter by genre name
    """
    query = db.query(Game)
    
    if search:
        query = query.filter(Game.name.ilike(f"%{search}%"))
    
    if genre:
        query = query.join(Game.genres).filter(Genre.name.ilike(f"%{genre}%"))
    
    games = query.offset(skip).limit(limit).all()
    return games


@app.get("/games/{app_id}", response_model=GameDetailResponse)
async def get_game(app_id: int, db: Session = Depends(get_db)):
    """
    Get detailed information about a specific game.
    
    - **app_id**: Steam application ID
    """
    game = db.query(Game).filter(Game.steam_appid == app_id).first()
    
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    
    # Get latest player stats
    latest_stats = db.query(PlayerStats).filter(
        PlayerStats.game_id == game.id
    ).order_by(desc(PlayerStats.timestamp)).first()
    
    # Get latest pricing
    latest_price = db.query(PricingHistory).filter(
        PricingHistory.game_id == game.id
    ).order_by(desc(PricingHistory.timestamp)).first()
    
    return GameDetailResponse(
        id=game.id,
        steam_appid=game.steam_appid,
        name=game.name,
        developer=game.developer,
        publisher=game.publisher,
        release_date=game.release_date,
        description=game.description,
        short_description=game.short_description,
        header_image=game.header_image,
        website=game.website,
        windows=game.windows,
        mac=game.mac,
        linux=game.linux,
        genres=[g.name for g in game.genres],
        tags=[t.name for t in game.tags],
        current_players=latest_stats.current_players if latest_stats else None,
        current_price=latest_price.final_price_usd if latest_price else None
    )


@app.get("/games/{app_id}/player-stats", response_model=List[PlayerStatsResponse])
async def get_player_stats(
    app_id: int,
    days: int = Query(7, ge=1, le=365),
    db: Session = Depends(get_db)
):
    """
    Get player statistics history for a game.
    
    - **app_id**: Steam application ID
    - **days**: Number of days of history to return
    """
    game = db.query(Game).filter(Game.steam_appid == app_id).first()
    
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    
    since = datetime.utcnow() - timedelta(days=days)
    
    stats = db.query(PlayerStats).filter(
        PlayerStats.game_id == game.id,
        PlayerStats.timestamp >= since
    ).order_by(PlayerStats.timestamp).all()
    
    return stats


@app.get("/genres", response_model=List[GenreResponse])
async def list_genres(db: Session = Depends(get_db)):
    """
    List all genres with game counts.
    """
    genres = db.query(
        Genre.id,
        Genre.name,
        func.count(Game.id).label('game_count')
    ).join(
        Genre.games
    ).group_by(
        Genre.id, Genre.name
    ).all()
    
    return [
        GenreResponse(id=g.id, name=g.name, game_count=g.game_count)
        for g in genres
    ]


@app.get("/stats/trending")
async def get_trending_games(
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """
    Get trending games based on recent player count increases.
    
    - **limit**: Number of games to return
    """
    # Get games with recent player stats
    recent_date = datetime.utcnow() - timedelta(hours=24)
    
    trending = db.query(
        Game,
        func.max(PlayerStats.current_players).label('max_players')
    ).join(
        PlayerStats
    ).filter(
        PlayerStats.timestamp >= recent_date
    ).group_by(
        Game.id
    ).order_by(
        desc('max_players')
    ).limit(limit).all()
    
    return [
        {
            "game": GameResponse.from_orm(game),
            "current_players": max_players
        }
        for game, max_players in trending
    ]


if __name__ == "__main__":
    import uvicorn
    from config.settings import settings
    
    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug
    )
