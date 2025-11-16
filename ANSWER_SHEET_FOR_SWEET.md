# Dashboard Capability Confirmation for Sweet

**Date:** November 16, 2025  
**Platform:** Steam Insights Dashboard  
**Status:** All questions answered with portal references

---

## Direct Answers to Your 7 Questions

### 1. Can your platform show overlap between players of two specific games?

**✅ YES**

**Where to find it:**
- Navigate in the dashboard: **Development Stage** dropdown → Select "🚀 Launch & Analytics" → Click "📈 Market Position"
- Or: Use the Market Analysis page in the Post-Launch Analytics section

**What you can see:**
- Select any two games from our 213K+ game database
- View estimated overlap percentage (calculated 10-40% based on genre similarity)
- See addressable market size for each game (non-overlapping audience)
- Add multiple games for extended market analysis
- Visual metrics and overlap calculations

**Important note:** 
The overlap is *estimated* based on genre similarity using Jaccard coefficient, not actual individual player data. Steam's privacy policies prevent access to cross-game individual player libraries. This gives you a reliable market-sizing estimation tool.

---

### 2. Do you track playtime, retention, or engagement across those audiences?

**⚠️ YES for Playtime, LIMITED for Retention/Engagement**

#### ✅ What WE DO Track:

**Playtime Metrics** (Available Now):
- Average playtime (in minutes) per game
- Peak playtime (historical maximum)
- Median playtime (middle value across all players)
- Time-series tracking of player counts

**Player Activity** (Available Now):
- Current concurrent players (real-time)
- Peak players in last 24 hours
- Historical player count trends
- Estimated total owners per game

**Where to find it:**
- "🎮 Game Explorer" - Individual game details with playtime stats
- "📈 Advanced Analytics" - Time-series charts and trends
- Player Analytics tab - Compare games and view trends

#### ❌ What We DON'T Track (Yet):

**Retention Metrics** (Not Available):
- Day 1, Day 7, Day 30 retention rates
- Player return frequency
- Churn analysis
- Cohort retention curves

**Engagement Metrics** (Not Available):
- Daily Active Users (DAU) / Monthly Active Users (MAU)
- Session frequency distribution
- Feature usage patterns within games
- Achievement completion rates

