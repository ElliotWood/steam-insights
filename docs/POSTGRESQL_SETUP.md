# PostgreSQL + pgvector Setup Guide

## Quick Setup for Windows

### Step 1: Install PostgreSQL (5 minutes)

**Option A: Using Chocolatey (Recommended)**
```powershell
# Install Chocolatey if not already installed
Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

# Install PostgreSQL
choco install postgresql -y

# Add to PATH
$env:Path += ";C:\Program Files\PostgreSQL\16\bin"
```

**Option B: Manual Download**
1. Download from: https://www.postgresql.org/download/windows/
2. Run installer (accept defaults)
3. Remember the password you set for `postgres` user
4. Add `C:\Program Files\PostgreSQL\16\bin` to your PATH

### Step 2: Create Database (2 minutes)

```powershell
# Connect to PostgreSQL
psql -U postgres

# In PostgreSQL console:
CREATE DATABASE steam_insights;
CREATE USER steam_user WITH ENCRYPTED PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE steam_insights TO steam_user;
\q
```

### Step 3: Install pgvector Extension (3 minutes)

```powershell
# Connect to your database
psql -U postgres -d steam_insights

# Install extension
CREATE EXTENSION IF NOT EXISTS vector;

# Verify installation
SELECT * FROM pg_extension WHERE extname = 'vector';
\q
```

**Note:** If pgvector isn't available, you may need to install it separately:
```powershell
# Download precompiled pgvector for Windows from:
# https://github.com/pgvector/pgvector/releases
# Extract and copy to PostgreSQL extension directory
```

### Step 4: Update .env Configuration (1 minute)

Edit `c:\repo\steam-insights\.env`:

```env
# Replace SQLite with PostgreSQL
DATABASE_URL=postgresql://steam_user:your_secure_password@localhost:5432/steam_insights

# Or keep commented for individual params:
DB_HOST=localhost
DB_PORT=5432
DB_NAME=steam_insights
DB_USER=steam_user
DB_PASSWORD=your_secure_password
```

### Step 5: Migrate Existing Data (Optional)

If you have data in SQLite, migrate it:

```powershell
# Export from SQLite
.\venv\Scripts\python.exe -c "
import sqlite3
import pandas as pd
conn = sqlite3.connect('steam_insights.db')
tables = pd.read_sql('SELECT name FROM sqlite_master WHERE type=\"table\"', conn)
for table in tables['name']:
    df = pd.read_sql(f'SELECT * FROM {table}', conn)
    df.to_csv(f'data/migration/{table}.csv', index=False)
conn.close()
"

# Import to PostgreSQL (run after schema creation)
.\venv\Scripts\python.exe scripts\import_from_sqlite.py
```

## Verification

```powershell
# Test connection
.\venv\Scripts\python.exe -c "
from src.database.connection import engine
from sqlalchemy import text
with engine.connect() as conn:
    result = conn.execute(text('SELECT version()'))
    print(result.fetchone()[0])
"
```

## Troubleshooting

### pgvector not found
- Download from: https://github.com/pgvector/pgvector/releases
- Look for Windows builds or compile from source

### Connection refused
- Check PostgreSQL service is running: `Get-Service postgresql*`
- Start if needed: `Start-Service postgresql-x64-16`

### Permission denied
- Ensure user has proper grants
- Check `pg_hba.conf` for authentication settings

## Alternative: Docker Setup (Fastest)

```powershell
# Pull PostgreSQL with pgvector
docker pull pgvector/pgvector:pg16

# Run container
docker run -d `
  --name steam-insights-db `
  -e POSTGRES_DB=steam_insights `
  -e POSTGRES_USER=steam_user `
  -e POSTGRES_PASSWORD=your_password `
  -p 5432:5432 `
  pgvector/pgvector:pg16

# Update .env with connection string
DATABASE_URL=postgresql://steam_user:your_password@localhost:5432/steam_insights
```

This is the fastest way to get started!
