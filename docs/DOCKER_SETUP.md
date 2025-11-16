# Docker Setup Guide

## Overview

This project uses Docker Compose to run both the PostgreSQL database and the Streamlit dashboard in containers. The services are connected via a Docker network and can communicate with each other.

## Services

### PostgreSQL Database
- **Container Name**: `steam-insights-db`
- **Port**: 5432 (exposed to host)
- **Image**: pgvector/pgvector:pg16
- **Network**: steam-insights-network
- **Data Persistence**: Uses named volume `postgres_data`

### Dashboard
- **Container Name**: `steam-insights-dashboard`
- **Port**: 8502 (exposed to host)
- **Network**: steam-insights-network
- **Database Connection**: Connects to PostgreSQL via internal Docker network

## Quick Start

### 1. Build and Start Services

```bash
# Build and start all services in detached mode
docker-compose up --build -d

# Or start without rebuilding
docker-compose up -d
```

### 2. Access the Dashboard

Open your browser and navigate to:
```
http://localhost:8502
```

### 3. Check Service Status

```bash
# View running containers
docker-compose ps

# View logs for all services
docker-compose logs

# View logs for specific service
docker-compose logs dashboard
docker-compose logs postgres
```

## Environment Variables

Create a `.env` file in the project root to customize settings:

```env
# Database
DB_PASSWORD=steaminsights2025
DB_NAME=steam_insights
DB_USER=steam_user

# Steam API
STEAM_API_KEY=your_steam_api_key_here

# Dashboard
DASHBOARD_PORT=8502
```

## Common Commands

### Stop Services
```bash
# Stop all services
docker-compose stop

# Stop specific service
docker-compose stop dashboard
```

### Restart Services
```bash
# Restart all services
docker-compose restart

# Restart specific service
docker-compose restart dashboard
```

### Rebuild Services
```bash
# Rebuild and restart all services
docker-compose up --build -d

# Rebuild specific service
docker-compose up --build -d dashboard
```

### View Logs
```bash
# Follow logs for all services
docker-compose logs -f

# Follow logs for dashboard only
docker-compose logs -f dashboard

# View last 100 lines of logs
docker-compose logs --tail=100 dashboard
```

### Stop and Remove Containers
```bash
# Stop and remove containers (keeps volumes)
docker-compose down

# Stop and remove containers and volumes (deletes data)
docker-compose down -v
```

## Database Access

### Connect from Host Machine
```bash
psql -h localhost -p 5432 -U steam_user -d steam_insights
# Password: steaminsights2025 (or your DB_PASSWORD)
```

### Connect from Dashboard Container
The dashboard automatically connects using:
```
postgresql://steam_user:password@postgres:5432/steam_insights
```

### Run Database Migrations
```bash
# Execute commands inside the dashboard container
docker-compose exec dashboard python scripts/add_performance_indexes.py
```

## Troubleshooting

### Dashboard Not Starting
1. Check if PostgreSQL is healthy:
```bash
docker-compose logs postgres
```

2. Wait for database initialization (first run takes longer)

3. Check dashboard logs:
```bash
docker-compose logs dashboard
```

### Connection Issues
- Ensure both services are on the same network: `steam-insights-network`
- Verify DATABASE_URL in dashboard environment variables
- Check firewall settings for ports 5432 and 8502

### Port Conflicts
If ports 5432 or 8502 are already in use:
1. Edit `docker-compose.yml`
2. Change the host port (left side of mapping):
```yaml
ports:
  - "8503:8502"  # Map host port 8503 to container port 8502
```

### Reset Everything
```bash
# Stop and remove all containers, networks, and volumes
docker-compose down -v

# Remove any cached images
docker-compose build --no-cache

# Start fresh
docker-compose up -d
```

## Development Mode

The docker-compose.yml includes volume mounts for development:
```yaml
volumes:
  - ./data:/app/data
  - ./src:/app/src  # Live code updates
  - ./config:/app/config
```

Changes to Python files in `src/` will be reflected immediately without rebuilding the container (Streamlit auto-reloads).

## Production Deployment

For production, consider:
1. Remove the source code volume mount from docker-compose.yml
2. Use environment-specific .env files
3. Set up proper secrets management
4. Configure SSL/TLS for secure connections
5. Use a reverse proxy (nginx) for the dashboard
6. Set resource limits for containers

## Health Checks

Both services include health checks:
- **PostgreSQL**: Checks if database accepts connections
- **Dashboard**: Checks Streamlit health endpoint

View health status:
```bash
docker-compose ps
```

## Data Persistence

- **Database**: Data persists in the `postgres_data` named volume
- **Application Data**: Mounted from `./data` directory on host

To backup database:
```bash
docker-compose exec postgres pg_dump -U steam_user steam_insights > backup.sql
```

To restore database:
```bash
cat backup.sql | docker-compose exec -T postgres psql -U steam_user -d steam_insights
```
