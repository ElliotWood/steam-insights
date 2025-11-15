"""
Tests for Kaggle Dataset Importer

Tests cover:
- Public dataset discovery
- CSV/JSON parsing
- DataFrame import
- SteamSpy API integration
- Column mapping detection
- Error handling
"""

import pytest
import pandas as pd
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock
import json
import tempfile
from pathlib import Path

from src.utils.kaggle_importer import KaggleDatasetImporter
from src.models.database import Game, PlayerStats


@pytest.fixture
def kaggle_importer(test_db):
    """Create a KaggleDatasetImporter instance for testing."""
    return KaggleDatasetImporter(test_db)


@pytest.fixture
def sample_csv_data():
    """Sample CSV data for testing."""
    return pd.DataFrame({
        'appid': [730, 570, 440],
        'name': ['Counter-Strike 2', 'Dota 2', 'Team Fortress 2'],
        'price': [0, 0, 0],
        'release_date': ['2012-08-21', '2013-07-09', '2007-10-10'],
    })


@pytest.fixture
def sample_steamspy_data():
    """Sample SteamSpy API data for testing."""
    return {
        '730': {
            'name': 'Counter-Strike 2',
            'owners': '100000000-200000000',
            'players_forever': 5000000,
            'average_forever': 800000,
        },
        '570': {
            'name': 'Dota 2',
            'owners': '50000000-100000000',
            'players_forever': 3000000,
            'average_forever': 500000,
        },
    }


class TestDatasetDiscovery:
    """Test public dataset discovery and listing."""
    
    def test_list_available_datasets(self, kaggle_importer):
        """Test listing available public datasets."""
        datasets = kaggle_importer.list_available_datasets()
        
        assert isinstance(datasets, list)
        assert len(datasets) > 0
        
        # Check dataset structure
        for dataset in datasets:
            assert 'name' in dataset
            assert 'url' in dataset
            assert 'format' in dataset
            assert 'description' in dataset
            assert 'accessible' in dataset
    
    @patch('requests.head')
    def test_dataset_accessibility_check(self, mock_head, kaggle_importer):
        """Test checking if datasets are accessible."""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_head.return_value = mock_response
        
        datasets = kaggle_importer.list_available_datasets()
        
        # All should be marked as accessible with successful mock
        accessible_count = sum(1 for d in datasets if d['accessible'])
        assert accessible_count > 0
    
    @patch('requests.head')
    def test_dataset_inaccessible(self, mock_head, kaggle_importer):
        """Test handling of inaccessible datasets."""
        # Mock failed response
        mock_head.side_effect = Exception("Connection error")
        
        datasets = kaggle_importer.list_available_datasets()
        
        # All should be marked as inaccessible
        assert all(not d['accessible'] for d in datasets)


class TestDatasetDownload:
    """Test dataset download functionality."""
    
    @patch('requests.get')
    def test_download_dataset_success(self, mock_get, kaggle_importer):
        """Test successful dataset download."""
        # Mock successful download
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.iter_content = Mock(return_value=[b'test data'])
        mock_get.return_value = mock_response
        
        file_path = kaggle_importer.download_dataset(
            "https://example.com/data.csv",
            format="csv"
        )
        
        assert file_path is not None
        assert file_path.exists()
        assert file_path.suffix == ".csv"
        
        # Cleanup
        file_path.unlink()
    
    @patch('requests.get')
    def test_download_dataset_failure(self, mock_get, kaggle_importer):
        """Test handling of failed downloads."""
        # Mock failed download
        mock_get.side_effect = Exception("Network error")
        
        file_path = kaggle_importer.download_dataset(
            "https://example.com/data.csv"
        )
        
        assert file_path is None


