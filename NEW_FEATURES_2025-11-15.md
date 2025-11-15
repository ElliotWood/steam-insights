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
