# Steam Insights Platform Capabilities - Quick Reference

**Last Updated:** November 16, 2025

This is a quick-reference summary. For detailed information, see [FAQ.md](FAQ.md).

---

## Quick Answers to Key Questions

| # | Question | Answer | Details |
|---|----------|--------|---------|
| 1 | **Player overlap between two games?** | ✅ **YES** | Market Analysis page - overlap estimation based on genre similarity |
| 2 | **Playtime, retention, engagement tracking?** | ⚠️ **PARTIAL** | Playtime: YES, Retention: NO, Engagement: LIMITED |
| 3 | **Filter by game features or tags?** | ✅ **YES** | Extensive filtering by genres/tags across multiple pages |
| 4 | **Review sentiment or player feedback?** | ⚠️ **PARTIAL** | Infrastructure ready, manual data import required |
| 5 | **Data granularity level?** | ✅ **GAME & SEGMENTS** | Game-level and aggregate segments, no user-level |
| 6 | **Export and visualization capabilities?** | ✅ **YES** | CSV, JSON, Excel, Parquet exports + interactive charts |
| 7 | **Platform coverage?** | ✅ **STEAM ONLY** | All Steam games (213K+), no console/mobile support |

---

## Feature Availability Matrix

### ✅ Fully Available Features

| Feature | What's Available | Where to Find |
|---------|------------------|---------------|
| **Game Overlap Analysis** | Two-game comparison, overlap estimation, addressable market | Market Analysis page (Launch & Analytics) |
| **Playtime Tracking** | Average playtime, peak playtime, median playtime | Game Explorer, Analytics pages |
| **Genre Filtering** | 86% coverage, 730K associations, multi-select filters | Game Explorer, Genre Analysis, Competition Analysis |
| **Tag Filtering** | 91.6% coverage, 944K associations, tag combinations | Tag Strategy, Competition Calculator |
| **Data Export** | CSV, JSON, Excel, Parquet formats | Data Management → Export Data |
| **Visualizations** | Interactive Plotly charts (bar, line, scatter, pie, heatmaps) | All analytics pages |
| **Player Counts** | Current players, peak 24h, historical trends | Analytics, Game Explorer |
| **Pricing Data** | Current prices, discounts, historical pricing | Game Explorer, Pricing Strategy |
| **Genre Analysis** | Market share, saturation, opportunities | Genre Analysis, Market Opportunities |

### ⚠️ Partially Available Features

| Feature | What's Available | What's Missing | Why |
|---------|------------------|----------------|-----|
| **Retention Metrics** | Time-series player counts | Day 1/7/30 retention rates | Steam API doesn't provide |
| **Engagement Metrics** | Average playtime, player counts | DAU/MAU, session frequency | Public API limitations |
| **Review Sentiment** | Database models, LLM infrastructure | Bulk review data | Manual import required |
| **Achievement Data** | Database model exists | Population of data | Not yet implemented |

### ❌ Not Available Features

| Feature | Reason |
|---------|--------|
| **Individual Player Data** | Privacy restrictions |
| **Cross-Platform Support** | Steam-only data sources |
| **Console Data** | No access to PlayStation/Xbox/Switch APIs |
| **Mobile Game Data** | Different ecosystems, no API access |
| **Real Player Overlap** | Steam doesn't provide cross-game player data |

---

## Where to Find Key Features

### Market Analysis & Overlap
- **Navigate:** Development Stage → "🚀 Launch & Analytics" → "📈 Market Position"
- **Features:** Two-game comparison, overlap estimation, addressable market
- **Code:** `src/dashboard/modules/postlaunch_pages.py` → `show_market_analysis()`

### Playtime & Player Stats
- **Navigate:** "🎮 Game Explorer" or "📈 Advanced Analytics"
- **Features:** Average/peak/median playtime, current/peak players, time-series
- **Database:** `player_stats` table (average_playtime_minutes, peak_playtime_minutes)