class TestDataParsing:
    """Test CSV and JSON parsing functionality."""
    
    def test_parse_csv_dataset(self, kaggle_importer, sample_csv_data):
        """Test parsing CSV dataset."""
        # Create temporary CSV file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            sample_csv_data.to_csv(f.name, index=False)
            temp_path = Path(f.name)
        
        try:
            df = kaggle_importer.parse_csv_dataset(temp_path)
            
            assert df is not None
            assert len(df) == 3
            assert 'appid' in df.columns
            assert 'name' in df.columns
        finally:
            temp_path.unlink()
    
    def test_parse_csv_invalid_file(self, kaggle_importer):
        """Test handling of invalid CSV file."""
        df = kaggle_importer.parse_csv_dataset(Path("/nonexistent/file.csv"))
        assert df is None
    
    @patch('requests.get')
    def test_parse_json_dataset_from_url(self, mock_get, kaggle_importer):
        """Test parsing JSON from URL."""
        mock_response = Mock()
        mock_response.json.return_value = {'730': {'name': 'CS2'}}
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        data = kaggle_importer.parse_json_dataset("https://api.example.com/data.json")
        
        assert data is not None
        assert '730' in data
        assert data['730']['name'] == 'CS2'
    
    def test_parse_json_dataset_from_file(self, kaggle_importer):
        """Test parsing JSON from file."""
        # Create temporary JSON file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({'test': 'data'}, f)
            temp_path = Path(f.name)
        
        try:
            data = kaggle_importer.parse_json_dataset(temp_path)
            
            assert data is not None
            assert data['test'] == 'data'
        finally:
            temp_path.unlink()


class TestColumnMapping:
    """Test automatic column mapping detection."""
    
    def test_detect_column_mapping_standard(self, kaggle_importer):
        """Test detecting standard column names."""
        df = pd.DataFrame({
            'appid': [1, 2, 3],
            'name': ['Game 1', 'Game 2', 'Game 3'],
            'price': [10, 20, 30],
        })
        
        mapping = kaggle_importer._detect_column_mapping(df)
        
        assert 'app_id' in mapping
        assert mapping['app_id'] == 'appid'
        assert 'name' in mapping
        assert mapping['name'] == 'name'
    
    def test_detect_column_mapping_variants(self, kaggle_importer):
        """Test detecting variant column names."""
        df = pd.DataFrame({
            'steam_appid': [1, 2, 3],
            'game_name': ['Game 1', 'Game 2', 'Game 3'],
            'final_price': [10, 20, 30],
        })
        
        mapping = kaggle_importer._detect_column_mapping(df)
        
        assert 'app_id' in mapping
        assert mapping['app_id'] == 'steam_appid'
        assert 'name' in mapping
        assert mapping['name'] == 'game_name'
        assert 'price' in mapping
        assert mapping['price'] == 'final_price'


class TestDataframeImport:
    """Test importing data from DataFrames."""
    
    def test_import_from_dataframe_new_games(self, kaggle_importer, sample_csv_data, test_db):
        """Test importing new games from DataFrame."""
        stats = kaggle_importer.import_from_dataframe(sample_csv_data)
        
        assert stats['games_imported'] == 3
        assert stats['games_updated'] == 0
        assert stats['games_skipped'] == 0
        
        # Verify games in database
        games = test_db.query(Game).all()
        assert len(games) == 3
        assert any(g.steam_appid == 730 for g in games)
    
    def test_import_from_dataframe_existing_games(self, kaggle_importer, sample_csv_data, test_db):
        """Test updating existing games from DataFrame."""
        # First import
        kaggle_importer.import_from_dataframe(sample_csv_data)
        
        # Create new importer for second import
        kaggle_importer2 = KaggleDatasetImporter(test_db)
        
        # Modify data and import again
        sample_csv_data['name'] = sample_csv_data['name'] + ' Updated'
        stats = kaggle_importer2.import_from_dataframe(sample_csv_data)
        
        assert stats['games_updated'] == 3
        assert stats['games_imported'] == 0
        
        # Verify update
        game = test_db.query(Game).filter(Game.steam_appid == 730).first()
        assert 'Updated' in game.name
    
    def test_import_from_dataframe_custom_mapping(self, kaggle_importer, test_db):
        """Test import with custom column mapping."""
        df = pd.DataFrame({
            'id': [123, 456],
            'title': ['Game A', 'Game B'],
        })
        
        mapping = {'app_id': 'id', 'name': 'title'}
        stats = kaggle_importer.import_from_dataframe(df, column_mapping=mapping)
        
        assert stats['games_imported'] == 2
        
        game = test_db.query(Game).filter(Game.steam_appid == 123).first()
        assert game is not None
        assert game.name == 'Game A'


