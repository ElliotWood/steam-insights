# Steam Insights - Project Documentation

This comprehensive guide covers setup, features, architecture, and usage patterns.

## Table of Contents

1. [Quick Start Guide](#quick-start-guide)
2. [Dashboard Features](#dashboard-features)
3. [Data Sources](#data-sources)
4. [API Reference](#api-reference)
5. [Architecture](#architecture)
6. [Common Use Cases](#common-use-cases)
7. [Testing](#testing)
8. [Configuration](#configuration)
9. [Troubleshooting](#troubleshooting)

---

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

---

## Dashboard Features

### Overview Page (📊 Dashboard Overview)
- **KPI Cards**: Total games, genres, recent updates, average players
- **Genre Distribution**: Bar chart and pie chart visualizations
- **Recent Activity**: Table of recently imported games
- **Top Performing**: Ranked list of games by player metrics

### Game Search (🔍 Find Games)
- Search functionality with live results
- Expandable game detail cards
- Platform badges (Windows/Mac/Linux)
- Header images and descriptions
- Player count history charts (30 days)

### Analytics (📈 Advanced Analytics)
Three analysis tabs:

1. **Player Analytics**: Top 15 games by player count with peak vs average comparison
2. **Market Insights**: Ownership distribution, developer treemap visualizations
3. **Trend Analysis**: Multi-game comparison with time series charts

### Market Analysis (🎯 Game Ownership Overlap)
- Two-game comparison for audience overlap
- Estimated overlap calculations based on genre similarity
- Addressable market sizing
- Interactive visualizations

### Advanced Analytics
Four specialized tabs:

1. **Correlations**: Find games with similar player patterns using heatmap
2. **Forecasting**: Predict future player counts (3 methods: moving average, linear regression, exponential)
3. **Growth Trends**: Track growth rates with volatility metrics
4. **Genre Performance**: Aggregate statistics and market share by genre

### Data Management (📥 Import Data)
Four management tabs:

1. **Import Single**: Import individual games by Steam App ID
2. **Bulk Import**: Import top 50 popular games or custom lists
3. **Export**: Download data as CSV/JSON with filters
4. **Stats**: Database health metrics and coverage monitoring

---

## Data Sources

### Steam Web API (Primary Source)
- **Current Players**: Real-time player counts via `ISteamUserStats/GetNumberOfCurrentPlayers`
- **Achievements**: Global achievement percentages and game schemas
- **Authentication**: Optional Steam Web API key (free from steamcommunity.com/dev)
- **Rate Limits**: ~200 requests per 5 minutes per IP

### Steam Store API
- **Game Metadata**: Name, developer, publisher, genres, platforms
- **Pricing**: Current prices, discounts, currency information
- **Categories**: Feature categories and tags
- **Reviews**: User review counts and recommendations
- **Metacritic**: Scores and URLs when available

### Web Scraper
- **User Tags**: Community-generated tags (not available via API)
- **Detailed Descriptions**: Full marketing and "about" sections
- **System Requirements**: Platform-specific hardware requirements
- **Rate Limiting**: Configurable delay (default 1s between requests)

### Data Quality
- **Reliability**: Steam API/Store API at 99.9% uptime
- **Freshness**: Real-time data on import
- **Coverage**: 239,000+ games available through Steam
- **Test Coverage**: 100% on data collection components

---

## API Reference

### API Endpoints Overview

The FastAPI backend provides RESTful endpoints for accessing game data. Access the interactive documentation at `http://localhost:8000/docs` when running the API server.

### Games Endpoints

- **`GET /games`** - List games with pagination and filtering
  - Query params: `skip`, `limit`, `search`, `genre`
  - Example: `curl "http://localhost:8000/games?search=counter&limit=10"`

- **`GET /games/{app_id}`** - Get detailed game information
  - Example: `curl http://localhost:8000/games/730`

- **`GET /games/{app_id}/player-stats`** - Get player statistics history
  - Query param: `days` (1-365)
  - Example: `curl "http://localhost:8000/games/730/player-stats?days=30"`

### Statistics Endpoints

- **`GET /genres`** - List all genres with game counts
  - Example: `curl http://localhost:8000/genres`

- **`GET /stats/trending`** - Get trending games by player count
  - Query param: `limit` (1-50)
  - Example: `curl "http://localhost:8000/stats/trending?limit=10"`

### System Endpoints

- **`GET /`** - API information and version
  - Example: `curl http://localhost:8000/`

---

## Architecture

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


# New Features Added - November 15, 2025

## 1. Play Time Statistics 📊

Added two new columns to the `PlayerStats` model to track player engagement:

- **average_playtime_minutes**: Average time players spend in the game
- **peak_playtime_minutes**: Maximum recorded playtime for any player

### Migration
Run the migration script to add these columns:
```bash
python src/database/migrations/add_playtime_columns.py
```

---

## 2. Top Charts 📈

New feature inspired by Video Game Insights showing trending games across multiple metrics:

### Location
`⚙️ Data Management` → `📊 Top Charts`

### Features
- **New Followers/Wishlists**: Games gaining the most followers in selected period
- **Player Growth**: Games with highest player activity growth
- **Revenue Leaders**: Top earning games

### Time Periods
- Last Week
- Last Month
- Last 3 Months
- Last Year

---

## 3. Market Analytics 🔍

Comprehensive Steam market analysis dashboard:

### Location
`⚙️ Data Management` → `🔍 Market Analytics`

### Tabs

#### Market Size
- Total games on Steam
- Games released per year (2010+)
- Growth trends visualization

#### User Engagement
- Peak concurrent players over time
- Daily player activity trends
- User engagement metrics

#### Genre Supply/Demand
- Supply: Number of games per genre
- Demand: Average owners per genre
- Scatter plot showing opportunities (low supply, high demand)

---

## 4. LLM Data Mining 🤖

AI-powered extraction of structured insights from game data:

### Location
`⚙️ Data Management` → `🤖 LLM Data Mining`

### Features

#### Individual Game Analysis
Search and analyze any game to extract:
- **Game Mechanics** (as bullet list):
  - Turn-based combat
  - Resource management
  - Base building
  - etc.

- **Themes** (as bullet list):
  - Post-apocalyptic
  - Survival
  - Exploration
  - etc.

- **Features/Functionality** (as bullet list):
  - Single-player campaign
  - Multiplayer co-op
  - Steam Workshop support
  - etc.

- **Player Feedback Sentiment**:
  - Sentiment score (% positive)
  - Common themes in reviews
  - Trend analysis

#### Batch Processing
- Process multiple games at once
- Build comprehensive database of structured insights
- Configurable batch size (10-1000 games)

### Implementation Notes
Currently shows placeholder data. To enable full functionality:

1. **Integrate with LLM API**:
   - OpenAI GPT-4
   - Anthropic Claude
   - Local LLM (e.g., Llama, Mistral)

2. **Add to requirements.txt**:
   ```
   openai>=1.0.0
   # or
   anthropic>=0.8.0
   ```

3. **Set API Key**:
   ```python
   # In config/settings.py
   OPENAI_API_KEY = "your-api-key"
   ```

4. **Implementation Example**:
   ```python
   import openai
   
   def analyze_game_with_llm(game_description):
       prompt = f"""
       Analyze this game description and extract:
       1. Game mechanics (as a list)
       2. Themes (as a list)
       3. Features/functionality (as a list)
       
       Game Description:
       {game_description}
       
       Format as JSON.
       """
       
       response = openai.ChatCompletion.create(
           model="gpt-4",
           messages=[{"role": "user", "content": prompt}]
       )
       
       return response.choices[0].message.content
   ```

---

## Navigation Structure Updated

### Data Management Section Now Includes:
1. ⚙️ System Settings (existing)
2. 📊 Top Charts (NEW)
3. 🔍 Market Analytics (NEW)
4. 🤖 LLM Data Mining (NEW)

---

## Future Enhancements

### Potential Additions:
- **Revenue Calculator**: Based on wishlists and conversion rates
- **Pricing Tool**: Optimal price point calculator
- **Unit Sales Estimation**: Estimate actual units sold
- **Developer Rankings**: Top publishers and studios
- **Release Calendar**: Upcoming game releases by genre
- **Tag Trend Analysis**: Emerging tag combinations

---

## Data Sources Inspiration

Based on features from [Video Game Insights](https://vginsights.com):
- Top Charts functionality
- Steam Market Data analytics
- Genre supply/demand analysis
- Developer tools section

## Technical Notes

### Database Schema Changes
New columns in `player_stats` table require migration.

### Performance Considerations
- Top Charts queries are indexed on `timestamp` and `estimated_owners`
- Market Analytics uses aggregations - may be slow on large datasets
- LLM Mining will require API rate limiting for batch processing

### Dependencies
No new dependencies required for Top Charts and Market Analytics.
LLM Mining requires OpenAI or Anthropic library when implemented.
