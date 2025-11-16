# Steam Insights - Project Documentation

**Last Updated**: November 16, 2025  
**Status**: Phase 3 Sprint 1 Complete ✅  
**Test Coverage**: 159 tests, 77% pass rate  
**Database**: 213,386 games, 39 English genres, 6,400+ player stats

This comprehensive guide covers setup, features, architecture, and usage patterns.

## Table of Contents

1. [Quick Start Guide](#quick-start-guide)
2. [Dashboard Features](#dashboard-features)
3. [Phase 3 Features (November 2025)](#phase-3-features-november-2025)
4. [Data Sources](#data-sources)
5. [ETL Pipeline](#etl-pipeline)
6. [API Reference](#api-reference)
7. [Architecture](#architecture)
8. [Common Use Cases](#common-use-cases)
9. [Testing](#testing)
10. [Configuration](#configuration)
11. [Recent Fixes](#recent-fixes)
12. [Troubleshooting](#troubleshooting)

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
- **Genre Distribution**: Interactive bar chart and pie chart visualizations
- **Recent Activity**: Table of recently imported games with metadata
- **Top Performing**: Top 15 games by peak players (24h) with real-time data
- **Database Stats**: Connection status, table counts, data quality metrics

### Game Explorer (🎮 Game Explorer)
- **Pagination**: Navigate through all 213K+ games with page controls
- **Search & Filters**: Real-time search with genre, platform, and owner filters
- **Game Cards**: Expandable cards with header images and full details
- **Platform Badges**: Windows/Mac/Linux support indicators
- **Player Stats**: Peak players (24h), current players, estimated owners
- **Price Info**: Current pricing with discount detection
- **No Artificial Limits**: View all games without 50K owner caps

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

### Data Management (⚙️ Data Management)
Comprehensive data operations:

1. **Import Single**: Import individual games by Steam App ID with validation
2. **Bulk Import**: Import top popular games, custom lists, or batch operations
3. **Export Options**: CSV, JSON, Excel formats with advanced filters
4. **Database Stats**: Health metrics, table sizes, index performance
5. **Top Charts** 📊: Trending games by followers, player growth, revenue
6. **Market Analytics** 🔍: Market size, user engagement, genre supply/demand
7. **LLM Data Mining** 🤖: AI-powered game analysis (placeholder for future)
8. **Feedback System**: User feedback collection and analytics

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

### SteamSpy API (Player Statistics)
- **Player Counts**: Peak 24h players, current players, historical trends
- **Ownership Data**: Estimated owners (ranges provided by SteamSpy)
- **Playtime Stats**: Average and peak playtime minutes
- **Review Data**: Positive/negative review counts
- **Rate Limits**: 4 requests per second
- **Coverage**: 200K+ games with player data

### Zenodo Academic Dataset
- **Source**: Steam dataset from academic research
- **Release Dates**: Historical release dates for 213K+ games
- **Genre Mappings**: Pre-classified genre associations
- **Tag Data**: Community tag relationships
- **Format**: CSV files with structured data

### Data Quality
- **Reliability**: Steam API/Store API at 99.9% uptime
- **Freshness**: Real-time data on import, SteamSpy updated hourly
- **Coverage**: 213,386 games in database, 6,400+ with player stats
- **Accuracy**: 99.7% success rate on SteamSpy imports
- **Cleanliness**: 39 English-only genres after multi-language cleanup
- **Test Coverage**: 77% pass rate across 159 tests

---

## ETL Pipeline

### Overview
The ETL (Extract, Transform, Load) pipeline coordinates data import from multiple sources:

```
Steam API → Game Importer → PostgreSQL
SteamSpy API → Player Stats Importer → PostgreSQL
Zenodo Dataset → Release Date Importer → PostgreSQL
```

### Available ETL Scripts

#### 1. SteamSpy Player Stats Import
**Location**: `src/etl/steamspy/import_player_stats.py`

**Features**:
- Imports player statistics for all games in database
- Fault-tolerant individual record commits
- Resume capability from last AppID
- Rate limiting (4 req/sec)
- Batch progress tracking (50 games per batch)

**Usage**:
```bash
python src/etl/steamspy/import_player_stats.py
```

**Data Imported**:
- peak_players_24h: Peak concurrent players in last 24 hours
- current_players: Current active players
- estimated_owners: Ownership range estimate
- average_playtime_minutes: Average time played
- median_playtime_minutes: Median playtime
- positive_reviews: Positive review count
- negative_reviews: Negative review count

#### 2. Zenodo Release Dates Import
**Location**: `src/etl/zenodo/import_release_dates.py`

**Features**:
- Imports release dates from academic dataset
- Updates existing game records
- Handles date format variations

**Usage**:
```bash
python src/etl/zenodo/import_release_dates.py
```

#### 3. Zenodo Genre Associations
**Location**: `src/etl/zenodo/import_genre_associations.py`

**Status**: ✅ Already executed
- 391,000+ genre associations imported
- Multi-language genres cleaned to 39 English genres

#### 4. Zenodo Tag Associations
**Location**: `src/etl/zenodo/import_tag_associations.py`

**Status**: ✅ Already executed
- Community tag mappings imported
- German tags removed during cleanup

#### 5. ETL Orchestration Pipeline
**Location**: `src/etl/orchestration/pipeline.py`

**Features**:
- Coordinates multiple ETL jobs
- Sequential or parallel execution
- Error handling and retry logic
- Job logging and metrics

**Usage**:
```bash
python src/etl/orchestration/pipeline.py
```

### Running Full ETL

To populate the database completely:

```bash
# 1. Import base game data (if needed)
python scripts/import_all_games.py

# 2. Import SteamSpy player stats (14-15 hours for 212K games)
python src/etl/steamspy/import_player_stats.py

# 3. Import Zenodo release dates (optional)
python src/etl/zenodo/import_release_dates.py

# Or use orchestration to run all
python src/etl/orchestration/pipeline.py
```

### Performance Indexes

Add performance indexes for faster queries:

```bash
python scripts/add_performance_indexes.py
```

**Indexes Added**:
- games.steam_appid (unique)
- games.name (text search)
- genres.name (lookups)
- player_stats.steam_appid (joins)
- player_stats.timestamp (time series)
- player_stats.peak_players_24h (rankings)
- player_stats.estimated_owners (filters)
- game_genres.game_id + genre_id (associations)

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

## Recent Fixes

### November 16, 2025 - Dashboard & Data Quality

#### Issues Fixed:
1. **Top Performing Games Showing Zeros**
   - Problem: All games showed "0" peak players
   - Cause: Only 3 games had player_stats data
   - Fix: Implemented SteamSpy ETL import (6,400+ games imported)
   - Query: Now uses `peak_players_24h` correctly

2. **Game Explorer Missing Pagination**
   - Problem: Stuck on first page, couldn't browse 213K games
   - Fix: Added page number selector with offset/limit logic
   - Features: Page controls, total page count, items per page setting

3. **Owner Values Capped at 50,000**
   - Problem: Hardcoded 50K limits throughout dashboard
   - Fix: Removed caps from 9 locations across 5 files
   - Files: analysis_pages.py, concept_research.py, preproduction.py, marketing_pages.py, app.py
   - Result: Now displays actual estimated_owners values

4. **Non-English Data Contamination**
   - Problem: 154 genres included French, German, Russian, Japanese, Korean, Chinese entries
   - Fix: Two-stage cleanup removed 115 foreign entries
   - Result: Clean 39 English-only genres
   - Script: `comprehensive_genre_cleanup.py` (one-time execution)

#### Data Quality Improvements:
- Genres reduced: 154 → 39 (English only)
- Player stats coverage: 3 → 6,400+ games (ongoing import)
- Database integrity: 213,386 games maintained
- Genre associations: 391K relationships preserved

### November 15, 2025 - Phase 3 Sprint 1

#### Completed:
- ✅ Database performance indexes (8 indexes)
- ✅ SteamSpy ETL integration with fault tolerance
- ✅ Zenodo dataset integration (genres, tags, release dates)
- ✅ Dashboard caching with Redis
- ✅ Enhanced export formats (CSV, JSON, Excel, Parquet)
- ✅ ETL orchestration pipeline
- ✅ Steam page builder tool
- ✅ User feedback system
- ✅ 159 tests written (77% pass rate)

---

## Troubleshooting

### Database Issues

**PostgreSQL Connection Errors**:
```bash
# Check PostgreSQL is running
sudo systemctl status postgresql

# Restart if needed
sudo systemctl restart postgresql

# Check connection in config/settings.py
DATABASE_URL=postgresql://user:pass@localhost:5432/steam_insights
```

**Migration Issues**:
```bash
# Run pending migrations
python scripts/update_schema.py

# Add performance indexes
python scripts/add_performance_indexes.py
```

### Import Failures

**Issue**: Games fail to import
**Solutions**:
- Check your Steam API key is configured in .env
- Verify the App ID is correct
- Check your internet connection
- Some games may not be available via API

**SteamSpy Import Failures**:
- If ON CONFLICT errors occur, ensure table has no unique constraint on (steam_appid, timestamp)
- Use fault-tolerant mode (individual commits)
- Check rate limiting (4 req/sec max)
- Resume from last AppID if interrupted

**Data Quality Issues**:
- Run `scripts/list_all_genres_tags.py` to check for non-English entries
- Non-English data already cleaned (November 16, 2025)
- If new foreign entries appear, modify genre/tag names directly in database

### Rate Limiting

**Steam API Rate Limits**:
Steam may rate limit requests. The scraper includes a default 1-second delay between requests. Increase if needed:

```python
from src.scrapers.steam_scraper import SteamStoreScraper
scraper = SteamStoreScraper(rate_limit_delay=2.0)
```

**SteamSpy Rate Limits**:
- Maximum: 4 requests per second
- Default delay: 0.25 seconds between requests
- Batch size: 50 games per progress update
- Total time: ~14-15 hours for 212,383 games

**Best Practices**:
- Run SteamSpy import during off-hours
- Use fault-tolerant mode for long-running imports
- Monitor terminal output for progress
- Note last AppID if interrupted for resume

## Configuration Options

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| STEAM_API_KEY | - | Your Steam Web API key |
| DATABASE_URL | postgresql://user:pass@localhost:5432/steam_insights | Database connection string |
| REDIS_HOST | localhost | Redis cache host (optional) |
| REDIS_PORT | 6379 | Redis cache port |
| REDIS_DB | 0 | Redis database number |
| CACHE_TTL | 3600 | Cache time-to-live in seconds |
| DEBUG | False | Enable debug mode |
| LOG_LEVEL | INFO | Logging level |
| API_HOST | 0.0.0.0 | API server host |
| API_PORT | 8000 | API server port |
| DASHBOARD_PORT | 8501 | Dashboard port |
| STEAMSPY_RATE_LIMIT | 0.25 | Delay between SteamSpy requests (seconds) |

### Database Configuration

**PostgreSQL (Current)**:
```
DATABASE_URL=postgresql://user:password@localhost:5432/steam_insights
```

**Current Stats**:
- Games: 213,386
- Genres: 39 (English only)
- Genre Associations: 391,000+
- Player Stats: 6,400+ (ongoing SteamSpy import)

**PostgreSQL Setup**:
See `docs/POSTGRESQL_SETUP.md` for detailed setup instructions.

**Alternative Databases**:

**SQLite** (Not recommended for production):
```
DATABASE_URL=sqlite:///steam_insights.db
```

**MySQL**:
```
DATABASE_URL=mysql+pymysql://user:password@localhost:3306/steam_insights
```

## Future Enhancements

Potential features to add:

1. **Scheduled Data Updates**
   - Automated daily SteamSpy imports using cron/scheduler
   - Background worker for continuous monitoring
   - Incremental updates for changed games only

2. **Advanced Analytics** (LLM Mining Placeholder Ready)
   - Predictive models for game success
   - AI-powered sentiment analysis of reviews
   - Regional pricing comparisons
   - Game mechanics extraction using LLMs

3. **Enhanced Visualizations**
   - Genre market share over time (partially implemented)
   - Developer performance tracking
   - Comparative game analysis across multiple titles
   - Heat maps for release timing

4. **User Features**
   - Watchlists for specific games
   - Alerts for price changes
   - Custom dashboards with saved filters
   - Personalized recommendations

5. **API Enhancements**
   - GraphQL endpoint for flexible queries
   - Webhooks for data updates
   - Rate limiting per API key
   - Public API with documentation

### Completed Features (Phase 3)
- ✅ Data Export (CSV, JSON, Excel, Parquet)
- ✅ Enhanced Visualizations (Top Charts, Market Analytics)
- ✅ Performance Optimization (Indexes, Caching)
- ✅ ETL Automation (SteamSpy, Zenodo integration)

## Contributing

Contributions are welcome! Areas that could use improvement:

- Additional data sources integration (more APIs, datasets)
- More visualization options (charts, graphs, dashboards)
- Performance optimizations (query tuning, caching strategies)
- Additional API endpoints (GraphQL, webhooks)
- Enhanced error handling (retry logic, better messages)
- More comprehensive tests (increase from 77% pass rate)
- LLM integration for game analysis (placeholder ready)
- Automated ETL scheduling (cron jobs, airflow)

### Development Guidelines
- Follow PEP 8 style guide
- Add tests for new features
- Update documentation
- Run `pytest` before committing
- Check for rate limiting impacts

## Resources

- [Steam Web API Documentation](https://steamcommunity.com/dev)
- [SteamSpy API](https://steamspy.com/api.php)
- [Zenodo Steam Dataset](https://zenodo.org/records/10447144)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)

---

## Version History

### Phase 3 Sprint 1 (November 15-16, 2025)
- Database performance indexes (8 indexes added)
- SteamSpy ETL integration with fault tolerance
- Zenodo dataset integration (genres, tags, release dates)
- Dashboard caching system with Redis
- Enhanced export formats (4 formats)
- ETL orchestration pipeline
- Steam page builder tool
- User feedback system
- 159 tests written (77% pass rate)
- **Critical fixes**: Pagination, 50K caps removed, data quality cleanup

### Phase 2 (Completed)
- Game database expanded to 213K+ games
- Genre and tag associations imported
- Export functionality across all tables
- Advanced analytics features

### Phase 1 (Completed)
- Core dashboard and API
- Steam API integration
- Basic database schema
- Data import scripts


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
