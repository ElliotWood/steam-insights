"""
Tests for performance optimization utilities.
"""

import pytest
import time
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
from src.utils.performance import (
    cache_result,
    clear_cache,
    get_cache_stats,
    timing_decorator,
    QueryOptimizer,
    PerformanceMonitor,
    batch_insert,
    optimize_query_for_pagination,
    precompute_aggregates
)


class TestCaching:
    """Test caching functionality."""
    
    def test_cache_result_caches_value(self):
        """Test that cache_result decorator caches return values."""
        call_count = 0
        
        @cache_result(ttl=60)
        def expensive_function(x):
            nonlocal call_count
            call_count += 1
            return x * 2
        
        # First call - should execute function
        result1 = expensive_function(5)
        assert result1 == 10
        assert call_count == 1
        
        # Second call - should use cache
        result2 = expensive_function(5)
        assert result2 == 10
        assert call_count == 1  # Not incremented
    
    def test_cache_result_respects_different_args(self):
        """Test that different arguments create different cache entries."""
        @cache_result(ttl=60)
        def add(a, b):
            return a + b
        
        result1 = add(1, 2)
        result2 = add(3, 4)
        
        assert result1 == 3
        assert result2 == 7
    
    def test_cache_expires(self):
        """Test that cache entries expire after TTL."""
        call_count = 0
        
        @cache_result(ttl=0.1)  # 0.1 second TTL
        def fast_expire():
            nonlocal call_count
            call_count += 1
            return "value"
        
        # First call
        fast_expire()
        assert call_count == 1
        
        # Wait for expiration
        time.sleep(0.2)
        
        # Should execute again
        fast_expire()
        assert call_count == 2
    
    def test_clear_cache_all(self):
        """Test clearing all cache entries."""
        @cache_result(ttl=60)
        def func1():
            return "value1"
        
        @cache_result(ttl=60)
        def func2():
            return "value2"
        
        func1()
        func2()
        
        # Cache should have entries
        stats_before = get_cache_stats()
        assert stats_before['size'] >= 2
        
        # Clear all
        clear_cache()
        
        # Cache should be empty
        stats_after = get_cache_stats()
        assert stats_after['size'] == 0
    
    def test_clear_cache_pattern(self):
        """Test clearing cache entries matching a pattern."""
        @cache_result(ttl=60)
        def user_func():
            return "user"
        
        @cache_result(ttl=60)
        def admin_func():
            return "admin"
        
        user_func()
        admin_func()
        
        # Clear only user functions
        clear_cache(pattern="user")
        
        # Cache should still have admin entry
        stats = get_cache_stats()
        assert stats['size'] >= 1
    
    def test_get_cache_stats(self):
        """Test getting cache statistics."""
        clear_cache()  # Start fresh
        
        @cache_result(ttl=60)
        def test_func(x):
            return x
        
        # Initially empty
        stats1 = get_cache_stats()
        assert stats1['size'] == 0
        
        # Add some entries
        test_func(1)
        test_func(2)
        
        stats2 = get_cache_stats()
        assert stats2['size'] == 2
        assert stats2['entries'] == 2
        assert stats2['oldest'] is not None
        assert stats2['newest'] is not None


class TestTimingDecorator:
    """Test timing decorator."""
    
    def test_timing_decorator_measures_time(self, capsys):
        """Test that timing decorator measures execution time."""
        @timing_decorator
        def slow_function():
            time.sleep(0.01)
            return "done"
        
        result = slow_function()
        assert result == "done"
        
        # Timing info is printed if > 1s, so no output expected here
        captured = capsys.readouterr()
        assert "took" not in captured.out  # Too fast to print


class TestQueryOptimizer:
    """Test query optimizer."""
    
    def test_query_optimizer_add_indexes(self, test_db):
        """Test adding database indexes."""
        optimizer = QueryOptimizer()
        
        # This should not raise an error
        result = optimizer.add_indexes(test_db)
        # Result may be True or False depending on DB state
        assert isinstance(result, bool)


