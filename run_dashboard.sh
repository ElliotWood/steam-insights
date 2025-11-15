#!/bin/bash
# Run the Steam Insights Dashboard

echo "🎮 Starting Steam Insights Dashboard..."
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Virtual environment not found. Creating one..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
fi

# Activate virtual environment
source venv/bin/activate

# Check if dependencies are installed
if [ ! -f "venv/.dependencies_installed" ]; then
    echo "Installing dependencies..."
    pip install -q -r requirements.txt
    touch venv/.dependencies_installed
    echo "✅ Dependencies installed"
fi

# Run setup if database doesn't exist
if [ ! -f "steam_insights.db" ]; then
    echo "Running initial setup..."
    python setup.py
fi

# Start the dashboard
echo ""
echo "Starting Streamlit dashboard..."
echo "Dashboard will open at: http://localhost:8501"
echo ""
streamlit run src/dashboard/app.py