### Genre & Tag Filtering
- **Game Explorer:** Real-time filtering of 213K+ games
- **Genre Analysis:** "💡 Concept & Research" → "📊 Genre Analysis"
- **Tag Strategy:** "🎨 Pre-Production & Validation" → "🏷️ Tag Strategy"
- **Competition Analysis:** "🎨 Pre-Production & Validation" → "🎯 Competition Analysis"

### Review Sentiment
- **Navigate:** "⚙️ Data Management" → "🤖 LLM Data Mining"
- **Database:** `reviews` table (is_positive), `game_enrichments` table (sentiment_score)
- **Status:** Infrastructure ready, data import needed

### Export & Visualization
- **Export:** "⚙️ Data Management" → "⚙️ System Settings" → "📤 Export Data"
- **Visualizations:** Available on all analytics pages (interactive Plotly charts)
- **API:** RESTful API at http://localhost:8000 with OpenAPI docs at /docs

---

## Data Coverage & Quality

| Metric | Value | Coverage |
|--------|-------|----------|
| **Total Games** | 213,386 | - |
| **Tag Coverage** | 195,380 games | 91.6% |
| **Genre Coverage** | 183,516 games | 86.0% |
| **Release Dates** | 179,249 games | 84.0% |
| **Tag Associations** | 944,000+ | - |
| **Genre Associations** | 730,000+ | - |
| **Player Stats** | 6,400+ games | 3.0% (growing) |

---

## Platform Support

### ✅ Supported
- **Steam (Windows)** - Full support
- **Steam (Mac)** - Full support  
- **Steam (Linux)** - Full support

### ❌ Not Supported
- Epic Games Store
- PlayStation (PS4, PS5)
- Xbox (One, Series X/S)
- Nintendo Switch
- Mobile (iOS, Android)
- GOG, Itch.io, other PC stores

---

## Technical Architecture

### Data Sources
1. **Steam Web API** - Real-time player counts, achievements
2. **Steam Store API** - Game metadata, pricing, reviews
3. **SteamSpy API** - Ownership estimates, playtime statistics
4. **Zenodo Academic Dataset** - Historical data, genres, tags

### Export Capabilities
- **Formats:** CSV, JSON, Excel (.xlsx), Parquet
- **API:** RESTful FastAPI backend with OpenAPI documentation
- **Programmatic Access:** Available at http://localhost:8000

### Database Schema
- **Primary Key:** `steam_appid` (Steam's unique game identifier)
- **Key Tables:** games, player_stats, reviews, genres, tags, pricing_history
- **Relationships:** Many-to-many (games ↔ genres, games ↔ tags)

---

## Use Case Recommendations

### ✅ Best For:
- PC game developers targeting Steam
- Indie developers planning Steam releases
- Market research on Steam ecosystem
- Competitive analysis of Steam games
- Genre analysis on PC platform
- Pricing strategy for Steam

### ⚠️ Limited For:
- Retention analysis (only playtime available)
- Individual player behavior (privacy restricted)
- Review sentiment analysis (data import needed)

### ❌ Not Suitable For:
- Console-exclusive analysis
- Mobile game market research
- Cross-platform sales comparison
- PlayStation/Xbox market insights
- Multi-store strategy planning

---

## Quick Links

- **[FAQ.md](FAQ.md)** - Detailed answers to all questions
- **[README.md](README.md)** - Quick start guide
- **[DOCUMENTATION.md](docs/DOCUMENTATION.md)** - Complete feature guide
- **[CONTRIBUTING.md](docs/CONTRIBUTING.md)** - Development setup

---

## Summary

The Steam Insights platform is a **comprehensive Steam-focused analytics tool** that excels at:
- Game-level market analysis
- Genre and tag-based filtering
- Ownership overlap estimation
- Playtime tracking
- Data export and visualization

It has **limitations** in:
- Detailed retention metrics (API constraints)
- Review sentiment analysis (manual import needed)
- Cross-platform support (Steam-only)
- User-level data (privacy restrictions)

For detailed information on any feature, see the comprehensive [FAQ.md](FAQ.md) document.
