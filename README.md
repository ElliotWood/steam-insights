# Steam Insights

A comprehensive analytics dashboard for Steam games, providing insights into player statistics, pricing history, genre analysis, and market overlap analysis.

## 🌟 Features

### Core Capabilities
- **Game Database**: Store and manage information about Steam games
- **Player Statistics**: Track current and historical player counts
- **Pricing History**: Monitor game prices and discounts over time
- **Genre Analysis**: Analyze games by genre and category
- **Market Analysis**: Game ownership overlap and addressable market analysis
- **Advanced Analytics**: Forecasting, correlation analysis, and trend detection
- **Data Management**: Bulk import, export to CSV/JSON, database health monitoring

### Technical Features
- **REST API**: FastAPI-based backend with automatic OpenAPI documentation
- **Interactive Dashboard**: Professional Streamlit interface with 6 pages
- **ETL Pipeline**: Automated data import from Steam API and web scraping
- **Multiple Data Sources**: Steam Web API, Steam Store API, web scraper support
- **Performance Optimized**: Caching, database indexing, batch operations

## 📋 Prerequisites

- Python 3.8 or higher
- PostgreSQL (optional, SQLite is used by default)
- Steam Web API Key (free from [steamcommunity.com/dev](https://steamcommunity.com/dev))

## 🚀 Quick Start

### 1. Installation

Clone the repository:
```bash
git clone https://github.com/ElliotWood/steam-insights.git
cd steam-insights
```

Install dependencies:
```bash
pip install -r requirements.txt
```

### 2. Configuration

Copy the example environment file:
```bash
cp .env.example .env
```

Edit `.env` and add your Steam API key:
```
STEAM_API_KEY=your_steam_api_key_here
```

### 3. Initialize Database

The database will be automatically created when you first run the application. By default, it uses SQLite.

### 4. Run the Dashboard

Start the Streamlit dashboard:
```bash
streamlit run src/dashboard/app.py
```

The dashboard will open in your browser at `http://localhost:8501`

### 5. Run the API (Optional)

Start the FastAPI backend:
```bash
python -m uvicorn src.api.main:app --reload
```

The API will be available at `http://localhost:8000`
API documentation: `http://localhost:8000/docs`

## 📊 Dashboard Pages

The dashboard includes 6 professional pages:

1. **Overview** - Key metrics, genre distribution, top performers
2. **Game Search** - Search and explore individual games with detailed stats
3. **Analytics** - Advanced charts with player analytics, market insights, and trend analysis
4. **Market Analysis** - Game ownership overlap and addressable market calculations
5. **Advanced Analytics** - Correlations, forecasting, growth trends, and genre performance
6. **Data Management** - Import games, bulk operations, export data, database stats

### Quick Start Usage

1. **Import Data**: Navigate to "Data Management" → Enter Steam App ID → Click "Import Game"
2. **View Analytics**: Visit "Overview" for quick insights or "Analytics" for detailed charts
3. **Analyze Markets**: Use "Market Analysis" to compare game audiences
4. **Export Data**: Go to "Data Management" → "Export" tab → Download CSV/JSON

## 🏗️ Architecture

```
Steam API → Steam Client → Game Importer → Database ← Dashboard
                                              ↕
Steam Store → Web Scraper ────────────────→ Database ← API Server
```

**Key Technologies**: Python 3.8+, FastAPI, Streamlit, SQLAlchemy, PostgreSQL/SQLite, Plotly

## 📝 Documentation

For comprehensive information, see:

- **[README.md](README.md)** (this file) - Quick start guide and project overview
- **[DOCUMENTATION.md](DOCUMENTATION.md)** - Complete feature guide, API reference, and architecture
- **[CONTRIBUTING.md](CONTRIBUTING.md)** - Development setup and contribution guidelines
- **[TEST_REPORT.md](TEST_REPORT.md)** - Test coverage and quality metrics

## 🧪 Testing

Run tests with pytest:

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest --cov=src tests/
```

**Test Results**: 42/42 tests passing ✅ | Coverage: 58% overall, 100% on critical components

## 🤝 Contributing

Contributions are welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup and guidelines.

## 📝 License

This project is open source and available under the MIT License.

## 🙏 Acknowledgments

- Data sourced from Steam Web API and Steam Store
- Inspired by Sensor Tower's Video Game Insights
- Built with FastAPI, Streamlit, SQLAlchemy, and Plotly

## ⚠️ Disclaimer

This project is not affiliated with, endorsed by, or connected to Valve Corporation or Steam. All game data is obtained through publicly available APIs and web pages in accordance with Steam's terms of service.

## 📞 Support

For issues, questions, or suggestions, please open an issue on GitHub.
