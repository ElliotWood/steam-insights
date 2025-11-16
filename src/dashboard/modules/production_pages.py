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


@st.cache_data(ttl=3600)
def get_dashboard_kpis():
    """Cached dashboard KPIs."""
    db = next(get_db())
    
    total_games = db.query(Game).count()
    total_genres = db.query(Genre).count()
    recent_stats = db.query(PlayerStats).filter(
        PlayerStats.timestamp >= datetime.now(timezone.utc) - timedelta(hours=24)
    ).count()
    avg_players = db.query(PlayerStats).filter(
        PlayerStats.timestamp >= datetime.now(timezone.utc) - timedelta(hours=1)
    ).with_entities(
        func.avg(PlayerStats.current_players)
    ).scalar()
    
    return {
        'total_games': total_games,
        'total_genres': total_genres,
        'recent_stats': recent_stats,
        'avg_players': int(avg_players or 0)
    }


def get_session():
    """Get database session."""
    return next(get_db())


def show_overview():
    """Show dashboard home page with dense information layout."""
    db = get_session()
    kpis = get_dashboard_kpis()
    
    # Top KPI row - compact metrics
    st.markdown("### 📊 Platform Metrics")
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    
    with col1:
        st.metric("Games", f"{kpis['total_games']:,}")
    with col2:
        st.metric("Genres", f"{kpis['total_genres']:,}")
    with col3:
        st.metric("Updates (24h)", f"{kpis['recent_stats']:,}")
    with col4:
        st.metric("Avg Players", f"{kpis['avg_players']:,}")
    with col5:
        # Additional metric - games added this week
        week_ago = datetime.now(timezone.utc) - timedelta(days=7)
        new_games = db.query(func.count(Game.steam_appid)).filter(
            Game.created_at >= week_ago
        ).scalar() or 0
        st.metric("New (7d)", f"{new_games:,}")
    with col6:
        # Games with player data
        games_with_stats = db.query(func.count(func.distinct(PlayerStats.steam_appid))).scalar() or 0
        st.metric("Tracked", f"{games_with_stats:,}")
    
    st.markdown("---")
    
    # Two column layout for dense information display
    col_left, col_right = st.columns([1, 1])
    
    with col_left:
        # Genre distribution chart
        st.markdown("#### 📊 Top Genres")
        genre_counts = db.query(
            Genre.name,
            func.count(Game.steam_appid).label('count')
        ).join(Genre.games).group_by(Genre.name).order_by(
            func.count(Game.steam_appid).desc()
        ).limit(10).all()
        
        if genre_counts:
            df_genres = pd.DataFrame(genre_counts, columns=['Genre', 'Count'])
            fig = px.bar(
                df_genres,
                x='Count',
                y='Genre',
                orientation='h',
                height=350
            )
            fig.update_layout(
                margin=dict(l=0, r=0, t=0, b=0),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='#ffffff',
                showlegend=False,
                yaxis={'categoryorder': 'total ascending'}
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No genre data available")
    
    with col_right:
        # Top games by players
        st.markdown("#### 🔥 Top Games (7d)")
        top_games = db.query(
            Game.name,
            func.max(PlayerStats.current_players).label('peak')
        ).join(PlayerStats).filter(
            PlayerStats.timestamp >= datetime.now(timezone.utc) - timedelta(days=7)
        ).group_by(Game.name).order_by(
            func.max(PlayerStats.current_players).desc()
        ).limit(10).all()
        
        if top_games:
            df_top = pd.DataFrame([
                {'Game': g.name[:25] + '...' if len(g.name) > 25 else g.name, 
                 'Peak': int(g.peak)}
                for g in top_games
            ])
            fig = px.bar(
                df_top,
                x='Peak',
                y='Game',
                orientation='h',
                height=350
            )
            fig.update_layout(
                margin=dict(l=0, r=0, t=0, b=0),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='#ffffff',
                showlegend=False,
                yaxis={'categoryorder': 'total ascending'}
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No player data available")
    
    # Three column section - more dense widgets
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("#### 📈 Recent Activity")
        # Games added over last 30 days
        games_by_date = db.query(
            func.date(Game.created_at).label('date'),
            func.count(Game.steam_appid).label('count')
        ).filter(
            Game.created_at >= datetime.now(timezone.utc) - timedelta(days=30)
        ).group_by(func.date(Game.created_at)).order_by(
            func.date(Game.created_at)
        ).all()
        
        if games_by_date and len(games_by_date) > 1:
            df_growth = pd.DataFrame([
                {'Date': str(item.date), 'Games': item.count}
                for item in games_by_date
            ])
            fig = px.line(df_growth, x='Date', y='Games', height=200)
            fig.update_layout(
                margin=dict(l=0, r=0, t=0, b=0),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='#ffffff',
                showlegend=False
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No recent activity")
    
    with col2:
        st.markdown("####  🎯 Coverage Stats")
        total = db.query(func.count(Game.steam_appid)).scalar() or 0
        with_genres = db.query(func.count(func.distinct(Game.steam_appid))).join(Genre.games).scalar() or 0
        with_release = db.query(func.count(Game.steam_appid)).filter(Game.release_date.isnot(None)).scalar() or 0
        
        coverage_data = pd.DataFrame([
            {'Category': 'Genres', 'Coverage': (with_genres/total*100 if total > 0 else 0)},
            {'Category': 'Release Date', 'Coverage': (with_release/total*100 if total > 0 else 0)},
            {'Category': 'Player Stats', 'Coverage': (games_with_stats/total*100 if total > 0 else 0)}
        ])
        
        fig = px.bar(coverage_data, x='Category', y='Coverage', height=200)
        fig.update_layout(
            margin=dict(l=0, r=0, t=0, b=0),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='#ffffff',
            showlegend=False,
            yaxis_title="Coverage %"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col3:
        st.markdown("#### 🚀 Quick Actions")
        st.markdown("""
        **Get Started:**
        - 📥 Import Games → Data Management
        - 🔍 Market Research → Concept Stage
        - 📊 View Analytics → Analytics Tools
        - 🎨 Build Steam Page → Production
        
        **Pro Tips:**
        - Stage-based navigation in sidebar
        - Interactive charts (hover for details)
        - Export data in multiple formats
        """)
    
    # Feature pills at bottom - more compact
    st.markdown("---")
    st.markdown("### 🔧 Platform Tools")
    feature_tab = st.radio(
        "Quick tool access:",
        ["🔍 All", "💡 Research", "📊 Analytics", "🎨 Production", "📈 Growth"],
        horizontal=True,
        key="feature_navigation",
        label_visibility="collapsed"
    )
    
    # Compact feature showcase based on selected tab
    if feature_tab == "🔍 All":
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown("**💡 Research**\n- Market Opportunities\n- Genre Analysis\n- Trends")
        with col2:
            st.markdown("**📊 Analytics**\n- Competition Calculator\n- Market Position\n- Post-Mortem")
        with col3:
            st.markdown("**🎨 Production**\n- Steam Page Builder\n- Competitor Tracking\n- Similar Games")
        with col4:
            st.markdown("**📈 Growth**\n- Demo Impact\n- Benchmarks\n- Review Estimator")
    
    elif feature_tab == "💡 Research":
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**🌟 Market Opportunities**\nFind golden age genres with high success rates")
            st.markdown("**📊 Genre Saturation**\nAnalyze competition levels across genres")
        with col2:
            st.markdown("**🔥 Rising Trends**\nSpot trending genres before oversaturation")
            st.markdown("**🎮 Game Explorer**\nDeep dive into any Steam game")
    
    elif feature_tab == "📊 Analytics":
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**⚔️ Competition Calculator**\nCalculate competitive intensity")
            st.markdown("**📈 Market Position**\nPlayer base overlap analysis")
        with col2:
            st.markdown("**🔍 Post-Mortem Analysis**\nForecasting and correlation analysis")
            st.markdown("**📊 Top Charts**\nTrack top performing games")
    
    elif feature_tab == "🎨 Production":
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**🎨 Steam Page Builder**\nDesign optimal store pages")
            st.markdown("**👀 Competitor Tracking**\nMonitor competitor updates")
        with col2:
            st.markdown("**🔍 Similar Games**\nFind similar titles for analysis")
            st.markdown("**📈 Genre Trends**\nTrack genre performance over time")
    
    elif feature_tab == "📈 Growth":
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**🚀 Demo Impact**\nCalculate demo release impact")
            st.markdown("**💎 Benchmark Your Game**\nCompare against similar titles")
        with col2:
            st.markdown("**📊 Review Estimator**\nProject expected review counts")
            st.markdown("**💰 Revenue Projections**\nEstimate potential revenue")
    
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
