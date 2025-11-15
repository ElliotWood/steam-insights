"""
Streamlit dashboard for Steam Insights.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from src.database.connection import get_db, init_db
from src.models.database import Game, Genre, PlayerStats, PricingHistory
from src.api.steam_client import SteamAPIClient
from src.etl.game_importer import GameDataImporter

# Page configuration
st.set_page_config(
    page_title="Steam Insights Dashboard",
    page_icon="🎮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize database
init_db()


def get_session():
    """Get database session."""
    return next(get_db())


def main():
    """Main dashboard function."""
    st.title("🎮 Steam Insights Dashboard")
    st.markdown("---")
    
    # Sidebar
    with st.sidebar:
        st.header("Navigation")
        page = st.radio(
            "Select a page:",
            ["Overview", "Game Search", "Analytics", "Data Management"]
        )
        
        st.markdown("---")
        st.markdown("### About")
        st.info(
            "Steam Insights provides analytics and insights "
            "for Steam games, including player counts, pricing history, "
            "and genre analysis."
        )
    
    # Route to different pages
    if page == "Overview":
        show_overview()
    elif page == "Game Search":
        show_game_search()
    elif page == "Analytics":
        show_analytics()
    elif page == "Data Management":
        show_data_management()


def show_overview():
    """Show overview page with key statistics."""
    st.header("Overview")
    
    db = get_session()
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_games = db.query(Game).count()
        st.metric("Total Games", f"{total_games:,}")
    
    with col2:
        total_genres = db.query(Genre).count()
        st.metric("Genres", f"{total_genres:,}")
    
    with col3:
        recent_stats = db.query(PlayerStats).filter(
            PlayerStats.timestamp >= datetime.utcnow() - timedelta(hours=24)
        ).count()
        st.metric("Recent Updates (24h)", f"{recent_stats:,}")
    
    with col4:
        avg_players = db.query(PlayerStats).filter(
            PlayerStats.timestamp >= datetime.utcnow() - timedelta(hours=1)
        ).with_entities(
            db.func.avg(PlayerStats.current_players)
        ).scalar()
        st.metric("Avg Current Players", f"{int(avg_players or 0):,}")
    
    st.markdown("---")
    
    # Top genres
    st.subheader("Top Genres by Game Count")
    
    genre_counts = db.query(
        Genre.name,
        db.func.count(Game.id).label('count')
    ).join(Genre.games).group_by(Genre.name).order_by(
        db.func.count(Game.id).desc()
    ).limit(10).all()
    
    if genre_counts:
        df_genres = pd.DataFrame(genre_counts, columns=['Genre', 'Game Count'])
        fig = px.bar(df_genres, x='Genre', y='Game Count', color='Game Count')
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No genre data available yet. Import some games first!")
    
    # Recently added games
    st.subheader("Recently Added Games")
    
    recent_games = db.query(Game).order_by(
        Game.created_at.desc()
    ).limit(10).all()
    
    if recent_games:
        games_data = []
        for game in recent_games:
            games_data.append({
                'Name': game.name,
                'Developer': game.developer or 'Unknown',
                'Release Date': game.release_date.strftime('%Y-%m-%d') if game.release_date else 'N/A',
                'Added': game.created_at.strftime('%Y-%m-%d %H:%M')
            })
        
        df_recent = pd.DataFrame(games_data)
        st.dataframe(df_recent, use_container_width=True)
    else:
        st.info("No games in database yet. Import some games to get started!")
    
    db.close()


def show_game_search():
    """Show game search and details page."""
    st.header("Game Search")
    
    db = get_session()
    
    # Search input
    search_term = st.text_input("Search for a game:", placeholder="Enter game name...")
    
    if search_term:
        games = db.query(Game).filter(
            Game.name.ilike(f"%{search_term}%")
        ).limit(20).all()
        
        if games:
            st.write(f"Found {len(games)} game(s)")
            
            # Display games
            for game in games:
                with st.expander(f"🎮 {game.name}"):
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.write(f"**Developer:** {game.developer or 'Unknown'}")
                        st.write(f"**Publisher:** {game.publisher or 'Unknown'}")
                        st.write(f"**Release Date:** {game.release_date.strftime('%Y-%m-%d') if game.release_date else 'N/A'}")
                        st.write(f"**Steam App ID:** {game.steam_appid}")
                        
                        if game.short_description:
                            st.write("**Description:**")
                            st.write(game.short_description)
                        
                        if game.genres:
                            genres = [g.name for g in game.genres]
                            st.write(f"**Genres:** {', '.join(genres)}")
                    
                    with col2:
                        if game.header_image:
                            st.image(game.header_image)
                        
                        # Platform badges
                        platforms = []
                        if game.windows:
                            platforms.append("🪟 Windows")
                        if game.mac:
                            platforms.append("🍎 Mac")
                        if game.linux:
                            platforms.append("🐧 Linux")
                        
                        if platforms:
                            st.write("**Platforms:**")
                            for platform in platforms:
                                st.write(platform)
                    
                    # Player stats chart
                    stats = db.query(PlayerStats).filter(
                        PlayerStats.game_id == game.id,
                        PlayerStats.timestamp >= datetime.utcnow() - timedelta(days=30)
                    ).order_by(PlayerStats.timestamp).all()
                    
                    if stats:
                        st.write("**Player Count (Last 30 Days)**")
                        df_stats = pd.DataFrame([
                            {'Date': s.timestamp, 'Players': s.current_players}
                            for s in stats
                        ])
                        fig = px.line(df_stats, x='Date', y='Players')
                        st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning(f"No games found matching '{search_term}'")
    
    db.close()


def show_analytics():
    """Show analytics page with charts and insights."""
    st.header("Analytics")
    
    db = get_session()
    
    # Time range selector
    time_range = st.selectbox(
        "Select time range:",
        ["Last 24 Hours", "Last 7 Days", "Last 30 Days", "Last 90 Days"]
    )
    
    days_map = {
        "Last 24 Hours": 1,
        "Last 7 Days": 7,
        "Last 30 Days": 30,
        "Last 90 Days": 90
    }
    days = days_map[time_range]
    
    since = datetime.utcnow() - timedelta(days=days)
    
    # Most active games
    st.subheader("Most Active Games")
    
    active_games = db.query(
        Game.name,
        db.func.max(PlayerStats.current_players).label('max_players'),
        db.func.avg(PlayerStats.current_players).label('avg_players')
    ).join(PlayerStats).filter(
        PlayerStats.timestamp >= since
    ).group_by(Game.name).order_by(
        db.func.max(PlayerStats.current_players).desc()
    ).limit(15).all()
    
    if active_games:
        df_active = pd.DataFrame(
            active_games,
            columns=['Game', 'Peak Players', 'Avg Players']
        )
        df_active['Peak Players'] = df_active['Peak Players'].astype(int)
        df_active['Avg Players'] = df_active['Avg Players'].astype(int)
        
        fig = px.bar(
            df_active,
            x='Game',
            y=['Peak Players', 'Avg Players'],
            barmode='group',
            title=f"Top 15 Games by Player Count ({time_range})"
        )
        fig.update_xaxis(tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No player statistics available for the selected time range.")
    
    db.close()


def show_data_management():
    """Show data management page for importing games."""
    st.header("Data Management")
    
    st.write("Import games from Steam to populate the database.")
    
    # Import single game
    st.subheader("Import Single Game")
    
    app_id = st.number_input(
        "Enter Steam App ID:",
        min_value=1,
        step=1,
        help="You can find the App ID in the Steam store URL"
    )
    
    if st.button("Import Game"):
        with st.spinner(f"Importing game {app_id}..."):
            db = get_session()
            importer = GameDataImporter(db)
            
            try:
                game = importer.import_game(app_id)
                if game:
                    st.success(f"✅ Successfully imported: {game.name}")
                    
                    # Also try to import player stats
                    stats = importer.update_player_stats(app_id)
                    if stats:
                        st.info(f"Current players: {stats.current_players}")
                else:
                    st.error("Failed to import game. Check the App ID and try again.")
            except Exception as e:
                st.error(f"Error: {str(e)}")
            finally:
                db.close()
    
    st.markdown("---")
    
    # Popular game suggestions
    st.subheader("Popular Games to Import")
    st.write("Try importing these popular games:")
    
    popular_games = [
        ("Counter-Strike 2", 730),
        ("Dota 2", 570),
        ("Team Fortress 2", 440),
        ("Rust", 252490),
        ("Apex Legends", 1172470),
        ("Grand Theft Auto V", 271590),
    ]
    
    cols = st.columns(3)
    for idx, (name, appid) in enumerate(popular_games):
        with cols[idx % 3]:
            if st.button(f"Import {name}", key=f"popular_{appid}"):
                with st.spinner(f"Importing {name}..."):
                    db = get_session()
                    importer = GameDataImporter(db)
                    
                    try:
                        game = importer.import_game(appid)
                        if game:
                            st.success(f"✅ Imported: {game.name}")
                        else:
                            st.error("Failed to import game")
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
                    finally:
                        db.close()


if __name__ == "__main__":
    main()
