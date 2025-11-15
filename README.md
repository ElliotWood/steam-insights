# Steam Insights

A comprehensive analytics dashboard for Steam games, providing insights into player statistics, pricing history, genre analysis, and market overlap analysis.

## 🌟 Features

- **Game Database**: Store and manage information about Steam games
- **Player Statistics**: Track current and historical player counts
- **Pricing History**: Monitor game prices and discounts over time
- **Genre Analysis**: Analyze games by genre and category
- **Market Analysis**: Game ownership overlap and addressable market analysis
- **REST API**: FastAPI-based backend for data access
- **Interactive Dashboard**: Streamlit-based web interface (5 pages)
- **Data Import**: ETL pipeline for importing game data from Steam API
- **Web Scraping**: Supplementary data collection from Steam store pages

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

## 📊 Usage

### Importing Games

1. Navigate to the "Data Management" page in the dashboard
2. Enter a Steam App ID (found in the Steam store URL)
3. Click "Import Game" to fetch and store game data
4. Or use the quick import buttons for popular games

### Viewing Analytics

1. Navigate to the "Overview" page for key statistics
2. Use "Game Search" to find and view specific games
3. Visit "Analytics" for charts and trends

### Using the API

Example API requests:

```bash
# List games
curl http://localhost:8000/games

# Get game details
curl http://localhost:8000/games/730

# Get player statistics
curl http://localhost:8000/games/730/player-stats?days=7

# List genres
curl http://localhost:8000/genres
```

## 🏗️ Project Structure

```
steam-insights/
├── src/
│   ├── api/           # FastAPI backend
│   │   ├── main.py    # API endpoints
│   │   └── steam_client.py  # Steam API client
│   ├── database/      # Database connection
│   │   └── connection.py
│   ├── models/        # Database models
│   │   └── database.py
│   ├── etl/          # ETL pipeline
│   │   └── game_importer.py
│   ├── scrapers/     # Web scrapers
│   │   └── steam_scraper.py
│   ├── dashboard/    # Streamlit dashboard
│   │   └── app.py
│   └── utils/        # Utility functions
│       └── logging_config.py
├── config/           # Configuration files
│   └── settings.py
├── tests/           # Test files
├── data/            # Data storage
│   ├── raw/        # Raw data files
│   └── processed/  # Processed data
├── requirements.txt  # Python dependencies
├── .env.example     # Environment variables template
└── README.md        # This file
```

## 🗄️ Database Schema

The application uses the following main database tables:

- **games**: Game metadata (name, developer, publisher, release date, etc.)
- **genres**: Game genres
- **tags**: Game tags/categories
- **player_stats**: Historical player count data
- **pricing_history**: Price tracking over time
- **reviews**: User reviews
- **achievements**: Game achievements

## 🔧 Configuration

### Environment Variables

- `STEAM_API_KEY`: Your Steam Web API key
- `DATABASE_URL`: Database connection string (default: SQLite)
- `DEBUG`: Enable debug mode (default: False)
- `LOG_LEVEL`: Logging level (default: INFO)
- `API_HOST`: API host address (default: 0.0.0.0)
- `API_PORT`: API port (default: 8000)
- `DASHBOARD_PORT`: Dashboard port (default: 8501)

### Using PostgreSQL

To use PostgreSQL instead of SQLite, update your `.env` file:

```
DATABASE_URL=postgresql://user:password@localhost:5432/steam_insights
```

## 📈 Available Data Sources

The project can import data from:

1. **Steam Web API**: Real-time game data, player counts, achievements
2. **Steam Store API**: Game details, pricing, reviews
3. **Kaggle Datasets**: Historical game data (manual import)
4. **Web Scraping**: Supplementary data from Steam store pages

## 🧪 Testing

Run tests with pytest:

```bash
pytest tests/
```

Run with coverage:

```bash
pytest --cov=src tests/
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

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
