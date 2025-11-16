"""
Tests for analysis_pages dashboard module.
"""
import pytest
import pandas as pd


class TestGenreSaturation:
    """Tests for genre saturation analysis."""
    
    def test_genre_saturation_returns_list(self, mocker):
        """Test that genre saturation returns proper data."""
        mock_db = mocker.patch(
            'src.dashboard.modules.analysis_pages.get_db'
        )
        mock_analyzer = mocker.patch(
            'src.dashboard.modules.analysis_pages.MarketInsightsAnalyzer'
        )
        
        mock_analyzer.return_value.analyze_genre_saturation.return_value = [
            {'genre': 'Action', 'game_count': 1000, 'opportunity': 'High'}
        ]
        
        from src.dashboard.modules.analysis_pages import get_genre_saturation_analysis
        
        result = get_genre_saturation_analysis()
        
        assert isinstance(result, list)
        if len(result) > 0:
            assert 'genre' in result[0]
            assert 'game_count' in result[0]


class TestGenreStats:
    """Tests for genre statistics."""
    
    def test_genre_stats_structure(self, mocker):
        """Test genre stats returns proper structure."""
        from src.dashboard.modules.analysis_pages import get_genre_stats
        
        mock_db = mocker.patch('src.dashboard.modules.analysis_pages.get_db')
        mock_session = mocker.MagicMock()
        mock_db.return_value.__next__.return_value = mock_session
        
        # Mock query result
        mock_result = mocker.MagicMock()
        mock_result.name = 'Action'
        mock_result.game_count = 500
        mock_result.avg_owners = 10000
        
        mock_session.query.return_value.join.return_value.outerjoin.return_value.group_by.return_value.order_by.return_value.limit.return_value.all.return_value = [
            mock_result
        ]
        
        result = get_genre_stats()
        
        assert isinstance(result, list)
        assert len(result) > 0
        assert result[0]['genre'] == 'Action'
        assert result[0]['game_count'] == 500
        assert result[0]['avg_owners'] == 10000
    
    def test_genre_stats_empty_result(self, mocker):
        """Test handling of empty genre stats."""
        from src.dashboard.modules.analysis_pages import get_genre_stats
        
        mock_db = mocker.patch('src.dashboard.modules.analysis_pages.get_db')
        mock_session = mocker.MagicMock()
        mock_db.return_value.__next__.return_value = mock_session
        
        mock_session.query.return_value.join.return_value.outerjoin.return_value.group_by.return_value.order_by.return_value.limit.return_value.all.return_value = []
        
        result = get_genre_stats()
        
        assert isinstance(result, list)
        assert len(result) == 0


class TestTagStats:
    """Tests for tag statistics."""
    
    def test_tag_stats_structure(self, mocker):
        """Test tag stats returns proper structure."""
        from src.dashboard.modules.analysis_pages import get_tag_stats
        
        mock_db = mocker.patch('src.dashboard.modules.analysis_pages.get_db')
        mock_session = mocker.MagicMock()
        mock_db.return_value.__next__.return_value = mock_session
        
        # Mock query result
        mock_result = mocker.MagicMock()
        mock_result.name = 'Singleplayer'
        mock_result.game_count = 800
        mock_result.avg_owners = 15000
        
        mock_session.query.return_value.join.return_value.outerjoin.return_value.group_by.return_value.order_by.return_value.limit.return_value.all.return_value = [
            mock_result
        ]
        
        result = get_tag_stats()
        
        assert isinstance(result, list)
        assert len(result) > 0
        assert result[0]['tag'] == 'Singleplayer'
        assert result[0]['game_count'] == 800
    
    def test_tag_stats_caching(self, mocker):
        """Test that tag stats are cached."""
        import streamlit as st
        
        if hasattr(st, 'cache_data'):
            st.cache_data.clear()
        
        from src.dashboard.modules.analysis_pages import get_tag_stats
        
        mock_db = mocker.patch('src.dashboard.modules.analysis_pages.get_db')
        mock_session = mocker.MagicMock()
        mock_db.return_value.__next__.return_value = mock_session
        
        mock_session.query.return_value.join.return_value.outerjoin.return_value.group_by.return_value.order_by.return_value.limit.return_value.all.return_value = []
        
        # Call twice
        get_tag_stats()
        get_tag_stats()
        
        # Should only query once due to caching
        assert mock_session.query.call_count == 1


class TestRisingTrends:
    """Tests for rising trends analysis."""
    
    def test_trend_data_filtering(self):
        """Test trend data can be filtered."""
        df = pd.DataFrame({
            'genre': ['Action', 'Indie', 'RPG'],
            'game_count': [100, 50, 25],
            'avg_owners': [10000, 5000, 2500]
        })
        
        min_games = 30
        filtered = df[df['game_count'] >= min_games]
        
        assert len(filtered) == 2
        assert 'RPG' not in filtered['genre'].values
    
    def test_empty_trend_data(self):
        """Test handling of empty trend data."""
        df = pd.DataFrame()
        
        assert df.empty
        assert len(df) == 0
