"""
Performance optimization utilities for Steam Insights.

This module provides caching, query optimization, and performance monitoring tools.
"""

import time
import hashlib
import json
from functools import wraps
from typing import Any, Callable, Optional, Dict
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import Index

# Simple in-memory cache (can be replaced with Redis in production)
_cache: Dict[str, Dict[str, Any]] = {}


def generate_cache_key(*args, **kwargs) -> str:
    """
    Generate a cache key from function arguments.
    
    Args:
        *args: Positional arguments
        **kwargs: Keyword arguments
        
    Returns:
        str: MD5 hash of the arguments
    """
    key_data = {
        'args': str(args),
        'kwargs': str(sorted(kwargs.items()))
    }
    key_str = json.dumps(key_data, sort_keys=True)
    return hashlib.md5(key_str.encode()).hexdigest()


def cache_result(ttl: int = 300):
    """
    Decorator to cache function results with time-to-live.
    
    Args:
        ttl: Time-to-live in seconds (default 5 minutes)
        
    Usage:
        @cache_result(ttl=600)
        def expensive_query(game_id):
            return db.query(Game).filter_by(id=game_id).first()
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = f"{func.__name__}:{generate_cache_key(*args, **kwargs)}"
            
            # Check if cached and not expired
            if cache_key in _cache:
                cached_data = _cache[cache_key]
                if datetime.now() < cached_data['expires_at']:
                    return cached_data['value']
                else:
                    # Expired, remove from cache
                    del _cache[cache_key]
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            _cache[cache_key] = {
                'value': result,
                'expires_at': datetime.now() + timedelta(seconds=ttl),
                'created_at': datetime.now()
            }
            
            return result
        
        return wrapper
    return decorator


def clear_cache(pattern: Optional[str] = None):
    """
    Clear cache entries matching a pattern.
    
    Args:
        pattern: Optional pattern to match (clears all if None)
    """
    if pattern is None:
        _cache.clear()
    else:
        keys_to_delete = [k for k in _cache.keys() if pattern in k]
        for key in keys_to_delete:
            del _cache[key]


def get_cache_stats() -> Dict[str, Any]:
    """
    Get cache statistics.
    
    Returns:
        dict: Cache statistics including size, oldest, newest entries
    """
    if not _cache:
        return {
            'size': 0,
            'entries': 0,
            'oldest': None,
            'newest': None
        }
    
    created_times = [v['created_at'] for v in _cache.values()]
    return {
        'size': len(_cache),
        'entries': len(_cache),
        'oldest': min(created_times).isoformat() if created_times else None,
        'newest': max(created_times).isoformat() if created_times else None
    }


def timing_decorator(func: Callable) -> Callable:
    """
    Decorator to measure function execution time.
    
    Usage:
        @timing_decorator
        def slow_function():
            time.sleep(1)
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        
        execution_time = end_time - start_time
        if execution_time > 1.0:
            print(f"⚠️  {func.__name__} took {execution_time:.2f}s")
        
        return result
    
    return wrapper


class QueryOptimizer:
    """
    Query optimization utilities.
    """
    
    @staticmethod
    def add_indexes(session: Session):
        """
        Add database indexes for common queries.
        
        Args:
            session: SQLAlchemy session
        """
        from src.models.database import Game, PlayerStats, PricingHistory, Genre
        
        # Indexes are defined in models using index=True
        # This method ensures they are created
        try:
            # Game indexes
            Index('ix_games_steam_appid', Game.steam_appid, unique=True)
            Index('ix_games_name', Game.name)
            Index('ix_games_developer', Game.developer)
            Index('ix_games_release_date', Game.release_date)
            
            # PlayerStats indexes
            Index('ix_playerstats_steam_appid', PlayerStats.steam_appid)
            Index('ix_playerstats_timestamp', PlayerStats.timestamp)
            Index('ix_playerstats_steam_timestamp', PlayerStats.steam_appid, PlayerStats.timestamp)
            
            # PricingHistory indexes
            Index('ix_pricing_steam_appid', PricingHistory.steam_appid)
            Index('ix_pricing_timestamp', PricingHistory.timestamp)
            
            # Genre indexes
            Index('ix_genres_name', Genre.name, unique=True)
            
            session.commit()
            return True
        except Exception as e:
            print(f"Index creation: {e}")
            session.rollback()
            return False
    
    @staticmethod
    def get_query_plan(session: Session, query):
        """
        Get query execution plan (for debugging).
        
        Args:
            session: SQLAlchemy session
            query: SQLAlchemy query object
            
        Returns:
            str: Query execution plan
        """
        return str(query.statement.compile(
            dialect=session.bind.dialect,
            compile_kwargs={"literal_binds": True}
        ))