class TestSteamSpyIntegration:
    """Test SteamSpy API integration."""
    
    @patch('src.utils.kaggle_importer.KaggleDatasetImporter.parse_json_dataset')
    def test_import_from_steamspy_new_games(self, mock_parse, kaggle_importer, sample_steamspy_data, test_db):
        """Test importing new games from SteamSpy."""
        mock_parse.return_value = sample_steamspy_data
        
        stats = kaggle_importer.import_from_steamspy()
        
        assert stats['games_imported'] == 2
        
        # Verify game and stats in database
        game = test_db.query(Game).filter(Game.steam_appid == 730).first()
        assert game is not None
        
        player_stats = test_db.query(PlayerStats).filter(
            PlayerStats.game_id == game.id
        ).first()
        assert player_stats is not None
        assert player_stats.estimated_owners == 150000000  # Average of range
    
    @patch('src.utils.kaggle_importer.KaggleDatasetImporter.parse_json_dataset')
    def test_import_from_steamspy_existing_games(self, mock_parse, kaggle_importer, sample_steamspy_data, test_db):
        """Test updating existing games with SteamSpy data."""
        # Create existing game
        game = Game(steam_appid=730, name='Counter-Strike 2')
        test_db.add(game)
        test_db.commit()
        
        mock_parse.return_value = sample_steamspy_data
        
        stats = kaggle_importer.import_from_steamspy()
        
        assert stats['games_updated'] >= 1
        
        # Verify stats were added
        player_stats = test_db.query(PlayerStats).filter(
            PlayerStats.game_id == game.id
        ).first()
        assert player_stats is not None
        assert player_stats.estimated_owners > 0
    
    @patch('src.utils.kaggle_importer.KaggleDatasetImporter.parse_json_dataset')
    def test_import_from_steamspy_failure(self, mock_parse, kaggle_importer):
        """Test handling of SteamSpy API failure."""
        mock_parse.return_value = None
        
        stats = kaggle_importer.import_from_steamspy()
        
        assert 'error' in stats


class TestImportReporting:
    """Test import report generation."""
    
    def test_get_import_report(self, kaggle_importer):
        """Test generating import report."""
        # Set up some stats
        kaggle_importer.import_stats.update({
            'games_imported': 100,
            'games_updated': 50,
            'games_skipped': 10,
            'errors': ['Error 1', 'Error 2'],
            'start_time': datetime.now(),
            'end_time': datetime.now(),
        })
        
        report = kaggle_importer.get_import_report()
        
        assert 'KAGGLE DATASET IMPORT REPORT' in report
        assert '100' in report  # games_imported
        assert '50' in report   # games_updated
        assert 'Error 1' in report
    
    def test_get_import_report_no_errors(self, kaggle_importer):
        """Test report with no errors."""
        kaggle_importer.import_stats.update({
            'games_imported': 10,
            'games_updated': 0,
            'games_skipped': 0,
            'errors': [],
        })
        
        report = kaggle_importer.get_import_report()
        
        assert 'KAGGLE DATASET IMPORT REPORT' in report
        assert 'Errors:          0' in report


class TestErrorHandling:
    """Test error handling and edge cases."""
    
    def test_import_with_missing_app_id(self, kaggle_importer, test_db):
        """Test handling of rows without app_id."""
        df = pd.DataFrame({
            'name': ['Game 1', 'Game 2'],
            'price': [10, 20],
        })
        
        stats = kaggle_importer.import_from_dataframe(df)
        
        # Should skip all rows without app_id
        assert stats['games_skipped'] == 2
        assert stats['games_imported'] == 0
    
    def test_import_with_invalid_data(self, kaggle_importer, test_db):
        """Test handling of invalid data in rows."""
        df = pd.DataFrame({
            'appid': [730, None, 'invalid'],  # Mix of valid and invalid
            'name': ['Game 1', 'Game 2', 'Game 3'],
        })
        
        # Should handle errors gracefully
        stats = kaggle_importer.import_from_dataframe(df)
        
        # At least one should succeed, others should error
        assert stats['games_imported'] >= 1
        assert len(stats['errors']) > 0
    
    def test_import_many_errors_stops(self, kaggle_importer, test_db):
        """Test that import stops after too many errors."""
        # Create DataFrame with 200 invalid rows
        df = pd.DataFrame({
            'appid': ['invalid'] * 200,
            'name': [f'Game {i}' for i in range(200)],
        })
        
        stats = kaggle_importer.import_from_dataframe(df)
        
        # Should stop before processing all rows
        assert len(stats['errors']) <= 101  # Stops at 100 errors + message
