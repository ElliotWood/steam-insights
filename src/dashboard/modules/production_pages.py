"""
Production & Launch stage pages for Steam Insights Dashboard.
Contains overview, game performance tracking, and market position analysis.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta, timezone
from sqlalchemy import func

from src.database.connection import get_db
from src.models.database import Game, Genre, PlayerStats


def get_session():
    """Get database session."""
    return next(get_db())


def show_overview():
    """Show overview page with key statistics."""
    st.header("📊 Dashboard Overview")
    
    db = get_session()
    
    # Key metrics row with enhanced styling
    st.markdown("### 🎯 Key Performance Indicators")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_games = db.query(Game).count()
        st.metric("Total Games", f"{total_games:,}", delta=None, help="Total games in database")
    
    with col2:
        total_genres = db.query(Genre).count()
        st.metric("Genres", f"{total_genres:,}", help="Unique genres tracked")
    
    with col3:
        recent_stats = db.query(PlayerStats).filter(
            PlayerStats.timestamp >= datetime.now(timezone.utc) - timedelta(hours=24)
        ).count()
        st.metric("Recent Updates (24h)", f"{recent_stats:,}", help="Stats updates in last 24h")
    
    with col4:
        avg_players = db.query(PlayerStats).filter(
            PlayerStats.timestamp >= datetime.now(timezone.utc) - timedelta(hours=1)
        ).with_entities(
            func.avg(PlayerStats.current_players)
        ).scalar()
        st.metric("Avg Current Players", f"{int(avg_players or 0):,}", help="Average players across all games")
    
    st.markdown("---")
    
    # Tabbed interface for different analytics views
    tab1, tab2, tab3 = st.tabs(["📈 Genre Distribution", "🎮 Recent Activity", "🔥 Top Performing"])
    
    with tab1:
        st.markdown("#### Genre Distribution Analysis")
        
        genre_counts = db.query(
            Genre.name,
            func.count(Game.id).label('count')
        ).join(Genre.games).group_by(Genre.name).order_by(
            func.count(Game.id).desc()
        ).limit(10).all()
        
        if genre_counts:
            col1, col2 = st.columns([2, 1])
            
            with col1:
                # Bar chart
                df_genres = pd.DataFrame(genre_counts, columns=['Genre', 'Game Count'])
                fig = px.bar(
                    df_genres, 
                    x='Genre', 
                    y='Game Count',
                    color='Game Count',
                    color_continuous_scale='Blues',
                    title="Top 10 Genres by Game Count"
                )
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font_color='#ffffff',
                    showlegend=False,
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Pie chart
                fig_pie = px.pie(
                    df_genres,
                    values='Game Count',
                    names='Genre',
                    title="Genre Distribution"
                )
                fig_pie.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font_color='#ffffff',
                    height=400
                )
                st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("📥 No genre data available yet. Import some games first!")
    
    with tab2:
        st.markdown("#### Recently Added Games")
        
        recent_games = db.query(Game).order_by(
            Game.created_at.desc()
        ).limit(15).all()
        
        if recent_games:
            games_data = []
            for game in recent_games:
                games_data.append({
                    'Name': game.name,
                    'Developer': game.developer or 'Unknown',
                    'Genres': ', '.join([g.name for g in game.genres[:2]]) if game.genres else 'N/A',
                    'Release Date': game.release_date.strftime('%Y-%m-%d') if game.release_date else 'N/A',
                    'Added': game.created_at.strftime('%Y-%m-%d %H:%M')
                })
            
            df_recent = pd.DataFrame(games_data)
            st.dataframe(
                df_recent,
                use_container_width=True,
                height=400,
                hide_index=True
            )
        else:
            st.info("📥 No games in database yet. Import some games to get started!")
    
    with tab3:
        st.markdown("#### Top Performing Games (by Player Count)")
        
        # Get games with recent player stats
        top_games = db.query(
            Game.name,
            Game.developer,
            func.max(PlayerStats.current_players).label('peak_players'),
            func.avg(PlayerStats.current_players).label('avg_players')
        ).join(PlayerStats).filter(
            PlayerStats.timestamp >= datetime.now(timezone.utc) - timedelta(days=7)
        ).group_by(Game.name, Game.developer).order_by(
            func.max(PlayerStats.current_players).desc()
        ).limit(10).all()
        
        if top_games:
            df_top = pd.DataFrame([
                {
                    'Rank': idx + 1,
                    'Game': game.name,
                    'Developer': game.developer or 'Unknown',
                    'Peak Players': f"{int(game.peak_players):,}",
                    'Avg Players': f"{int(game.avg_players):,}"
                }
                for idx, game in enumerate(top_games)
            ])
            
            st.dataframe(
                df_top,
                use_container_width=True,
                height=400,
                hide_index=True
            )
        else:
            st.info("📊 No player statistics available yet. Import games and update player stats!")
    
    db.close()


def show_game_performance():
    """Individual game performance tracking."""
    st.header("🎮 Game Performance Tracker")
    st.markdown("*Track a specific game's metrics over time*")
    
    # Import the function from postlaunch_pages
    from src.dashboard.modules.postlaunch_pages import show_game_search
    show_game_search()


def show_market_position():
    """Market positioning and overlap analysis."""
    st.header("📈 Market Position Analysis")
    st.markdown("*Understand your position in the market*")
    
    # Import the function from postlaunch_pages
    from src.dashboard.modules.postlaunch_pages import show_market_analysis
    show_market_analysis()
