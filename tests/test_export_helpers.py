"""
Tests for dashboard export functionality.
Tests CSV and Excel export helpers used across dashboard pages.
"""
import pytest
import pandas as pd
from datetime import datetime
from src.utils.export_helpers import (
    create_csv_download,
    create_excel_download,
    add_export_buttons
)


class TestCSVExport:
    """Test CSV export functionality."""
    
    def test_create_csv_basic(self):
        """Test basic CSV creation."""
        df = pd.DataFrame({
            'Name': ['Game1', 'Game2'],
            'Genre': ['Action', 'RPG'],
            'Owners': [10000, 50000]
        })
        
        csv_data, filename = create_csv_download(df, "test_export")
        
        assert csv_data is not None
        assert 'Game1' in csv_data
        assert 'Game2' in csv_data
        assert filename.startswith('test_export_')
        assert filename.endswith('.csv')
    
    def test_csv_filename_timestamp(self):
        """Test CSV filename includes timestamp."""
        df = pd.DataFrame({'col': [1, 2, 3]})
        _, filename = create_csv_download(df, "data")
        
        # Extract timestamp part
        timestamp_str = filename.replace('data_', '').replace('.csv', '')
        
        # Should be parseable as datetime
        try:
            datetime.strptime(timestamp_str, '%Y%m%d_%H%M%S')
            assert True
        except ValueError:
            assert False, "Timestamp format incorrect"
    
    def test_csv_empty_dataframe(self):
        """Test CSV export with empty DataFrame."""
        df = pd.DataFrame()
        csv_data, filename = create_csv_download(df, "empty")
        
        assert csv_data is not None
        assert filename.endswith('.csv')
    
    def test_csv_special_characters(self):
        """Test CSV handles special characters."""
        df = pd.DataFrame({
            'Name': ['Game, with comma', 'Game "quoted"'],
            'Genre': ['Action', 'RPG']
        })
        
        csv_data, _ = create_csv_download(df, "special")
        
        assert 'Game, with comma' in csv_data
        assert 'Game "quoted"' in csv_data


class TestExcelExport:
    """Test Excel export functionality."""
    
    def test_create_excel_basic(self):
        """Test basic Excel creation."""
        df = pd.DataFrame({
            'Name': ['Game1', 'Game2'],
            'Owners': [10000, 50000]
        })
        
        excel_data, filename = create_excel_download(df, "test_export")
        
        assert excel_data is not None
        assert len(excel_data) > 0
        assert filename.startswith('test_export_')
        assert filename.endswith('.xlsx')
    
    def test_excel_filename_format(self):
        """Test Excel filename format."""
        df = pd.DataFrame({'col': [1]})
        _, filename = create_excel_download(df, "report")
        
        assert 'report_' in filename
        assert '.xlsx' in filename
    
    def test_excel_empty_dataframe(self):
        """Test Excel with empty DataFrame."""
        df = pd.DataFrame()
        excel_data, _ = create_excel_download(df, "empty")
        
        assert excel_data is not None


class TestExportHelpers:
    """Test export helper integration."""
    
    def test_add_export_buttons_with_data(self, mocker):
        """Test add_export_buttons with valid data."""
        # Mock streamlit components
        mock_st = mocker.MagicMock()
        mocker.patch('src.utils.export_helpers.st', mock_st)
        
        df = pd.DataFrame({
            'col1': [1, 2, 3],
            'col2': ['a', 'b', 'c']
        })
        
        from src.utils.export_helpers import add_export_buttons
        add_export_buttons(df, "test_data")
        
        # Should create columns and download buttons
        assert mock_st.columns.called
        assert mock_st.download_button.called
    
    def test_add_export_buttons_empty_data(self, mocker):
        """Test add_export_buttons with empty data."""
        mock_st = mocker.MagicMock()
        mocker.patch('src.utils.export_helpers.st', mock_st)
        
        from src.utils.export_helpers import add_export_buttons
        add_export_buttons(None, "test")
        
        # Should show info message
        assert mock_st.info.called
    
    def test_export_large_dataset(self):
        """Test export with large dataset."""
        # Create DataFrame with 10K rows
        df = pd.DataFrame({
            'id': range(10000),
            'value': [i * 2 for i in range(10000)]
        })
        
        csv_data, _ = create_csv_download(df, "large_data")
        
        assert csv_data is not None
        assert len(csv_data) > 100000  # Should be substantial


class TestExportIntegration:
    """Integration tests for export across dashboard."""
    
    def test_market_opportunities_export_format(self):
        """Test market opportunities data exports correctly."""
        # Simulate market opportunities DataFrame
        df = pd.DataFrame({
            'genre': ['Action', 'RPG', 'Strategy'],
            'total_games': [1000, 500, 300],
            'avg_owners': [50000, 100000, 75000],
            'opportunity_score': [85, 92, 78]
        })
        
        csv_data, _ = create_csv_download(df, "market_opportunities")
        
        # Verify all columns present
        assert 'genre' in csv_data
        assert 'total_games' in csv_data
        assert 'avg_owners' in csv_data
        assert 'opportunity_score' in csv_data
    
    def test_tag_analysis_export_format(self):
        """Test tag analysis data exports correctly."""
        df = pd.DataFrame({
            'Tag': ['Singleplayer', 'Multiplayer', 'Co-op'],
            'Games Using Tag': [50000, 30000, 15000]
        })
        
        csv_data, _ = create_csv_download(df, "popular_tags")
        
        assert 'Singleplayer' in csv_data
        assert '50000' in csv_data


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
