# Frequently Asked Questions (FAQ)

## Platform Capabilities & Feature Reference

This document answers common questions about what the Steam Insights platform can do and where to find specific features in the dashboard.

---

## 1. Can your platform show overlap between players of two specific games?

**Answer: Yes ✅** 

The platform provides game ownership overlap analysis in the **Market Analysis** page.

**Where to find it:**
- Navigate to: **Development Stage** → "🚀 Launch & Analytics" → "📈 Market Position" (or through legacy navigation)
- The Market Analysis feature is also accessible through the Post-Launch Analytics section

**What it shows:**
- **Two-game comparison:** Select any two games from the database to analyze audience overlap
- **Overlap estimation:** Calculates estimated overlap based on genre similarity using Jaccard similarity coefficient
- **Addressable market:** Shows the addressable market size for each game (audience that doesn't overlap)
- **Visual representation:** Provides metrics and visualizations of the overlap percentage
- **Multi-game support:** Can add additional games for extended market analysis

**Technical details:**
- Overlap calculation ranges from 10-40% based on genre similarity
- Higher genre similarity = higher estimated overlap
- Uses estimated owners data from SteamSpy API
- Located in: `src/dashboard/modules/postlaunch_pages.py` (function: `show_market_analysis()`)

**Limitations:**
- Overlap is *estimated* based on genre similarity, not actual player data (Steam doesn't provide cross-game player data publicly)
- Requires games to have ownership data imported from SteamSpy
- Does not show actual individual players who own both games (privacy restrictions)

---

## 2. Do you track playtime, retention, or engagement across those audiences?

**Answer: Partial ✅ (Playtime Yes, Retention/Engagement Limited)**

### What IS tracked:

**Playtime Metrics:**
- **Average playtime** (in minutes) - Available through SteamSpy integration
- **Peak playtime** (in minutes) - Historical peak playtime data
- **Median playtime** - Median time players spend in the game
- Located in: `player_stats` table, columns: `average_playtime_minutes`, `peak_playtime_minutes`

**Player Count Tracking:**
- **Current players** - Real-time concurrent players
- **Peak players (24h)** - Peak concurrent players in last 24 hours
- **Estimated owners** - Total estimated ownership
- Time-series tracking allows viewing trends over time

**Where to find it:**
- **Game Explorer** (`🎮 Game Explorer`) - Shows playtime in individual game details
- **Analytics** (`📈 Advanced Analytics`) - Time series charts of player counts
- **Player Analytics** tab - Shows trends and comparisons
- Located in: Database model `PlayerStats` in `src/models/database.py`

### What is NOT tracked:

**Retention Metrics (Not Currently Available):**
- Day 1, Day 7, Day 30 retention rates
- Player return rates
- Churn analysis
- Session frequency

**Engagement Metrics (Not Currently Available):**
- Achievement completion rates (data model exists but not populated)
- Daily Active Users (DAU) / Monthly Active Users (MAU)
- Session length distribution
- Feature usage patterns

**Why these limitations exist:**
- Steam's public APIs don't provide individual player-level retention data
- Aggregate playtime is available, but not retention curves
- Privacy restrictions prevent cross-game individual player tracking

**Data source:** SteamSpy API (`src/etl/steamspy/import_player_stats.py`)

---

## 3. Can we filter or compare by game features or tags (e.g., genres, mechanics)?

**Answer: Yes ✅**

The platform provides extensive filtering and comparison by genres and tags.

### Genre Filtering & Analysis:

**Where to find it:**
1. **Game Explorer** (`🎮 Game Explorer`)
   - Multi-select genre filter
   - Real-time filtering of 213K+ games
   - Combine with search and platform filters
   
2. **Genre Analysis** (`📊 Genre Analysis`)
   - Full genre performance metrics
   - Market share by genre
   - Genre saturation analysis
   - Located in: Concept & Research stage

3. **Competition Analysis** (`🎯 Competition Analysis`)
   - Filter by genre/tag combinations
   - Analyze competition level by tags
   - Find successful games with specific tag combinations
   - Located in: Pre-Production & Validation stage

4. **Genre Saturation** (`📊 Genre Saturation`)
   - Opportunity scoring by genre
   - Competition level indicators
   - Located in: Concept & Research stage

### Tag Filtering & Strategy:

**Where to find it:**
1. **Tag Strategy** (`🏷️ Tag Strategy`)
   - Analyze winning tag combinations
   - Find successful tag patterns
   - See which combinations lead to high ownership
   - Located in: Pre-Production & Validation stage

2. **Competition Calculator** (`⚔️ Competition Calculator`)
   - Calculate competition index by tags
   - Evaluate difficulty by tag combination
   - Located in: Production & Tracking stage

**Data coverage:**
- **213,386 games** in database
- **91.6% tag coverage** (195,380 games with tags)
- **86.0% genre coverage** (183,516 games with genres)
- **944K tag associations**
- **730K genre associations**

**Technical implementation:**
- Many-to-many relationships between games and genres/tags
- Database models: `game_genres` and `game_tags` association tables
- Efficient indexed queries for fast filtering
- Located in: `src/models/database.py`

---

## 4. Do you include review sentiment or player feedback data from Steam?

**Answer: Partial ✅ (Infrastructure Ready, Limited Data)**

### Review Data Model (Available):

The platform has a complete **Review model** in the database:
- Review text storage
- Positive/negative classification (`is_positive` boolean)
- Vote counts (helpful, funny)
- Playtime at review time
- Author information
- Located in: `src/models/database.py` - `Review` class

### LLM-Enhanced Sentiment Analysis (Available):

The platform includes **GameEnrichment** model with:
- **Sentiment score** (-1.0 to 1.0 scale)
- **Sentiment summary** (text summary of player feedback)
- LLM-powered extraction from descriptions and reviews
- Located in: `src/models/database.py` - `GameEnrichment` class

**Where to find it:**
- **LLM Data Mining** (`🤖 LLM Data Mining`)
  - AI-powered game analysis
  - Sentiment analysis display
  - Located in: Data Management section
  - Implementation: `src/dashboard/modules/data_management.py`

### Current Status & Limitations:

**What's ready:**
- ✅ Database models for reviews and sentiment
- ✅ LLM enrichment infrastructure (`src/utils/llm_enrichment.py`)
- ✅ Batch processing system for large-scale analysis
- ✅ Dashboard pages to display sentiment data

**What's limited:**
- ⚠️ Review data must be imported (not automatically collected)
- ⚠️ Steam's review API requires authenticated requests for bulk access
- ⚠️ LLM enrichment is opt-in and requires processing time
- ⚠️ Focus is primarily on aggregate metrics, not individual review analysis

**Data Sources:**
- Steam Store API (review counts)
- SteamSpy (positive/negative review counts - documented in DOCUMENTATION.md)
- Steam Review API (individual reviews - requires implementation)
- LLM processing for sentiment extraction

**Future Enhancement Opportunity:**
The infrastructure is in place to add comprehensive review sentiment analysis. The main work needed is:
1. Implementing Steam Review API scraper
2. Running LLM enrichment batch jobs
3. Populating the review sentiment data

---

## 5. How granular is the data — game-level, audience segment, or user-level?

**Answer: Primarily Game-Level with Some Aggregate Audience Data**

### Data Granularity Breakdown:

#### Game-Level Data (Primary Focus) ✅
**Full coverage with detailed metrics:**
- Game metadata (name, developer, publisher, release date)
- Platform support (Windows, Mac, Linux)
- Genres and tags (many-to-many relationships)
- Pricing history over time
- Player statistics (current players, peak players, estimated owners)
- Playtime metrics (average, peak, median)
- Review counts
- All 213K+ games in database

**Where to find it:**
- Every dashboard page provides game-level analysis
- **Game Explorer** - Browse individual games
- **Analytics** - Game-specific time series
- **Market Analysis** - Game-to-game comparisons

#### Aggregate Audience Segments ✅
**Available through various analytics:**
- **Genre-level aggregates:**
  - Total games per genre
  - Average ownership per genre
  - Success rates by genre
  - Competition levels
  
- **Tag-based segments:**
  - Games grouped by tag combinations
  - Performance by tag clusters
  - Market opportunities by tags

- **Price-tier segments:**
  - Analysis by price ranges ($0-5, $5-10, etc.)
  - Success rates by pricing tier
  - Revenue estimates by tier

- **Platform segments:**
  - Windows vs Mac vs Linux comparisons
  - Multi-platform vs exclusive analysis

**Where to find it:**
- **Genre Analysis** - Genre-level aggregates
- **Market Opportunities** - Segment identification
- **Pricing Strategy** - Price-tier analysis
- **Competition Analysis** - Tag-based segmentation

#### User-Level Data ❌
**NOT available due to privacy restrictions:**
- Individual player identities
- Personal gaming libraries
- Cross-game player behavior
- Individual player progression
- User demographics

**Why no user-level data:**
- Steam privacy policies restrict access to individual player data
- Public APIs only provide aggregate statistics
- SteamSpy provides estimates, not individual records
- Our platform respects player privacy

### Data Granularity by Feature:

| Feature | Granularity Level | Details |
|---------|------------------|---------|
| Ownership overlap | Game-pair estimates | Based on genre similarity, not individual players |
| Playtime | Game-level aggregates | Average/median across all players of a game |
| Player counts | Game-level time-series | Concurrent players tracked over time |
| Genres/Tags | Game-to-category associations | Many-to-many relationships |
| Pricing | Game-level historical | Price changes tracked per game over time |
| Reviews | Game-level counts | Aggregate positive/negative, not individual analysis |
| Market size | Genre/tag segments | Aggregate market opportunities |

**Technical Implementation:**
- Database schema: `src/models/database.py`
- All models are game-centric (Game as primary entity)
- Relationships connect games to genres, tags, stats, reviews
- No user/player entity in the data model

---

## 6. Can we export or visualize that overlap and engagement data ourselves?

**Answer: Yes ✅ (Strong Export Capabilities)**

### Export Functionality:

The platform provides comprehensive data export options in multiple formats.

**Where to find it:**
- Navigate to: **Data Management** → "⚙️ System Settings" → "📤 Export Data" tab
- Located in: `src/dashboard/modules/postlaunch_pages.py` (function: `show_data_management()`)
- Implementation: `src/utils/data_export.py` - `DataExporter` class

### Export Options:

#### 1. Games Catalog Export
**What you can export:**
- Game metadata (name, developer, publisher)
- Platform support
- Release dates
- Ownership estimates
- All 213K+ games available

**Formats:**
- CSV (comma-separated values)
- JSON (structured data)

**Filters available:**
- Genre filtering
- Platform filtering
- Date range filtering
- Ownership threshold filtering

#### 2. Player Statistics Export
**What you can export:**
- Current players
- Peak players (24h)
- Estimated owners
- Average playtime
- Historical time-series data

**Formats:**
- CSV with timestamps
- Filterable by date range

#### 3. Genre Analysis Export
**What you can export:**
- Genre performance metrics
- Game counts per genre
- Success rates
- Market saturation data

**Format:**
- CSV/JSON structured exports

#### 4. Additional Export Formats (Mentioned in docs)
According to `README.md` and `DOCUMENTATION.md`:
- **Excel** format (.xlsx)
- **Parquet** format (for big data analysis)
- Available for all major tables

### Visualization Capabilities:

#### Built-in Visualizations ✅
**Interactive charts using Plotly:**
- Bar charts (genre distribution, competition levels)
- Line charts (time-series player counts)
- Scatter plots (market opportunities, price vs success)
- Pie charts (market share)
- Heatmaps (correlation analysis)
- Treemaps (developer market share)

**Where to find them:**
- Every analytics page includes interactive visualizations
- **Analytics** page has 4+ visualization tabs
- **Market Analysis** shows overlap visualizations
- **Advanced Analytics** includes forecasting charts

#### External Analysis ✅
**Export for your own tools:**
1. Export data in CSV/JSON/Excel/Parquet
2. Use in your preferred tools:
   - Excel/Google Sheets
   - Tableau/Power BI
   - Python (pandas, matplotlib)
   - R (ggplot2)
   - Custom applications

#### API Access ✅
**RESTful API available:**
- FastAPI backend at `http://localhost:8000`
- OpenAPI documentation at `/docs`
- Programmatic access to all data
- Query parameters for filtering
- Located in: `src/api/`

**Example endpoints:**
```
GET /games - List games with pagination
GET /games/{app_id} - Get specific game
GET /games/{app_id}/stats - Get player statistics
GET /genres - List all genres
GET /analytics/overlap - Game overlap analysis
```

### What CAN be exported:
✅ All game metadata
✅ Player statistics (time-series)
✅ Ownership data
✅ Genre and tag associations
✅ Pricing history
✅ Market analysis results
✅ Analytics calculations

### What CANNOT be exported:
❌ Individual player identities (privacy)
❌ Cross-game individual player behavior
❌ Raw Steam API responses (terms of service)
❌ Proprietary Steam data beyond public APIs

**Technical Details:**
- Export implementation: `src/utils/data_export.py`
- Uses pandas DataFrames for data manipulation
- Streaming exports for large datasets
- Progress indicators for long exports
- Download buttons integrated in Streamlit UI

---

## 7. What platforms does this work for — just Steam, or cross-platform too?

**Answer: Steam Only 🎮**

### Current Platform Support:

**Steam (PC) - Fully Supported ✅**
- Windows games
- Mac games  
- Linux games
- All 213K+ Steam games
- Complete Steam ecosystem integration

**Platform Coverage within Steam:**
The dashboard tracks which platforms *within Steam* each game supports:
- Windows support flag
- Mac support flag
- Linux support flag
- Filterable in Game Explorer

### Data Sources (All Steam-focused):

1. **Steam Web API**
   - Real-time player counts
   - Achievement data
   - Game metadata
   - Official Valve API

2. **Steam Store API**
   - Game details
   - Pricing information
   - Categories and tags
   - Review counts

3. **SteamSpy API**
   - Ownership estimates
   - Playtime statistics
   - Player demographics
   - Third-party but Steam-focused

4. **Zenodo Academic Dataset**
   - Historical Steam data
   - Genre classifications
   - Release dates
   - Research-grade Steam data

**All data sources are Steam-exclusive.**

### Cross-Platform Support: ❌ Not Currently Available

**Platforms NOT included:**
- ❌ Epic Games Store
- ❌ PlayStation (PS4, PS5)
- ❌ Xbox (One, Series X/S)
- ❌ Nintendo Switch
- ❌ Mobile (iOS, Android)
- ❌ GOG
- ❌ Itch.io
- ❌ Other PC storefronts

**Why Steam-only:**
- Steam has the most comprehensive public APIs
- SteamSpy provides unique ownership estimates
- Other platforms have more restricted data access
- Platform specialization allows deeper insights
- Steam is the largest PC gaming platform (>90% market share)

### Cross-Platform Game Tracking (Partial Information):

**What IS tracked:**
- If a Steam game is "also available on" other platforms (when mentioned in Steam store data)
- But no actual data *from* those other platforms

**What is NOT tracked:**
- Sales on other platforms
- Player counts on console
- Cross-platform ownership overlap
- Mobile game performance
- Epic Games exclusivity impact

### Technical Architecture (Steam-focused):

**API Clients:**
- `SteamAPIClient` - Official Steam API
- `SteamStoreClient` - Steam Store scraping
- `SteamSpyClient` - SteamSpy integration
- Located in: `src/api/steam_client.py`

**Database Schema:**
- All models reference `steam_appid` as primary key
- No console game IDs
- No cross-platform identifiers
- Schema: `src/models/database.py`

**ETL Pipelines:**
- All import scripts target Steam data sources
- Located in: `src/etl/`
- No console or mobile data pipelines

### Future Cross-Platform Potential:

**Could be added (with significant work):**
1. **Epic Games Store** - Has limited API
2. **GOG** - Has public API
3. **Itch.io** - Has API access

**Challenging to add:**
- PlayStation Network - Restricted data access
- Xbox Live - Requires Microsoft partnership
- Nintendo - Very limited public data
- Mobile stores - Different data structures

**Design considerations for expansion:**
- Would need platform identifier field in database
- Separate API clients for each platform
- Data normalization challenges (different metrics)
- Platform-specific analytics pages

### Current Use Case:

**Best for:**
✅ PC game developers targeting Steam
✅ Indie developers planning Steam releases
✅ Market research on Steam ecosystem
✅ Competitive analysis of Steam games
✅ Genre analysis on PC platform
✅ Pricing strategy for Steam

**Not ideal for:**
❌ Console-exclusive analysis
❌ Mobile game market research
❌ Cross-platform sales comparison
❌ PlayStation/Xbox market insights
❌ Multi-store strategy planning

### Platform Summary:

| Platform | Supported | Data Sources | Coverage |
|----------|-----------|--------------|----------|
| Steam (Windows) | ✅ Yes | Full API access | 213K+ games |
| Steam (Mac) | ✅ Yes | Full API access | Subset of Steam |
| Steam (Linux) | ✅ Yes | Full API access | Subset of Steam |
| Epic Games | ❌ No | - | - |
| PlayStation | ❌ No | - | - |
| Xbox | ❌ No | - | - |
| Switch | ❌ No | - | - |
| Mobile | ❌ No | - | - |

**Disclaimer:**
This project is not affiliated with, endorsed by, or connected to Valve Corporation or Steam. All game data is obtained through publicly available APIs and web pages in accordance with Steam's terms of service.

---

## Additional Resources

For more detailed information, see:

- **[README.md](README.md)** - Quick start guide and project overview
- **[DOCUMENTATION.md](docs/DOCUMENTATION.md)** - Complete feature guide and API reference
- **[CONTRIBUTING.md](docs/CONTRIBUTING.md)** - Development setup and contribution guidelines

## Need Help?

- Open an issue on GitHub for bugs or feature requests
- Check existing documentation in the `/docs` folder
- Review the dashboard's built-in tooltips and help text

---

**Last Updated:** November 16, 2025  
**Platform Version:** Phase 3 Complete  
**Database:** 213,386 games, 86-92% data coverage