**Why these limitations?**
Steam's public APIs don't provide individual player-level retention data or session-level engagement metrics. These require either:
1. Direct game developer access to their own analytics
2. Private partnerships with Valve (which we don't have)
3. Individual player tracking (blocked by privacy policies)

**Bottom line:** Great for playtime and player count trends, but not for detailed retention/engagement analytics.

---

### 3. Can we filter or compare by game features or tags (e.g., genres, mechanics)?

**✅ YES - Extensively**

**Coverage:**
- **213,386 games** in database
- **91.6% have tags** (195,380 games with 944K tag associations)
- **86.0% have genres** (183,516 games with 730K genre associations)

**Where to find filtering:**

1. **Game Explorer** (🎮 Game Explorer)
   - Multi-select genre filter
   - Tag filtering
   - Platform filters (Windows/Mac/Linux)
   - Search by name
   - Sort by popularity, release date, name

2. **Genre Analysis** (📊 Genre Analysis)
   - Under "💡 Concept & Research" stage
   - Full genre performance metrics
   - Market share by genre
   - Saturation analysis

3. **Tag Strategy** (🏷️ Tag Strategy)
   - Under "🎨 Pre-Production & Validation" stage
   - Analyze winning tag combinations
   - Find successful patterns
   - See which combos lead to high ownership

4. **Competition Analysis** (🎯 Competition Analysis)
   - Under "🎨 Pre-Production & Validation" stage
   - Filter by genre/tag combinations
   - Analyze competition level
   - Find successful games with specific tags

5. **Genre Saturation** (📊 Genre Saturation)
   - Under "💡 Concept & Research" stage
   - Opportunity scoring by genre
   - Competition indicators

**What you can filter/compare:**
- Genres (Action, RPG, Strategy, etc.)
- Tags (Multiplayer, Singleplayer, Co-op, etc.)
- Price ranges
- Platform support
- Release date ranges
- Ownership levels

---

### 4. Do you include review sentiment or player feedback data from Steam?

**⚠️ PARTIAL - Infrastructure Ready, Data Import Needed**

#### What's Available:

**Database Models** (Built and Ready):
- Review storage system with positive/negative classification
- Sentiment scoring (-1.0 to +1.0 scale)
- LLM-powered sentiment analysis infrastructure
- Vote counts (helpful, funny)
- Playtime at review time

**Where to find it:**
- Navigate: "⚙️ Data Management" → "🤖 LLM Data Mining"
- This page shows sentiment scores and AI-analyzed feedback

#### Current Status:

**✅ Ready:**
- Complete database schema for reviews
- LLM enrichment system for sentiment extraction
- Batch processing for large-scale analysis
- Dashboard pages to display sentiment

**⚠️ Requires Work:**
- Bulk review data must be manually imported (not automatic)
- Steam's Review API requires authenticated requests
- LLM sentiment processing is opt-in (takes time)

**Available Now:**
- Review counts (positive/negative totals) from SteamSpy
- Basic review metrics on game pages

**Future Enhancement:**
The infrastructure is 100% ready. The main work needed is setting up the Steam Review API scraper to populate the database, then running LLM batch jobs to analyze sentiment. This is technically feasible but not currently populated with data.

---

### 5. How granular is the data — game-level, audience segment, or user-level?

**✅ GAME-LEVEL and AGGREGATE SEGMENTS**

#### Game-Level Data (Primary - Fully Available):
- Complete metadata for all 213,386 games
- Individual game statistics
- Platform support per game
- Genres and tags per game
- Pricing history per game
- Player counts per game
- Playtime metrics per game
- Review counts per game

**Where to find it:** Every page in the dashboard shows game-level data

#### Aggregate Audience Segments (Available):

**Genre-Based Segments:**
- Total games per genre
- Average ownership per genre
- Success rates by genre
- Competition levels

**Tag-Based Segments:**
- Games grouped by tag combinations
- Performance by tag clusters
- Market opportunities by tags

**Price-Tier Segments:**
- Analysis by price ranges ($0-5, $5-10, $10-15, etc.)
- Success rates by pricing tier
- Revenue estimates by tier

**Platform Segments:**
- Windows vs Mac vs Linux
- Multi-platform vs exclusive

**Where to find it:**
- "📊 Genre Analysis" - Genre aggregates
- "🌟 Market Opportunities" - Segment identification
- "💰 Pricing Strategy" - Price-tier analysis
- "🎯 Competition Analysis" - Tag segmentation

#### User-Level Data (NOT Available):
**Cannot provide:**
- Individual player identities
- Personal gaming libraries
- Cross-game player behavior
- Individual player progression
- User demographics

**Why not?**
- Steam privacy policies restrict this
- Public APIs only provide aggregates
- We respect player privacy
- No individual player tracking capability

**Summary:** You get detailed game-level metrics and market segments, but not individual player tracking.

---

### 6. Can we export or visualize that overlap and engagement data ourselves?

**✅ YES - Comprehensive Export and Visualization**

#### Export Functionality:

**Where to find it:**
- Navigate: "⚙️ Data Management" → "⚙️ System Settings" → "📤 Export Data" tab

**Export Formats Available:**
- **CSV** (comma-separated values)
- **JSON** (structured data)
- **Excel** (.xlsx files)
- **Parquet** (for big data analysis)

**What You Can Export:**

1. **Games Catalog**
   - All game metadata
   - Platform support
   - Release dates
   - Ownership estimates
   - Filter before export

2. **Player Statistics**
   - Current players
   - Peak players (24h)
   - Estimated owners
   - Average playtime
   - Time-series data

3. **Genre Analysis**
   - Performance metrics
   - Game counts per genre
   - Success rates
   - Market saturation

4. **Market Analysis Results**
   - Overlap calculations
   - Addressable market data
   - Custom analysis results

#### Visualization Capabilities:

**Built-in Interactive Charts** (Throughout Dashboard):
- Bar charts (genre distribution, competition)
- Line charts (time-series player counts)
- Scatter plots (market opportunities, price vs success)
- Pie charts (market share)
- Heatmaps (correlation analysis)
- Treemaps (developer market share)

**All charts are interactive:**
- Hover for details
- Zoom and pan
- Click to filter
- Export as images

**Where you'll see them:**
- Every analytics page has visualizations
- 4+ tabs in Advanced Analytics
- Market Analysis has overlap visuals
- Forecasting charts available

#### API Access:

**RESTful API Available:**
- Endpoint: `http://localhost:8000`
- Full documentation: `http://localhost:8000/docs`
- Programmatic access to all data
- Query parameters for filtering

**Example API Endpoints:**
```
GET /games - List games with pagination
GET /games/{app_id} - Get specific game data
GET /games/{app_id}/stats - Player statistics
GET /genres - List all genres
GET /analytics/overlap - Game overlap analysis
```

**Use Your Own Tools:**
Export data and analyze in:
- Excel / Google Sheets
- Tableau / Power BI
- Python (pandas, matplotlib)
- R (ggplot2)
- Custom applications

**Summary:** Full export capabilities in multiple formats + interactive visualizations + API access. You can get the raw data for your own analysis.

---

### 7. What platforms does this work for — just Steam, or cross-platform too?

**✅ STEAM ONLY (PC Gaming Platform)**

#### Supported Platforms:

**Steam (All Versions):**
- ✅ Windows games (full support)
- ✅ Mac games (full support)
- ✅ Linux games (full support)
- ✅ 213,386 total games
- ✅ Complete Steam ecosystem

**Within Steam, we track which OS each game supports:**
- Windows compatibility
- Mac compatibility
- Linux compatibility
- Multi-platform games

#### NOT Supported (Currently):

**Console Platforms:**
- ❌ PlayStation (PS4, PS5)
- ❌ Xbox (One, Series X/S)
- ❌ Nintendo Switch

**Other PC Stores:**
- ❌ Epic Games Store
- ❌ GOG
- ❌ Itch.io
- ❌ Origin / EA App
- ❌ Ubisoft Connect

**Mobile:**
- ❌ iOS (Apple App Store)
- ❌ Android (Google Play)

#### Why Steam Only?

**Technical Reasons:**
1. Steam has the most comprehensive public APIs
2. SteamSpy provides unique ownership estimates
3. Other platforms have restricted data access
4. Focus allows deeper Steam-specific insights
5. Steam is 90%+ of PC gaming market

**Data Sources (All Steam-focused):**
- Steam Web API (official Valve)
- Steam Store API (metadata, pricing)
- SteamSpy API (ownership, playtime)
- Zenodo Academic Dataset (historical Steam data)

#### Cross-Platform Considerations:

**What We CAN Tell You:**
- If a Steam game is also on other platforms (when mentioned in store data)
- But no actual sales/player data from those other platforms

**What We CANNOT Tell You:**
- PlayStation/Xbox sales or player counts
- Epic Games Store exclusivity impact
- Console vs PC performance comparisons
- Mobile game market data
- Cross-store ownership overlap

#### Best Use Cases:

**✅ Ideal For:**
- PC game developers targeting Steam
- Indie developers planning Steam releases
- Market research on Steam/PC ecosystem
- Competitive analysis of Steam games
- Genre analysis for PC platform
- Pricing strategy for Steam

**❌ Not Suitable For:**
- Console-exclusive market research
- Mobile game analysis
- Cross-platform strategy planning
- Epic Games Store specific insights
- Multi-store sales comparison

---

## Summary Table

| Question | Answer | Portal Location |
|----------|--------|-----------------|
| **1. Player overlap?** | ✅ YES | Market Analysis page (Launch & Analytics → Market Position) |
| **2. Playtime/retention/engagement?** | ⚠️ Playtime: YES<br>Retention: NO<br>Engagement: LIMITED | Game Explorer, Analytics pages (playtime)<br>*Retention APIs not available* |
| **3. Filter by features/tags?** | ✅ YES | Game Explorer, Genre Analysis, Tag Strategy, Competition Analysis |
| **4. Review sentiment/feedback?** | ⚠️ Infrastructure: YES<br>Data: MANUAL IMPORT | LLM Data Mining page (Data Management section)<br>*Requires data import* |
| **5. Data granularity?** | ✅ Game-level: YES<br>Segments: YES<br>User-level: NO | All pages (game-level)<br>*User data restricted by privacy* |
| **6. Export/visualize?** | ✅ YES | Export: Data Management → System Settings → Export Data<br>Visualizations: All analytics pages<br>API: localhost:8000/docs |
| **7. Platform coverage?** | ✅ Steam: YES<br>Others: NO | All pages show Steam data<br>*213K+ Steam games only* |

---

## Quick Stats

- **Total Games:** 213,386
- **Tag Coverage:** 91.6% (195,380 games)
- **Genre Coverage:** 86.0% (183,516 games)
- **Export Formats:** CSV, JSON, Excel, Parquet
- **Visualization Types:** 6+ interactive chart types
- **API Access:** Yes (RESTful with OpenAPI docs)
- **Platform Support:** Steam only (Windows, Mac, Linux)

---

## For More Details

- **Full FAQ:** [FAQ.md](FAQ.md) - Comprehensive answers with technical details
- **Quick Reference:** [CAPABILITY_SUMMARY.md](CAPABILITY_SUMMARY.md) - One-page feature matrix
- **Documentation:** [DOCUMENTATION.md](docs/DOCUMENTATION.md) - Complete feature guide
- **Getting Started:** [README.md](README.md) - Quick start guide

---

**Bottom Line:**

This platform is a **comprehensive Steam analytics tool** that excels at market analysis, genre/tag filtering, and data export for PC games on Steam. It provides estimated player overlap, extensive playtime tracking, and powerful visualization tools.

**Strengths:**
- ✅ Market overlap estimation
- ✅ Comprehensive filtering
- ✅ Extensive exports
- ✅ Game-level analytics

**Limitations:**
- ⚠️ No detailed retention metrics (API constraints)
- ⚠️ Review sentiment requires manual setup
- ⚠️ Steam-only (no console/mobile)
- ⚠️ No individual player tracking (privacy)

**Best for:** PC game developers and publishers planning Steam releases or conducting Steam market research.
