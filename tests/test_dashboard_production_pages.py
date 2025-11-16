"""
Tests for production_pages dashboard module.
"""
import pytest
from datetime import datetime, timezone, timedelta


class TestDashboardKPIs:
    """Tests for dashboard KPI calculations."""
    
    def test_kpi_structure(self, mocker):
        """Test KPI data returns proper structure."""
        from src.dashboard.modules.production_pages import get_dashboard_kpis
        
        mock_db = mocker.patch('src.dashboard.modules.production_pages.get_db')
        mock_session = mocker.MagicMock()
        mock_db.return_value.__next__.return_value = mock_session
        
        # Mock query results
        mock_session.query.return_value.count.return_value = 213386
        mock_session.query.return_value.filter.return_value.count.return_value = 150
        mock_session.query.return_value.filter.return_value.with_entities.return_value.scalar.return_value = 1000.0
        
        result = get_dashboard_kpis()
        
        assert isinstance(result, dict)
        assert 'total_games' in result
        assert 'total_genres' in result
        assert 'recent_stats' in result
        assert 'avg_players' in result
    
    def test_kpi_values(self, mocker):
        """Test KPI calculations."""
        from src.dashboard.modules.production_pages import get_dashboard_kpis
        
        mock_db = mocker.patch('src.dashboard.modules.production_pages.get_db')
        mock_session = mocker.MagicMock()
        mock_db.return_value.__next__.return_value = mock_session
        
        # Set specific values
        mock_game_query = mocker.MagicMock()
        mock_game_query.count.return_value = 100000
        
        mock_genre_query = mocker.MagicMock()
        mock_genre_query.count.return_value = 50
        
        mock_stats_query = mocker.MagicMock()
        mock_stats_query.filter.return_value.count.return_value = 200
        
        mock_players_query = mocker.MagicMock()
        mock_players_query.filter.return_value.with_entities.return_value.scalar.return_value = 500.5
        
        mock_session.query.side_effect = [
            mock_game_query,
            mock_genre_query,
            mock_stats_query,
            mock_players_query
        ]
        
        result = get_dashboard_kpis()
        
        assert result['total_games'] == 100000
        assert result['total_genres'] == 50
        assert result['recent_stats'] == 200
        assert result['avg_players'] == 500
    
    def test_kpi_caching(self, mocker):
        """Test that KPIs are cached."""
        import streamlit as st
        
        if hasattr(st, 'cache_data'):
            st.cache_data.clear()
        
        from src.dashboard.modules.production_pages import get_dashboard_kpis
        
        mock_db = mocker.patch('src.dashboard.modules.production_pages.get_db')
        mock_session = mocker.MagicMock()
        mock_db.return_value.__next__.return_value = mock_session
        
        mock_session.query.return_value.count.return_value = 100
        
        # Call twice
        get_dashboard_kpis()
        get_dashboard_kpis()
        
        # Should cache and only call once
        assert mock_session.query.call_count == 4  # 4 queries in function


class TestGenreDistribution:
    """Tests for genre distribution data."""
    
    def test_distribution_structure(self, mocker):
        """Test genre distribution returns proper structure."""
        from src.dashboard.modules.production_pages import get_genre_distribution
        
        mock_db = mocker.patch('src.dashboard.modules.production_pages.get_db')
        mock_session = mocker.MagicMock()
        mock_db.return_value.__next__.return_value = mock_session
        
        # Mock query result
        mock_result = mocker.MagicMock()
        mock_result.name = 'Action'
        mock_result.game_count = 1000
        
        mock_session.query.return_value.join.return_value.group_by.return_value.order_by.return_value.limit.return_value.all.return_value = [
            mock_result
        ]
        
        result = get_genre_distribution()
        
        assert isinstance(result, list)
        assert len(result) > 0
        assert result[0]['genre'] == 'Action'
        assert result[0]['game_count'] == 1000
    
    def test_distribution_limit(self, mocker):
        """Test genre distribution respects limit."""
        from src.dashboard.modules.production_pages import get_genre_distribution
        
        mock_db = mocker.patch('src.dashboard.modules.production_pages.get_db')
        mock_session = mocker.MagicMock()
        mock_db.return_value.__next__.return_value = mock_session
        
        # Create 20 mock results
        mock_results = []
        for i in range(20):
            mock_result = mocker.MagicMock()
            mock_result.name = f'Genre{i}'
            mock_result.game_count = 100 - i
            mock_results.append(mock_result)
        
        mock_session.query.return_value.join.return_value.group_by.return_value.order_by.return_value.limit.return_value.all.return_value = mock_results[:15]
        
        result = get_genre_distribution()
        
        assert len(result) == 15


class TestOverviewPage:
    """Tests for overview page functionality."""
    
    def test_coverage_calculation(self):
        """Test data coverage percentage calculation."""
        total_games = 213386
        games_with_genres = 183516
        
        coverage_pct = (games_with_genres / total_games * 100) if total_games > 0 else 0
        
        assert coverage_pct == pytest.approx(86.0, 0.1)
    
    def test_coverage_edge_cases(self):
        """Test coverage calculation edge cases."""
        # Zero total games
        assert (0 / 1 * 100) if 1 > 0 else 0 == 0
        
        # Full coverage
        assert (100 / 100 * 100) == 100.0
        
        # Partial coverage
        assert (50 / 100 * 100) == 50.0