class TestPerformanceMonitor:
    """Test performance monitoring."""
    
    def test_record_metric(self):
        """Test recording a metric."""
        monitor = PerformanceMonitor()
        
        monitor.record('query_time', 0.5)
        monitor.record('query_time', 0.8)
        
        assert len(monitor.metrics['query_time']) == 2
    
    def test_get_average(self):
        """Test getting average metric value."""
        monitor = PerformanceMonitor()
        
        monitor.record('response_time', 100)
        monitor.record('response_time', 200)
        monitor.record('response_time', 300)
        
        avg = monitor.get_average('response_time')
        assert avg == 200
    
    def test_get_average_time_window(self):
        """Test getting average over time window."""
        monitor = PerformanceMonitor()
        
        # Record old metric (will be outside window)
        monitor.metrics['test'] = [{
            'value': 10,
            'timestamp': datetime.now() - timedelta(seconds=400)
        }]
        
        # Record recent metrics
        monitor.record('test', 20)
        monitor.record('test', 30)
        
        # Average should only include recent values
        avg = monitor.get_average('test', window_seconds=300)
        assert avg == 25  # (20 + 30) / 2
    
    def test_get_stats(self):
        """Test getting metric statistics."""
        monitor = PerformanceMonitor()
        
        monitor.record('latency', 10)
        monitor.record('latency', 20)
        monitor.record('latency', 30)
        
        stats = monitor.get_stats('latency')
        
        assert stats['count'] == 3
        assert stats['min'] == 10
        assert stats['max'] == 30
        assert stats['avg'] == 20
        assert stats['last'] == 30
    
    def test_get_stats_empty(self):
        """Test getting stats for non-existent metric."""
        monitor = PerformanceMonitor()
        
        stats = monitor.get_stats('nonexistent')
        assert stats == {}


class TestBatchInsert:
    """Test batch insert functionality."""
    
    def test_batch_insert(self, test_db):
        """Test batch inserting items."""
        from src.models.database import Genre
        
        items = [
            {'name': f'Genre{i}', 'description': f'Desc{i}'}
            for i in range(10)
        ]
        
        inserted = batch_insert(test_db, Genre, items, batch_size=3)
        
        assert inserted == 10
        assert test_db.query(Genre).count() >= 10


class TestPagination:
    """Test pagination optimization."""
    
    def test_optimize_query_for_pagination(self, test_db):
        """Test query pagination optimization."""
        from src.models.database import Game
        
        # Add some test games
        for i in range(25):
            game = Game(
                steam_appid=1000 + i,
                name=f'Test Game {i}'
            )
            test_db.add(game)
        test_db.commit()
        
        # Test pagination
        query = test_db.query(Game)
        optimized, total = optimize_query_for_pagination(query, page=1, per_page=10)
        
        results = optimized.all()
        assert len(results) <= 10
        assert total >= 25


class TestPrecomputedAggregates:
    """Test precomputed aggregates."""
    
    def test_precompute_aggregates(self, test_db):
        """Test precomputing aggregates."""
        from src.models.database import Game, Genre
        
        # Add some test data
        genre = Genre(name='TestGenre')
        test_db.add(genre)
        
        game = Game(steam_appid=9999, name='Test Game', windows=True)
        test_db.add(game)
        test_db.commit()
        
        # Compute aggregates
        aggregates = precompute_aggregates(test_db, force=True)
        
        assert 'total_games' in aggregates
        assert 'total_genres' in aggregates
        assert 'platform_counts' in aggregates
        assert aggregates['total_games'] >= 1
    
    def test_precompute_aggregates_uses_cache(self, test_db):
        """Test that precomputed aggregates use cache."""
        # First call
        agg1 = precompute_aggregates(test_db, force=True)
        time1 = agg1['computed_at']
        
        # Second call (should use cache)
        time.sleep(0.1)
        agg2 = precompute_aggregates(test_db, force=False)
        time2 = agg2['computed_at']
        
        # Should be same (from cache)
        assert time1 == time2
    
    def test_precompute_aggregates_force_refresh(self, test_db):
        """Test forcing aggregate refresh."""
        # First call
        agg1 = precompute_aggregates(test_db, force=True)
        time1 = agg1['computed_at']
        
        # Wait a bit
        time.sleep(0.1)
        
        # Force refresh
        agg2 = precompute_aggregates(test_db, force=True)
        time2 = agg2['computed_at']
        
        # Should be different (forced refresh)
        assert time1 != time2