class PerformanceMonitor:
    """
    Monitor performance metrics.
    """
    
    def __init__(self):
        self.metrics: Dict[str, list] = {}
    
    def record(self, metric_name: str, value: float):
        """
        Record a performance metric.
        
        Args:
            metric_name: Name of the metric
            value: Metric value
        """
        if metric_name not in self.metrics:
            self.metrics[metric_name] = []
        
        self.metrics[metric_name].append({
            'value': value,
            'timestamp': datetime.now()
        })
    
    def get_average(self, metric_name: str, window_seconds: int = 300) -> Optional[float]:
        """
        Get average metric value over a time window.
        
        Args:
            metric_name: Name of the metric
            window_seconds: Time window in seconds
            
        Returns:
            float: Average value or None
        """
        if metric_name not in self.metrics:
            return None
        
        cutoff = datetime.now() - timedelta(seconds=window_seconds)
        recent = [
            m['value'] for m in self.metrics[metric_name]
            if m['timestamp'] > cutoff
        ]
        
        return sum(recent) / len(recent) if recent else None
    
    def get_stats(self, metric_name: str) -> Dict[str, Any]:
        """
        Get statistics for a metric.
        
        Args:
            metric_name: Name of the metric
            
        Returns:
            dict: Statistics including count, min, max, avg
        """
        if metric_name not in self.metrics or not self.metrics[metric_name]:
            return {}
        
        values = [m['value'] for m in self.metrics[metric_name]]
        return {
            'count': len(values),
            'min': min(values),
            'max': max(values),
            'avg': sum(values) / len(values),
            'last': values[-1] if values else None
        }


# Global performance monitor
performance_monitor = PerformanceMonitor()


def batch_insert(session: Session, model_class, items: list, batch_size: int = 100):
    """
    Batch insert items for better performance.
    
    Args:
        session: SQLAlchemy session
        model_class: SQLAlchemy model class
        items: List of dicts with item data
        batch_size: Number of items per batch
        
    Returns:
        int: Number of items inserted
    """
    inserted = 0
    
    for i in range(0, len(items), batch_size):
        batch = items[i:i + batch_size]
        session.bulk_insert_mappings(model_class, batch)
        session.commit()
        inserted += len(batch)
    
    return inserted


def optimize_query_for_pagination(query, page: int = 1, per_page: int = 20):
    """
    Optimize query for pagination with proper offset/limit.
    
    Args:
        query: SQLAlchemy query
        page: Page number (1-indexed)
        per_page: Items per page
        
    Returns:
        tuple: (optimized_query, total_count)
    """
    # Count total (expensive operation, consider caching)
    total = query.count()
    
    # Apply pagination
    offset = (page - 1) * per_page
    optimized = query.offset(offset).limit(per_page)
    
    return optimized, total


def lazy_load_relationships(session: Session, model, relationship_name: str):
    """
    Explicitly lazy load a relationship (for debugging).
    
    Args:
        session: SQLAlchemy session
        model: Model instance
        relationship_name: Name of the relationship
    """
    getattr(model, relationship_name)  # This triggers the load


# Pre-computed aggregates cache
_aggregates_cache = {}


def precompute_aggregates(session: Session, force: bool = False):
    """
    Pre-compute common aggregates for better performance.
    
    Args:
        session: SQLAlchemy session
        force: Force recomputation even if cached
        
    Returns:
        dict: Aggregated statistics
    """
    from src.models.database import Game, Genre, PlayerStats
    
    cache_key = 'aggregates'
    
    # Check cache
    if not force and cache_key in _aggregates_cache:
        cached = _aggregates_cache[cache_key]
        if datetime.now() < cached['expires_at']:
            return cached['data']
    
    # Compute aggregates
    aggregates = {
        'total_games': session.query(Game).count(),
        'total_genres': session.query(Genre).count(),
        'games_with_stats': session.query(
            PlayerStats.steam_appid
        ).distinct().count(),
        'platform_counts': {
            'windows': session.query(Game).filter(Game.windows == True).count(),
            'mac': session.query(Game).filter(Game.mac == True).count(),
            'linux': session.query(Game).filter(Game.linux == True).count(),
        },
        'computed_at': datetime.now().isoformat()
    }
    
    # Cache for 10 minutes
    _aggregates_cache[cache_key] = {
        'data': aggregates,
        'expires_at': datetime.now() + timedelta(minutes=10)
    }
    
    return aggregates
