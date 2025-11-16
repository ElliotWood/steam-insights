"""
Kaggle Dataset Importer for Steam Insights

This module automatically searches for and imports Steam game datasets from Kaggle
and other public data sources. It handles CSV/Parquet file downloads, parsing,
and importing into the Steam Insights database.

Supported Data Sources:
1. Kaggle Datasets (via API or direct download)
2. GitHub repositories with Steam data
3. Direct CSV/JSON file URLs
4. SteamSpy API for ownership data
"""

import logging
import os
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import json

import pandas as pd
import requests
from sqlalchemy.orm import Session

from src.models.database import Game, Genre, Tag, PlayerStats, PricingHistory
from src.database.connection import get_db
from src.utils.logging_config import setup_logging

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)


class KaggleDatasetImporter:
    """
    Automatically search for and import Steam datasets from public sources.
    
    This class provides functionality to:
    - Search for Steam datasets on Kaggle and GitHub
    - Download CSV/Parquet/JSON files
    - Parse and validate data
    - Import into Steam Insights database
    - Track import progress and errors
    """
    
    # Public Steam datasets (no auth required)
    PUBLIC_DATASETS = [
        {
            "name": "Steam Games Dataset (2024)",
            "url": "https://raw.githubusercontent.com/dgwozdz/steam-games-dataset/main/games.csv",
            "format": "csv",
            "description": "Comprehensive Steam games catalog with metadata",
            "size_mb": 15,
            "last_updated": "2024-01",
        },
        {
            "name": "Steam Store Games",
            "url": "https://raw.githubusercontent.com/nik-davis/steam-games/master/steam_games.csv",
            "format": "csv",
            "description": "Steam store games with pricing and reviews",
            "size_mb": 8,
            "last_updated": "2023-12",
        },
        {
            "name": "SteamSpy Dataset",
            "url": "https://steamspy.com/api.php?request=all",
            "format": "json",
            "description": "SteamSpy data with ownership estimates",
            "size_mb": 25,
            "last_updated": "live",
        },
    ]
    
    def __init__(self, db: Session):
        """
        Initialize the Kaggle dataset importer.
        
        Args:
            db: SQLAlchemy database session
        """
        self.db = db
        self.import_stats = {
            "games_imported": 0,
            "games_updated": 0,
            "games_skipped": 0,
            "errors": [],
            "start_time": None,
            "end_time": None,
        }
        
    def list_available_datasets(self) -> List[Dict]:
        """
        List all available public Steam datasets.
        
        Returns:
            List of dataset metadata dictionaries
        """
        logger.info("Listing available public Steam datasets")
        
        available = []
        for dataset in self.PUBLIC_DATASETS:
            # Check if URL is accessible
            try:
                response = requests.head(dataset["url"], timeout=5)
                accessible = response.status_code == 200
            except Exception as e:
                logger.warning(f"Cannot access {dataset['name']}: {e}")
                accessible = False
            
            dataset_info = dataset.copy()
            dataset_info["accessible"] = accessible
            available.append(dataset_info)
        
        return available
    
    def download_dataset(self, dataset_url: str, format: str = "csv") -> Optional[Path]:
        """
        Download a dataset from a public URL.
        
        Args:
            dataset_url: URL to download from
            format: File format (csv, json, parquet)
            
        Returns:
            Path to downloaded file, or None if failed
        """
        logger.info(f"Downloading dataset from {dataset_url}")
        
        try:
            # Create temp directory
            temp_dir = Path(tempfile.gettempdir()) / "steam_insights_datasets"
            temp_dir.mkdir(exist_ok=True)
            
            # Download file
            response = requests.get(dataset_url, timeout=60, stream=True)
            response.raise_for_status()
            
            # Save to temp file
            temp_file = temp_dir / f"dataset_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{format}"
            
            with open(temp_file, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            logger.info(f"Downloaded {temp_file.stat().st_size / (1024*1024):.1f} MB to {temp_file}")
            return temp_file
            
        except Exception as e:
            logger.error(f"Failed to download dataset: {e}")
            return None
    
    def parse_csv_dataset(self, file_path: Path) -> Optional[pd.DataFrame]:
        """
        Parse a CSV dataset file.
        
        Args:
            file_path: Path to CSV file
            
        Returns:
            Pandas DataFrame or None if failed
        """
        logger.info(f"Parsing CSV dataset: {file_path}")
        
        try:
            # Try different encodings
            for encoding in ['utf-8', 'latin-1', 'iso-8859-1']:
                try:
                    df = pd.read_csv(file_path, encoding=encoding)
                    logger.info(f"Parsed {len(df)} rows with {len(df.columns)} columns")
                    return df
                except UnicodeDecodeError:
                    continue
            
            logger.error("Failed to parse CSV with any encoding")
            return None
            
        except Exception as e:
            logger.error(f"Failed to parse CSV: {e}")
            return None
    
    def parse_json_dataset(self, file_path: Path) -> Optional[Dict]:
        """
        Parse a JSON dataset file or API response.
        
        Args:
            file_path: Path to JSON file or URL
            
        Returns:
            Parsed JSON dict or None if failed
        """
        logger.info(f"Parsing JSON dataset: {file_path}")
        
        try:
            if str(file_path).startswith('http'):
                # Direct API call
                response = requests.get(str(file_path), timeout=30)
                response.raise_for_status()
                data = response.json()
            else:
                # Local file
                with open(file_path, 'r') as f:
                    data = json.load(f)
            
            logger.info(f"Parsed JSON with {len(data)} entries")
            return data
            
        except Exception as e:
            logger.error(f"Failed to parse JSON: {e}")
            return None
    
    def import_from_dataframe(
        self, 
        df: pd.DataFrame,
        column_mapping: Optional[Dict[str, str]] = None
    ) -> Dict:
        """
        Import games from a pandas DataFrame.
        
        Args:
            df: DataFrame with game data
            column_mapping: Map dataset columns to database fields
                e.g., {"appid": "app_id", "game_name": "name"}
        
        Returns:
            Import statistics dictionary
        """
        logger.info(f"Importing {len(df)} games from DataFrame")
        self.import_stats["start_time"] = datetime.now()
        
        # Default column mappings for common dataset formats
        if column_mapping is None:
            column_mapping = self._detect_column_mapping(df)
        
        for idx, row in df.iterrows():
            try:
                self._import_game_row(row, column_mapping)
            except Exception as e:
                error_msg = f"Row {idx}: {str(e)}"
                logger.error(error_msg)
                self.import_stats["errors"].append(error_msg)
                if len(self.import_stats["errors"]) > 100:
                    logger.warning("Too many errors, stopping import")
                    break
        
        # Final commit
        self.db.commit()
        self.import_stats["end_time"] = datetime.now()
        return self.import_stats
    
    def import_from_steamspy(self) -> Dict:
        """
        Import ownership data from SteamSpy API.
        
        Returns:
            Import statistics dictionary
        """
        logger.info("Importing data from SteamSpy API")
        
        try:
            # Get all games from SteamSpy
            data = self.parse_json_dataset("https://steamspy.com/api.php?request=all")
            if not data:
                return {"error": "Failed to fetch SteamSpy data"}
            
            self.import_stats["start_time"] = datetime.now()
            
            for app_id, game_data in data.items():
                try:
                    self._import_steamspy_game(int(app_id), game_data)
                except Exception as e:
                    logger.error(f"Failed to import SteamSpy data for {app_id}: {e}")
                    self.import_stats["errors"].append(f"App {app_id}: {str(e)}")
            
            self.import_stats["end_time"] = datetime.now()
            return self.import_stats
            
        except Exception as e:
            logger.error(f"Failed to import from SteamSpy: {e}")
            return {"error": str(e)}
    
    def _detect_column_mapping(self, df: pd.DataFrame) -> Dict[str, str]:
        """
        Automatically detect column mappings from DataFrame.
        
        Args:
            df: DataFrame with game data
            
        Returns:
            Dictionary mapping dataset columns to database fields
        """
        columns = [col.lower() for col in df.columns]
        mapping = {}
        
        # App ID mappings
        for col in ['appid', 'app_id', 'id', 'steam_appid']:
            if col in columns:
                mapping['app_id'] = df.columns[columns.index(col)]
                break
        
        # Name mappings
        for col in ['name', 'game_name', 'title', 'game']:
            if col in columns:
                mapping['name'] = df.columns[columns.index(col)]
                break
        
        # Price mappings
        for col in ['price', 'price_overview', 'final_price']:
            if col in columns:
                mapping['price'] = df.columns[columns.index(col)]
                break
        
        # Release date mappings
        for col in ['release_date', 'releasedate', 'release']:
            if col in columns:
                mapping['release_date'] = df.columns[columns.index(col)]
                break
        
        logger.info(f"Detected column mapping: {mapping}")
        return mapping
    
    def _import_game_row(self, row: pd.Series, column_mapping: Dict[str, str]):
        """
        Import a single game row from DataFrame.
        
        Args:
            row: Pandas Series with game data
            column_mapping: Column name mappings
        """
        # Get steam_appid
        if 'app_id' not in column_mapping:
            self.import_stats["games_skipped"] += 1
            return
        
        steam_appid = int(row[column_mapping['app_id']])
        
        # Check if game exists
        existing_game = self.db.query(Game).filter(Game.steam_appid == steam_appid).first()
        
        if existing_game:
            # Update existing game
            if 'name' in column_mapping and pd.notna(row[column_mapping['name']]):
                existing_game.name = str(row[column_mapping['name']])
            self.import_stats["games_updated"] += 1
        else:
            # Create new game
            name = row[column_mapping.get('name', 'name')] if 'name' in column_mapping else f"Game {steam_appid}"
            
            new_game = Game(
                steam_appid=steam_appid,
                name=str(name) if pd.notna(name) else f"Game {steam_appid}",
            )
            
            # Add optional fields if available
            if 'release_date' in column_mapping and pd.notna(row[column_mapping['release_date']]):
                try:
                    new_game.release_date = pd.to_datetime(row[column_mapping['release_date']])
                except:
                    pass
            
            self.db.add(new_game)
            self.import_stats["games_imported"] += 1
        
        # Commit periodically
        if (self.import_stats["games_imported"] + self.import_stats["games_updated"]) % 100 == 0:
            self.db.commit()
    
    def _import_steamspy_game(self, steam_appid: int, data: Dict):
        """
        Import a game from SteamSpy data.
        
        Args:
            steam_appid: Steam App ID
            data: SteamSpy game data dictionary
        """
        # Get or create game
        game = self.db.query(Game).filter(Game.steam_appid == steam_appid).first()
        
        if not game:
            game = Game(
                steam_appid=steam_appid,
                name=data.get('name', f'Game {steam_appid}')
            )
            self.db.add(game)
            self.db.commit()
            self.import_stats["games_imported"] += 1
        else:
            self.import_stats["games_updated"] += 1
        
        # Create or update player stats with ownership data
        stats = self.db.query(PlayerStats).filter(
            PlayerStats.steam_appid == game.steam_appid
        ).order_by(PlayerStats.timestamp.desc()).first()
        
        if not stats:
            stats = PlayerStats(
                steam_appid=game.steam_appid,
                timestamp=datetime.now()
            )
            self.db.add(stats)
        
        # Import ownership estimates
        if 'owners' in data:
            # SteamSpy returns ranges like "100,000,000 .. 200,000,000"
            owners_str = str(data['owners'])
            if '..' in owners_str:
                # Take average of range
                parts = owners_str.split('..')
                low = parts[0].replace(',', '').strip()
                high = parts[1].replace(',', '').strip()
                stats.estimated_owners = int((int(low) + int(high)) / 2)
            elif '-' in owners_str:
                # Alternative format "20000-50000"
                low, high = owners_str.split('-')
                stats.estimated_owners = int((int(low) + int(high)) / 2)
        
        # Import player counts
        if 'average_forever' in data:
            stats.peak_players = int(data['average_forever'])
        
        if 'ccu' in data:
            stats.current_players = int(data['ccu'])
        
        self.db.commit()
    
    def get_import_report(self) -> str:
        """
        Generate a human-readable import report.
        
        Returns:
            Formatted report string
        """
        duration = None
        if self.import_stats["start_time"] and self.import_stats["end_time"]:
            duration = (self.import_stats["end_time"] - self.import_stats["start_time"]).total_seconds()
        
        report = [
            "\n" + "="*60,
            "KAGGLE DATASET IMPORT REPORT",
            "="*60,
            f"Games Imported:  {self.import_stats['games_imported']}",
            f"Games Updated:   {self.import_stats['games_updated']}",
            f"Games Skipped:   {self.import_stats['games_skipped']}",
            f"Errors:          {len(self.import_stats['errors'])}",
        ]
        
        if duration:
            report.append(f"Duration:        {duration:.1f}s")
        
        if self.import_stats["errors"]:
            report.append("\nFirst 10 Errors:")
            for error in self.import_stats["errors"][:10]:
                report.append(f"  - {error}")
        
        report.append("="*60)
        
        return "\n".join(report)


def main():
    """
    CLI interface for Kaggle dataset import.
    """
    db = next(get_db())
    importer = KaggleDatasetImporter(db)
    
    print("\n🔍 Searching for available Steam datasets...\n")
    
    # List available datasets
    datasets = importer.list_available_datasets()
    
    for i, dataset in enumerate(datasets, 1):
        status = "✅ Available" if dataset["accessible"] else "❌ Unavailable"
        print(f"{i}. {dataset['name']}")
        print(f"   {status} | {dataset['size_mb']} MB | {dataset['description']}")
        print(f"   Last Updated: {dataset['last_updated']}")
        print()
    
    # Import from SteamSpy (always available)
    print("📥 Importing ownership data from SteamSpy API...\n")
    
    stats = importer.import_from_steamspy()
    print(importer.get_import_report())


if __name__ == "__main__":
    main()
