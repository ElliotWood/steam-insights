# Steam Insights - Project Documentation

## Quick Start Guide

### 1. Initial Setup

```bash
# Clone the repository
git clone https://github.com/ElliotWood/steam-insights.git
cd steam-insights

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your Steam API key

# Initialize database
python setup.py
```

### 2. Running the Application

#### Option A: Dashboard (Recommended for Quick Start)
```bash
streamlit run src/dashboard/app.py
```
Access at: http://localhost:8501

#### Option B: API Server
```bash
python -m uvicorn src.api.main:app --reload
```
Access at: http://localhost:8000
API Docs: http://localhost:8000/docs

#### Option C: Use the Run Script
```bash
./run_dashboard.sh
```

## Features

### 1. Dashboard Features

#### Overview Page
- Total games count
- Number of genres tracked
- Recent update statistics
- Average current players
- Top genres by game count (bar chart)
- Recently added games list

#### Game Search
- Search games by name
- View detailed game information
- Platform indicators (Windows, Mac, Linux)
- Game descriptions and metadata
- Player count history charts (last 30 days)
- Genre tags

#### Analytics
- Time range selector (24 hours to 90 days)
- Most active games ranking
- Peak and average player counts
- Interactive charts with Plotly

#### Data Management
- Import games by Steam App ID
- Quick import buttons for popular games
- Automatic player statistics collection
- Status feedback for imports

### 2. API Endpoints

#### Games
- `GET /games` - List games with pagination and filtering
  - Query params: skip, limit, search, genre
- `GET /games/{app_id}` - Get detailed game information
- `GET /games/{app_id}/player-stats` - Get player statistics history
  - Query param: days (1-365)

#### Statistics
- `GET /genres` - List all genres with game counts
- `GET /stats/trending` - Get trending games by player count
  - Query param: limit (1-50)

#### System
- `GET /` - API information and version

## Project Architecture

### Data Flow

```
Steam API → Steam Client → Game Importer → Database
    ↓                           ↓
Steam Store → Web Scraper → Game Importer → Database
                                                ↓
                                    ←→ API Server ←→
                                                ↓
                                          Dashboard
```

### Database Schema

**Core Tables:**
- `games` - Game information
- `genres` - Genre definitions
- `tags` - Tag/category definitions
- `player_stats` - Time-series player counts
- `pricing_history` - Price tracking
- `reviews` - User reviews
- `achievements` - Game achievements

**Relationships:**
- Games ←→ Genres (many-to-many)
- Games ←→ Tags (many-to-many)
- Games → Reviews (one-to-many)
- Games → PlayerStats (one-to-many)
- Games → PricingHistory (one-to-many)

### Module Responsibilities

#### `src/api/`
- **main.py**: FastAPI application with REST endpoints
- **steam_client.py**: Steam Web API integration

#### `src/database/`
- **connection.py**: Database connection management

#### `src/models/`
- **database.py**: SQLAlchemy ORM models

#### `src/etl/`
- **game_importer.py**: ETL pipeline for importing games

#### `src/scrapers/`
- **steam_scraper.py**: Web scraper for Steam store

#### `src/dashboard/`
- **app.py**: Streamlit dashboard application

#### `src/utils/`
- **logging_config.py**: Logging configuration

#### `config/`
- **settings.py**: Application configuration

## Common Use Cases

### Import a Single Game

```python
from src.database.connection import get_db
from src.etl.game_importer import GameDataImporter

db = next(get_db())
importer = GameDataImporter(db)

# Import Counter-Strike 2
game = importer.import_game(730)
print(f"Imported: {game.name}")

# Update player stats
stats = importer.update_player_stats(730)
print(f"Current players: {stats.current_players}")

db.close()
```

### Query Games Programmatically

```python
from src.database.connection import get_db
from src.models.database import Game, Genre

db = next(get_db())

# Find all action games
action_games = db.query(Game).join(Game.genres).filter(
    Genre.name == "Action"
).all()

for game in action_games:
    print(f"{game.name} by {game.developer}")

db.close()
```

### Use the API

```bash
# Search for games
curl "http://localhost:8000/games?search=counter"

# Get specific game
curl http://localhost:8000/games/730

# Get player stats
curl "http://localhost:8000/games/730/player-stats?days=7"

# Get all genres
curl http://localhost:8000/genres

# Get trending games
curl "http://localhost:8000/stats/trending?limit=10"
```

## Testing

### Run All Tests
```bash
pytest tests/ -v
```

### Run with Coverage
```bash
pytest --cov=src tests/
```

### Run Specific Test File
```bash
pytest tests/test_models.py -v
```

## Troubleshooting

### Database Issues

If you encounter database errors, try reinitializing:
```bash
rm steam_insights.db
python setup.py
```

### Import Failures

**Issue**: Games fail to import
**Solutions**:
- Check your Steam API key is configured in .env
- Verify the App ID is correct
- Check your internet connection
- Some games may not be available via API

### Rate Limiting

Steam may rate limit requests. The scraper includes a default 1-second delay between requests. Increase if needed:

```python
from src.scrapers.steam_scraper import SteamStoreScraper
scraper = SteamStoreScraper(rate_limit_delay=2.0)
```

## Configuration Options

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| STEAM_API_KEY | - | Your Steam Web API key |
| DATABASE_URL | sqlite:///steam_insights.db | Database connection string |
| DEBUG | False | Enable debug mode |
| LOG_LEVEL | INFO | Logging level |
| API_HOST | 0.0.0.0 | API server host |
| API_PORT | 8000 | API server port |
| DASHBOARD_PORT | 8501 | Dashboard port |

### Database Configuration

**SQLite (Default)**:
```
DATABASE_URL=sqlite:///steam_insights.db
```

**PostgreSQL**:
```
DATABASE_URL=postgresql://user:password@localhost:5432/steam_insights
```

**MySQL**:
```
DATABASE_URL=mysql+pymysql://user:password@localhost:3306/steam_insights
```

## Future Enhancements

Potential features to add:

1. **Scheduled Data Updates**
   - Automated daily imports using APScheduler
   - Background worker for continuous monitoring

2. **Advanced Analytics**
   - Predictive models for game success
   - Sentiment analysis of reviews
   - Regional pricing comparisons

3. **Enhanced Visualizations**
   - Genre market share over time
   - Developer performance tracking
   - Comparative game analysis

4. **Data Export**
   - CSV/JSON export functionality
   - Report generation

5. **User Features**
   - Watchlists for specific games
   - Alerts for price changes
   - Custom dashboards

## Contributing

Contributions are welcome! Areas that could use improvement:

- Additional data sources integration
- More visualization options
- Performance optimizations
- Additional API endpoints
- Enhanced error handling
- More comprehensive tests

## Resources

- [Steam Web API Documentation](https://steamcommunity.com/dev)
- [Kaggle Steam Datasets](https://www.kaggle.com/search?q=steam+games)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
