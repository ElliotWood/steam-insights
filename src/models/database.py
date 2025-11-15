"""
Database models for Steam Insights application.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean, ForeignKey, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

# Association table for many-to-many relationship between games and genres
game_genres = Table(
    'game_genres',
    Base.metadata,
    Column('game_id', Integer, ForeignKey('games.id')),
    Column('genre_id', Integer, ForeignKey('genres.id'))
)

# Association table for many-to-many relationship between games and tags
game_tags = Table(
    'game_tags',
    Base.metadata,
    Column('game_id', Integer, ForeignKey('games.id')),
    Column('tag_id', Integer, ForeignKey('tags.id'))
)


class Game(Base):
    """Game model representing a Steam game."""
    __tablename__ = 'games'

    id = Column(Integer, primary_key=True)
    steam_appid = Column(Integer, unique=True, nullable=False, index=True)
    name = Column(String(500), nullable=False, index=True)
    developer = Column(String(500))
    publisher = Column(String(500))
    release_date = Column(DateTime)
    description = Column(Text)
    short_description = Column(Text)
    header_image = Column(String(500))
    website = Column(String(500))
    
    # Platform support
    windows = Column(Boolean, default=False)
    mac = Column(Boolean, default=False)
    linux = Column(Boolean, default=False)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    genres = relationship('Genre', secondary=game_genres, back_populates='games')
    tags = relationship('Tag', secondary=game_tags, back_populates='games')
    reviews = relationship('Review', back_populates='game', cascade='all, delete-orphan')
    player_stats = relationship('PlayerStats', back_populates='game', cascade='all, delete-orphan')
    pricing_history = relationship('PricingHistory', back_populates='game', cascade='all, delete-orphan')


class Genre(Base):
    """Genre model."""
    __tablename__ = 'genres'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text)
    
    # Relationships
    games = relationship('Game', secondary=game_genres, back_populates='genres')


class Tag(Base):
    """Tag model."""
    __tablename__ = 'tags'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    
    # Relationships
    games = relationship('Game', secondary=game_tags, back_populates='tags')


class Review(Base):
    """Review model for game reviews."""
    __tablename__ = 'reviews'

    id = Column(Integer, primary_key=True)
    game_id = Column(Integer, ForeignKey('games.id'), nullable=False)
    steam_review_id = Column(String(100), unique=True)
    author = Column(String(200))
    review_text = Column(Text)
    is_positive = Column(Boolean)
    votes_up = Column(Integer, default=0)
    votes_funny = Column(Integer, default=0)
    playtime_at_review = Column(Float)  # hours
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    game = relationship('Game', back_populates='reviews')


class PlayerStats(Base):
    """Player statistics for a game at a specific time."""
    __tablename__ = 'player_stats'

    id = Column(Integer, primary_key=True)
    game_id = Column(Integer, ForeignKey('games.id'), nullable=False, index=True)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    
    # Player counts
    current_players = Column(Integer)
    peak_players_24h = Column(Integer)
    
    # Estimates
    estimated_owners = Column(Integer)
    estimated_revenue = Column(Float)
    
    # Relationships
    game = relationship('Game', back_populates='player_stats')


class PricingHistory(Base):
    """Pricing history for games."""
    __tablename__ = 'pricing_history'

    id = Column(Integer, primary_key=True)
    game_id = Column(Integer, ForeignKey('games.id'), nullable=False, index=True)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    
    # Pricing
    price_usd = Column(Float)
    discount_percent = Column(Float, default=0.0)
    final_price_usd = Column(Float)
    is_free = Column(Boolean, default=False)
    
    # Relationships
    game = relationship('Game', back_populates='pricing_history')


class Achievement(Base):
    """Achievement model."""
    __tablename__ = 'achievements'

    id = Column(Integer, primary_key=True)
    game_id = Column(Integer, ForeignKey('games.id'), nullable=False)
    name = Column(String(200), nullable=False)
    display_name = Column(String(200))
    description = Column(Text)
    icon = Column(String(500))
    completion_percentage = Column(Float)  # Global completion percentage
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
