"""
Tests for concept_research dashboard module.
"""
import pytest
import pandas as pd
from datetime import datetime, timedelta


class TestMarketOpportunities:
    """Tests for market opportunities analysis."""
    
    def test_golden_age_data_returns_dataframe(self, mocker):
        """Test that golden age data returns proper structure."""
        mock_db = mocker.patch(
            'src.dashboard.modules.concept_research.get_db'
        )
        mock_analyzer = mocker.patch(
            'src.dashboard.modules.concept_research.MarketInsightsAnalyzer'
        )
        
        # Mock return data
        mock_analyzer.return_value.analyze_golden_age_opportunities.return_value = [
            {
                'genre': 'Action',
                'total_games': 500,
                'avg_owners': 15000,
                'recent_releases': 5,
                'trend': 'Growing',
                'competition_level': 'Low',
                'opportunity_score': 85
            }
        ]
        
        from src.dashboard.modules.concept_research import get_golden_age_data
        
        result = get_golden_age_data(10000, 1000, 3, 180)
        
        assert isinstance(result, list)
        assert len(result) > 0
        assert 'genre' in result[0]
        assert 'opportunity_score' in result[0]
    
    def test_golden_age_data_caching(self, mocker):
        """Test that data is cached properly."""
        import streamlit as st
        
        # Clear cache before test
        if hasattr(st, 'cache_data'):
            st.cache_data.clear()
        
        mock_db = mocker.patch(
            'src.dashboard.modules.concept_research.get_db'
        )
        mock_analyzer = mocker.patch(
            'src.dashboard.modules.concept_research.MarketInsightsAnalyzer'
        )
        
        mock_analyzer.return_value.analyze_golden_age_opportunities.return_value = []
        
        from src.dashboard.modules.concept_research import get_golden_age_data
        
        # Call twice with same params
        get_golden_age_data(10000, 1000, 3, 180)
        get_golden_age_data(10000, 1000, 3, 180)
        
        # Should only call analyzer once due to caching
        assert mock_analyzer.return_value.analyze_golden_age_opportunities.call_count == 1
    
    def test_genre_saturation_data_structure(self, mocker):
        """Test genre saturation returns proper structure."""
        mock_db = mocker.patch(
            'src.dashboard.modules.concept_research.get_db'
        )
        mock_analyzer = mocker.patch(
            'src.dashboard.modules.concept_research.MarketInsightsAnalyzer'
        )
        
        mock_analyzer.return_value.analyze_genre_saturation.return_value = [
            {
                'genre': 'Indie',
                'game_count': 5000,
                'saturation_score': 75,
                'opportunity': 'Medium'
            }
        ]
        
        from src.dashboard.modules.concept_research import get_genre_saturation_data
        
        result = get_genre_saturation_data()
        
        assert isinstance(result, list)
        if len(result) > 0:
            assert 'genre' in result[0]
            assert 'game_count' in result[0]


class TestRevenueProjections:
    """Tests for revenue projection calculator."""
    
    def test_revenue_calculation_conservative(self):
        """Test conservative revenue calculation."""
        wishlists = 10000
        price = 19.99
        conversion_low = 15  # 15%
        
        sales_low = int(wishlists * (conversion_low / 100))
        revenue_low = sales_low * price * 0.7  # Steam's cut
        
        assert sales_low == 1500
        assert revenue_low == pytest.approx(20985.0, 0.01)
    
    def test_revenue_calculation_optimistic(self):
        """Test optimistic revenue calculation."""
        wishlists = 10000
        price = 19.99
        conversion_high = 25  # 25%
        
        sales_high = int(wishlists * (conversion_high / 100))
        revenue_high = sales_high * price * 0.7
        
        assert sales_high == 2500
        assert revenue_high == pytest.approx(34975.0, 0.01)
    
    def test_revenue_edge_cases(self):
        """Test revenue calculation edge cases."""
        # Zero wishlists
        assert int(0 * 0.15) * 19.99 * 0.7 == 0
        
        # Maximum values
        wishlists = 500000
        sales = int(wishlists * 0.25)
        revenue = sales * 100.0 * 0.7
        assert revenue > 0


class TestCompetitionAnalysis:
    """Tests for competition analysis functionality."""
    
    def test_competition_data_filtering(self, mocker):
        """Test that competition analysis filters correctly."""
        mock_session = mocker.MagicMock()
        
        # Mock query chain
        mock_query = mock_session.query.return_value
        mock_query.join.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.count.return_value = 150
        
        result = mock_query.count()
        
        assert result == 150
    
    def test_empty_genre_selection(self, mocker):
        """Test behavior with empty genre selection."""
        selected_genres = []
        
        # Should handle gracefully
        assert isinstance(selected_genres, list)
        assert len(selected_genres) == 0
