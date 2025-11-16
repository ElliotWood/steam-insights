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


@st.cache_data(ttl=3600)
def get_genre_distribution():
    """Cached genre distribution data."""
    db = next(get_db())
    
    results = db.query(
        Genre.name,
        func.count(Game.steam_appid).label('game_count')
    ).join(
        Game.genres
    ).group_by(
        Genre.name
    ).order_by(
        func.count(Game.steam_appid).desc()
    ).limit(15).all()
    
    return [{
        'genre': r.name,
        'game_count': r.game_count
    } for r in results]


def get_session():
    """Get database session."""
    return next(get_db())


def show_overview():
    """Show enhanced home dashboard landing page."""
    # Hero section with welcome message
    st.markdown("""
    <div style='text-align: center; padding: 2rem 0 1rem 0;'>
        <h1 style='font-size: 2.5rem; margin-bottom: 0.5rem;'>🎮 Welcome to Steam Insights</h1>
        <p style='font-size: 1.2rem; color: #888;'>Data-Driven Game Development & Marketing Intelligence Platform</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Quick stats banner
    st.markdown("### 📊 Platform Overview")
    col1, col2, col3, col4 = st.columns(4)
    
    kpis = get_dashboard_kpis()
    
    with col1:
        st.metric("📚 Games Database", f"{kpis['total_games']:,}", help="Total games tracked in our database")
    
    with col2:
        st.metric("🎯 Genre Categories", f"{kpis['total_genres']:,}", help="Unique game genres analyzed")
    
    with col3:
        st.metric("⚡ Recent Updates", f"{kpis['recent_stats']:,}", help="Data updates in last 24 hours")
    
    with col4:
        st.metric("👥 Active Players", f"{kpis['avg_players']:,}", help="Average current players tracked")
    
    st.markdown("---")
    
    # Feature showcase with pill navigation
    st.markdown("### 🚀 What You Can Do with Steam Insights")
    
    # Pill-based navigation tabs
    feature_tab = st.radio(
        "Explore platform features:",
        ["🔍 Overview", "💡 Research Tools", "📊 Analytics Tools", "🎨 Production Tools", "📈 Growth Tools"],
        horizontal=True,
        key="feature_navigation",
        label_visibility="collapsed"
    )
    
    if feature_tab == "🔍 Overview":
        # Platform capabilities overview
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            #### 💡 Concept & Research
            - **Market Opportunities**: Find golden age genres
            - **Genre Analysis**: Deep genre insights  
            - **Google Trends**: Validate game ideas
            - **Rising Trends**: Spot emerging niches
            """)
        
        with col2:
            st.markdown("""
            #### 🎨 Pre-Production & Planning
            - **Revenue Projections**: Estimate potential
            - **Competition Analysis**: Understand rivals
            - **Tag Strategy**: Optimize discoverability
            - **Pricing Strategy**: Find optimal price
            """)
        
        with col3:
            st.markdown("""
            #### 🚀 Launch & Analytics
            - **Demo Impact**: Calculate demo value
            - **Wishlist Benchmarks**: Track momentum
            - **Review Estimator**: Project reviews
            - **Market Position**: Competitive standing
            """)
        
        st.markdown("---")
        st.markdown("### 🎯 Getting Started")
        
        col1, col2 = st.columns(2)
        with col1:
            st.info("""
            **New to Steam Insights?**
            
            1. 📥 Import games via *Data Management*
            2. 🔍 Explore *Market Opportunities*
            3. 📊 Analyze with stage-based tools
            4. 💾 Export insights for your team
            """)
        
        with col2:
            st.success("""
            **Quick Tips:**
            
            - Use the sidebar to navigate by development stage
            - All charts are interactive - hover for details
            - Export data in multiple formats (CSV, Excel, JSON)
            - Track competitors in real-time
            """)
    
    elif feature_tab == "💡 Research Tools":
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 🌟 Market Opportunities")
            st.write("Find emerging genres with high success rates and low competition. Identify golden age opportunities based on Chris Zukowski's methodology.")
            
            st.markdown("#### 📊 Genre Saturation")
            st.write("Analyze competition levels across genres. Lower saturation = easier to stand out in the market.")
        
        with col2:
            st.markdown("#### 🔥 Rising Trends")
            st.write("Spot trending genres and mechanics before they become oversaturated. Early mover advantage.")
            
            st.markdown("#### 🎮 Game Explorer")
            st.write("Deep dive into any Steam game. View player stats, pricing history, reviews, and competitive positioning.")
    
    elif feature_tab == "📊 Analytics Tools":
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### ⚔️ Competition Calculator")
            st.write("Calculate competitive intensity for genre/tag combinations. Understand market crowding.")
            
            st.markdown("#### 📈 Market Position")
            st.write("Analyze player base overlap and addressable market calculations for your game.")
        
        with col2:
            st.markdown("#### 🔍 Post-Mortem Analysis")
            st.write("Advanced analytics with forecasting, correlation analysis, and trend detection.")
            
            st.markdown("#### 📊 Top Charts")
            st.write("Track top performing games across multiple dimensions - players, revenue, reviews.")
    
    elif feature_tab == "🎨 Production Tools":
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 🎨 Steam Page Builder")
            st.write("Design and optimize your Steam store page with AI-powered suggestions and best practices.")
            
            st.markdown("#### 👀 Competitor Tracking")
            st.write("Monitor competitor releases, updates, and performance metrics in real-time.")
        
        with col2:
            st.markdown("#### 🔍 Similar Games")
            st.write("Find games similar to yours for competitive analysis and positioning.")
            
            st.markdown("#### 📈 Genre Trends")
            st.write("Track genre performance over time with detailed trend analysis.")
    
    elif feature_tab == "📈 Growth Tools":
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 🚀 Demo Impact Calculator")
            st.write("Calculate potential impact of releasing a demo based on historical data.")
            
            st.markdown("#### 💎 Benchmark Your Game")
            st.write("Compare your game's wishlists and metrics against similar titles.")
        
        with col2:
            st.markdown("#### 📊 Review Estimator")
            st.write("Estimate expected review counts based on projected sales.")
            
            st.markdown("#### 💰 Revenue Projections")
            st.write("Project potential revenue using multiple methodologies and historical data.")
    
    st.markdown("---")
    
    # Data insights section with tabs
    st.markdown("### 📈 Current Market Insights")
    tab1, tab2, tab3 = st.tabs(["📊 Genre Trends", "🎮 Recent Games", "🔥 Top Performers"])
    
    db = get_session()
    
    with tab1:
        st.markdown("#### 📊 Genre Distribution & Market Overview")
        
        # Check data quality first
        total_games = db.query(func.count(Game.steam_appid)).scalar() or 0
        games_with_genres = db.query(
            func.count(func.distinct(Game.steam_appid))
        ).join(Genre.games).scalar() or 0
        coverage_pct = (
            games_with_genres / total_games * 100
        ) if total_games > 0 else 0
        
        # Summary metrics for genres
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Coverage", f"{coverage_pct:.1f}%", help="Percentage of games with genre data")
        with col2:
            st.metric("Games Analyzed", f"{games_with_genres:,}", help="Games with genre information")
        with col3:
            unique_genres = db.query(func.count(Genre.id)).scalar() or 0
            st.metric("Unique Genres", f"{unique_genres:,}", help="Total distinct genres tracked")
        
        # Show warning if coverage is poor
        if coverage_pct < 50:
            st.warning(
                f"⚠️ **Data Quality Note**: {coverage_pct:.1f}% genre coverage. "
                f"Import more games or run enrichment for complete data."
            )
            
            # Show minimal data anyway, but with clear labeling
            genre_counts = db.query(
                Genre.name,
                func.count(Game.steam_appid).label('count')
            ).join(Genre.games).group_by(Genre.name).order_by(
                func.count(Game.steam_appid).desc()
            ).limit(15).all()
            
            if genre_counts:
                df_genres = pd.DataFrame(
                    genre_counts,
                    columns=['Genre', 'Game Count']
                )
                
                # Create a nice horizontal bar chart
                fig = px.bar(
                    df_genres,
                    x='Game Count',
                    y='Genre',
                    orientation='h',
                    color='Game Count',
                    color_continuous_scale='Viridis',
                    title="Top Genres by Game Count"
                )
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font_color='#ffffff',
                    showlegend=False,
                    height=500,
                    yaxis={'categoryorder': 'total ascending'}
                )
                st.plotly_chart(fig, use_container_width=True)
        else:
            # Normal visualization when data quality is good
            genre_counts = db.query(
                Genre.name,
                func.count(Game.steam_appid).label('count')
            ).join(Genre.games).group_by(Genre.name).order_by(
                func.count(Game.steam_appid).desc()
            ).limit(15).all()
            
            if genre_counts:
                col1, col2 = st.columns([3, 2])
                
                with col1:
                    df_genres = pd.DataFrame(
                        genre_counts,
                        columns=['Genre', 'Game Count']
                    )
                    fig = px.bar(
                        df_genres,
                        x='Game Count',
                        y='Genre',
                        orientation='h',
                        color='Game Count',
                        color_continuous_scale='Viridis',
                        title="Top 15 Genres by Game Count"
                    )
                    fig.update_layout(
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        font_color='#ffffff',
                        showlegend=False,
                        height=500,
                        yaxis={'categoryorder': 'total ascending'}
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    # Show top 10 for pie chart to avoid clutter
                    df_top_genres = df_genres.head(10)
                    fig_pie = px.pie(
                        df_top_genres,
                        values='Game Count',
                        names='Genre',
                        title="Top 10 Genre Share",
                        hole=0.3
                    )
                    fig_pie.update_layout(
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        font_color='#ffffff',
                        height=500
                    )
                    st.plotly_chart(fig_pie, use_container_width=True)
            else:
                st.info(
                    "📥 No genre data available yet. "
                    "Import some games first!"
                )
    
    with tab2:
        st.markdown("#### 🎮 Recently Added to Database")
        
        col1, col2 = st.columns([4, 1])
        with col1:
            st.caption("Latest games imported into the platform")
        with col2:
            limit = st.selectbox(
                "Show:",
                options=[10, 25, 50],
                index=1,
                key="recent_games_limit",
                label_visibility="collapsed"
            )
        
        recent_games = db.query(Game).order_by(
            Game.created_at.desc()
        ).limit(limit).all()
        
        if recent_games:
            games_data = []
            for game in recent_games:
                games_data.append({
                    'Game': game.name,
                    'Developer': game.developer or 'Unknown',
                    'Genres': ', '.join([g.name for g in game.genres[:2]]) if game.genres else 'N/A',
                    'Release Date': game.release_date.strftime('%Y-%m-%d') if game.release_date else 'TBA',
                    'Added to DB': game.created_at.strftime('%Y-%m-%d')
                })
            
            df_recent = pd.DataFrame(games_data)
            st.dataframe(
                df_recent,
                use_container_width=True,
                height=450,
                hide_index=True
            )
            
            # Growth over time chart
            games_by_date = db.query(
                func.date(Game.created_at).label('date'),
                func.count(Game.steam_appid).label('count')
            ).filter(
                Game.created_at >= datetime.now(timezone.utc) - timedelta(days=30)
            ).group_by(
                func.date(Game.created_at)
            ).order_by(
                func.date(Game.created_at)
            ).all()
            
            if games_by_date and len(games_by_date) > 1:
                df_growth = pd.DataFrame([
                    {'Date': str(item.date), 'Games Added': item.count}
                    for item in games_by_date
                ])
                
                fig_growth = px.line(
                    df_growth,
                    x='Date',
                    y='Games Added',
                    title="Games Added (Last 30 Days)",
                    markers=True
                )
                fig_growth.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font_color='#ffffff',
                    height=300
                )
                st.plotly_chart(fig_growth, use_container_width=True)
        else:
            st.info("📥 No games in database yet. Head to Data Management to import games!")
    
    with tab3:
        st.markdown("#### 🔥 Top Performing Games")
        st.caption("Based on player activity in the last 7 days")
        
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
        ).limit(20).all()
        
        if top_games:
            # Create visualization
            df_top_viz = pd.DataFrame([
                {
                    'Game': game.name[:30] + '...' if len(game.name) > 30 else game.name,
                    'Peak Players': int(game.peak_players),
                    'Avg Players': int(game.avg_players)
                }
                for game in top_games[:15]  # Top 15 for chart
            ])
            
            fig_top = px.bar(
                df_top_viz,
                x='Peak Players',
                y='Game',
                orientation='h',
                color='Peak Players',
                color_continuous_scale='Plasma',
                title="Top 15 Games by Peak Players (Last 7 Days)"
            )
            fig_top.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='#ffffff',
                showlegend=False,
                height=500,
                yaxis={'categoryorder': 'total ascending'}
            )
            st.plotly_chart(fig_top, use_container_width=True)
            
            # Table with all data
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
                height=300,
                hide_index=True
            )
        else:
            st.info("📊 No player statistics available yet. Import games and update player stats!")
    
    # Close the database session
    db.close()
    
    # Call to action section
    st.markdown("---")
    st.markdown("### 🚀 Ready to Get Started?")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        #### 📥 Import Data
        Head to **Data Management** to:
        - Import individual games
        - Bulk import from databases
        - Update player statistics
        - Export your analytics
        """)
    
    with col2:
        st.markdown("""
        #### 🔍 Explore Tools
        Choose your development stage:
        - **Concept**: Research opportunities
        - **Pre-Production**: Plan strategy
        - **Production**: Track competitors
        - **Launch**: Monitor performance
        """)
    
    with col3:
        st.markdown("""
        #### 💡 Get Insights
        Use our analytics to:
        - Find market gaps
        - Optimize pricing
        - Track player trends
        - Benchmark performance
        """)
    
    # Footer
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: #666; padding: 1rem 0;'>"
        "Steam Insights Dashboard | Data-Driven Game Development"
        "</div>",
        unsafe_allow_html=True
    )
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
