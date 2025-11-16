# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    postgresql-client \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project
COPY . .

# Create necessary directories
RUN mkdir -p data/raw data/processed data/feedback data/steam_pages

# Set Python path
ENV PYTHONPATH=/app

# Expose the dashboard port
EXPOSE 8502

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8502/_stcore/health || exit 1

# Run the Streamlit dashboard
CMD ["streamlit", "run", "src/dashboard/app.py", "--server.port=8502", "--server.address=0.0.0.0", "--server.headless=true"]
