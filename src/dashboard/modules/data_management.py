"""
Data Management pages: Top Charts, Market Analytics, LLM Data Mining.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta, timezone
from sqlalchemy import func
import json

from src.database.connection import get_db
from src.models.database import (
    Game, Genre, PlayerStats, Review, game_genres,
    GameEnrichment, BatchProcessingJob
)
from src.utils.llm_enrichment import create_default_extractor
from src.utils.batch_processor import BatchProcessor


def get_session():
    """Get database session."""
    return next(get_db())


def show_top_charts():
    """Top charts showing trending games by various metrics."""
    st.header("📊 Top Charts")
    st.markdown("*Trending games by followers, wishlist growth, and player activity*")
    
    db = get_session()
    
    # Time period selector
    period = st.selectbox(
        "Time Period",
        ["Last Week", "Last Month", "Last 3 Months", "Last Year"],
        key="top_charts_period"
    )
    
    days_map = {
        "Last Week": 7,
        "Last Month": 30,
        "Last 3 Months": 90,
        "Last Year": 365
    }
    days = days_map[period]
    cutoff_date = datetime.now() - timedelta(days=days)
    
    tab1, tab2, tab3 = st.tabs([
        "📈 New Followers/Wishlists",
        "👥 Player Growth",
        "💰 Revenue Leaders"
    ])
    
    with tab1:
        st.subheader(f"Top Games by Followers/Owners - {period}")
        st.info("Games with highest estimated ownership")
        
        # Get latest stats for each game within period
        latest_stats = db.query(
            PlayerStats.game_id,
            func.max(PlayerStats.timestamp).label('latest_time')
        ).filter(
            PlayerStats.timestamp >= cutoff_date
        ).group_by(PlayerStats.game_id).subquery()
        
        results = db.query(
            Game.name,
            Game.developer,
            PlayerStats.estimated_owners,
            PlayerStats.current_players
        ).join(
            PlayerStats
        ).join(
            latest_stats,
            (PlayerStats.game_id == latest_stats.c.game_id) &
            (PlayerStats.timestamp == latest_stats.c.latest_time)
        ).filter(
            PlayerStats.estimated_owners.isnot(None)
        ).order_by(
            PlayerStats.estimated_owners.desc()
        ).limit(20).all()
        
        if results:
            df = pd.DataFrame(results, columns=[
                'Game', 'Developer', 'Est. Owners', 'Current Players'
            ])
            df['Est. Owners'] = df['Est. Owners'].apply(
                lambda x: f"{x:,}" if pd.notna(x) else "N/A"
            )
            df['Current Players'] = df['Current Players'].apply(
                lambda x: f"{x:,}" if pd.notna(x) else "N/A"
            )
            
            # Visualization
            plot_df = pd.DataFrame(results, columns=[
                'Game', 'Developer', 'Est. Owners', 'Current Players'
            ])
            fig = px.bar(
                plot_df.head(10),
                x='Est. Owners',
                y='Game',
                orientation='h',
                title=f'Top 10 Games by Owners ({period})',
                labels={'Est. Owners': 'Estimated Owners'}
            )
            st.plotly_chart(fig, use_container_width=True)
            
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.warning("No data available for this period")
    
    with tab2:
        st.subheader(f"Player Activity Leaders - {period}")
        st.info("Games with the highest concurrent player counts")
        
        # Get latest player stats
        latest_stats = db.query(
            PlayerStats.game_id,
            func.max(PlayerStats.timestamp).label('latest_time')
        ).filter(
            PlayerStats.timestamp >= cutoff_date
        ).group_by(PlayerStats.game_id).subquery()
        
        results = db.query(
            Game.name,
            Game.developer,
            PlayerStats.current_players,
            PlayerStats.peak_players_24h,
            PlayerStats.estimated_owners
        ).join(
            PlayerStats
        ).join(
            latest_stats,
            (PlayerStats.game_id == latest_stats.c.game_id) &
            (PlayerStats.timestamp == latest_stats.c.latest_time)
        ).filter(
            PlayerStats.peak_players_24h.isnot(None)
        ).order_by(
            PlayerStats.peak_players_24h.desc()
        ).limit(20).all()
        
        if results:
            df = pd.DataFrame(results, columns=[
                'Game', 'Developer', 'Current Players',
                'Peak 24h', 'Est. Owners'
            ])
            df['Current Players'] = df['Current Players'].apply(
                lambda x: f"{x:,}" if pd.notna(x) else "N/A"
            )
            df['Peak 24h'] = df['Peak 24h'].apply(
                lambda x: f"{x:,}" if pd.notna(x) else "N/A"
            )
            df['Est. Owners'] = df['Est. Owners'].apply(
                lambda x: f"{x:,}" if pd.notna(x) else "N/A"
            )
            
            # Visualization
            plot_df = pd.DataFrame(results, columns=[
                'Game', 'Developer', 'Current Players',
                'Peak 24h', 'Est. Owners'
            ])
            fig = px.bar(
                plot_df.head(10),
                x='Peak 24h',
                y='Game',
                orientation='h',
                title=f'Top 10 by Peak Players ({period})',
                labels={'Peak 24h': 'Peak Players (24h)'}
            )
            st.plotly_chart(fig, use_container_width=True)
            
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.warning("No player data available")
    
    with tab3:
        st.subheader(f"Revenue Leaders - {period}")
        st.info("Top earning games by estimated revenue")
        
        # Get latest revenue data
        latest_stats = db.query(
            PlayerStats.game_id,
            func.max(PlayerStats.timestamp).label('latest_time')
        ).filter(
            PlayerStats.timestamp >= cutoff_date
        ).group_by(PlayerStats.game_id).subquery()
        
        results = db.query(
            Game.name,
            Game.developer,
            PlayerStats.estimated_revenue,
            PlayerStats.estimated_owners
        ).join(
            PlayerStats
        ).join(
            latest_stats,
            (PlayerStats.game_id == latest_stats.c.game_id) &
            (PlayerStats.timestamp == latest_stats.c.latest_time)
        ).filter(
            PlayerStats.estimated_revenue.isnot(None)
        ).order_by(
            PlayerStats.estimated_revenue.desc()
        ).limit(20).all()
        
        if results:
            df = pd.DataFrame(results, columns=[
                'Game', 'Developer', 'Est. Revenue', 'Est. Owners'
            ])
            
            # Visualization
            fig = px.bar(
                df.head(10),
                x='Est. Revenue',
                y='Game',
                orientation='h',
                title=f'Top 10 by Revenue ({period})',
                labels={'Est. Revenue': 'Estimated Revenue ($)'}
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Format for display
            df['Est. Revenue'] = df['Est. Revenue'].apply(
                lambda x: f"${x:,.0f}" if pd.notna(x) else "N/A"
            )
            df['Est. Owners'] = df['Est. Owners'].apply(
                lambda x: f"{x:,}" if pd.notna(x) else "N/A"
            )
            
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.warning("No revenue data available")


def show_market_analytics():
    """Market-wide analytics similar to Video Game Insights."""
    st.header("🔍 Steam Market Analytics")
    st.markdown("*Overview of Steam market size and trends*")
    
    db = get_session()
    
    tab1, tab2, tab3 = st.tabs([
        "📊 Market Size",
        "👥 User Engagement",
        "🎮 Genre Supply/Demand"
    ])
    
    with tab1:
        st.subheader("Steam Market Size")
        
        # Total games
        total_games = db.query(Game).count()
        
        # Games by year
        from sqlalchemy import extract
        
        games_by_year = db.query(
            extract('year', Game.release_date).label('year'),
            func.count(Game.id).label('count')
        ).filter(
            Game.release_date.isnot(None)
        ).group_by('year').order_by('year').all()
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Games on Steam", f"{total_games:,}")
        
        if games_by_year:
            df = pd.DataFrame(games_by_year, columns=['Year', 'Games Released'])
            df = df[df['Year'] >= 2010]  # Filter recent years
            
            fig = px.bar(
                df,
                x='Year',
                y='Games Released',
                title='Games Released per Year'
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        st.subheader("Steam User Engagement")
        st.info("Total concurrent players across all tracked games")
        
        # Get total concurrent players over time (sum across all games)
        daily_totals = db.query(
            func.date(PlayerStats.timestamp).label('date'),
            func.sum(PlayerStats.current_players).label('total_players')
        ).filter(
            PlayerStats.current_players.isnot(None)
        ).group_by('date').order_by('date').limit(90).all()
        
        if daily_totals:
            df = pd.DataFrame(
                daily_totals, columns=['Date', 'Total Players']
            )
            
            # Summary metrics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric(
                    "Latest Total",
                    f"{df['Total Players'].iloc[-1]:,.0f}"
                )
            with col2:
                st.metric("Average", f"{df['Total Players'].mean():,.0f}")
            with col3:
                st.metric("Peak", f"{df['Total Players'].max():,.0f}")
            
            # Line chart
            fig = px.line(
                df,
                x='Date',
                y='Total Players',
                title='Daily Total Concurrent Players (Last 90 Days)'
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Top games by current players
            st.markdown("**Top Games by Current Players:**")
            top_current = db.query(
                Game.name,
                PlayerStats.current_players
            ).join(
                PlayerStats
            ).filter(
                PlayerStats.current_players.isnot(None)
            ).order_by(
                PlayerStats.current_players.desc()
            ).limit(10).all()
            
            if top_current:
                top_df = pd.DataFrame(
                    top_current, columns=['Game', 'Current Players']
                )
                top_df['Current Players'] = top_df['Current Players'].apply(
                    lambda x: f"{x:,}"
                )
                st.dataframe(
                    top_df, use_container_width=True, hide_index=True
                )
        else:
            st.warning("No player data available")
    
    with tab3:
        st.subheader("Genre Supply & Demand")
        st.info("Which genres are oversupplied vs. high demand")
        
        # Get genre stats
        genre_stats = db.query(
            Genre.name,
            func.count(Game.id).label('supply'),
            func.avg(PlayerStats.estimated_owners).label('avg_demand')
        ).join(
            game_genres, Genre.id == game_genres.c.genre_id
        ).join(
            Game, Game.id == game_genres.c.game_id
        ).join(
            PlayerStats
        ).filter(
            PlayerStats.estimated_owners.isnot(None)
        ).group_by(Genre.name).all()
        
        if genre_stats:
            df = pd.DataFrame(genre_stats, columns=[
                'Genre', 'Supply (Games)', 'Avg Demand (Owners)'
            ])
            df['Avg Demand (Owners)'] = df['Avg Demand (Owners)'].fillna(
                0
            ).astype(int)
            
            fig = px.scatter(
                df,
                x='Supply (Games)',
                y='Avg Demand (Owners)',
                size='Avg Demand (Owners)',
                hover_data=['Genre'],
                title='Genre Supply vs Demand',
                labels={
                    'Supply (Games)': 'Number of Games (Supply)',
                    'Avg Demand (Owners)': 'Average Owners (Demand)'
                }
            )
            st.plotly_chart(fig, use_container_width=True)
            
            st.dataframe(
                df.sort_values('Avg Demand (Owners)', ascending=False),
                use_container_width=True,
                hide_index=True
            )


def show_llm_mining():
    """LLM-powered batch data enrichment for game database."""
    st.header("🤖 LLM Data Mining")
    st.markdown(
        "*Automatically enrich game data with AI-extracted insights*"
    )
    
    st.info(
        "This tool uses Language Models to analyze game descriptions "
        "and extract:\n"
        "- **Game mechanics** (gameplay systems)\n"
        "- **Themes** (narrative and artistic themes)\n"
        "- **Features** (technical features and functionality)\n"
        "- **Player sentiment** (from reviews)"
    )
    
    db = get_session()
    
    # Get statistics
    total_games = db.query(Game).count()
    enriched_games = db.query(GameEnrichment).filter(
        GameEnrichment.error_message.is_(None)
    ).count()
    failed_games = db.query(GameEnrichment).filter(
        GameEnrichment.error_message.isnot(None)
    ).count()
    
    # Display stats
    st.markdown("### 📊 Database Status")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Games", f"{total_games:,}")
    with col2:
        st.metric("Enriched", f"{enriched_games:,}")
    with col3:
        st.metric("Pending", f"{total_games - enriched_games - failed_games:,}")
    with col4:
        completion = (enriched_games / total_games * 100) if total_games > 0 else 0
        st.metric("Progress", f"{completion:.1f}%")
    
    # Progress bar
    st.progress(completion / 100)
    
    st.markdown("---")
    
    # Check for active job
    extractor = create_default_extractor()
    processor = BatchProcessor(db, extractor)
    active_job = processor.get_active_job()
    latest_job = processor.get_latest_job()
    
    if active_job:
        st.markdown("### 🔄 Active Batch Job")
        
        # Job status
        status_color = {
            'running': '🟢',
            'paused': '🟡',
            'pending': '🔵'
        }
        st.markdown(
            f"**Status:** {status_color.get(active_job.status, '⚪')} "
            f"{active_job.status.upper()}"
        )
        
        # Progress
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(
                "Processed",
                f"{active_job.processed_items}/{active_job.total_items}"
            )
        with col2:
            st.metric("Failed", active_job.failed_items)
        with col3:
            st.metric("Progress", f"{active_job.progress_percentage:.1f}%")
        
        # Progress bar
        st.progress(active_job.progress_percentage / 100)
        
        # ETA
        if active_job.estimated_completion and active_job.status == 'running':
            eta = active_job.estimated_completion - datetime.now(timezone.utc)
            st.info(f"⏱️ Estimated completion: {eta.seconds // 60} minutes")
        
        # Control buttons
        col1, col2, col3 = st.columns(3)
        with col1:
            if active_job.status == 'running':
                if st.button("⏸️ Pause Job", type="secondary"):
                    processor.pause_job(active_job.id)
                    st.rerun()
            elif active_job.status == 'paused':
                if st.button("▶️ Resume Job", type="primary"):
                    processor.resume_job(active_job.id)
                    st.rerun()
        
        with col2:
            if st.button("🛑 Cancel Job", type="secondary"):
                processor.cancel_job(active_job.id)
                st.rerun()
        
        # Error log
        if active_job.error_log:
            with st.expander("View Errors"):
                try:
                    errors = json.loads(active_job.error_log)
                    if errors:
                        st.dataframe(
                            pd.DataFrame(errors),
                            use_container_width=True
                        )
                    else:
                        st.success("No errors yet!")
                except:
                    st.text(active_job.error_log)
    
    else:
        st.markdown("### 🚀 Start Batch Processing")
        
        # Configuration
        col1, col2 = st.columns(2)
        
        with col1:
            batch_size = st.number_input(
                "Number of games to process",
                min_value=10,
                max_value=1000,
                value=100,
                step=10,
                help="How many games to enrich in this batch"
            )
        
        with col2:
            st.markdown("**Processing Options:**")
            skip_processed = st.checkbox(
                "Skip already enriched games",
                value=True,
                help="Only process games without enrichment data"
            )
        
        # LLM Configuration (future enhancement)
        with st.expander("⚙️ LLM Configuration (Coming Soon)"):
            st.info(
                "**Future Features:**\n"
                "- Choose LLM provider (OpenAI, Anthropic, Local)\n"
                "- Configure model (GPT-4, Claude, Llama, etc.)\n"
                "- Set API keys and rate limits\n"
                "- Customize extraction prompts\n\n"
                "Currently using mock implementation for testing."
            )
        
        # Start button
        if st.button("🚀 Start Batch Processing", type="primary"):
            # Get games to process
            games_to_process = processor.get_games_to_process(
                limit=batch_size,
                exclude_processed=skip_processed
            )
            
            if not games_to_process:
                st.warning(
                    "No games to process! All games may already be enriched."
                )
            else:
                # Create job
                config = {
                    'batch_size': batch_size,
                    'skip_processed': skip_processed
                }
                job = processor.create_job(
                    total_items=len(games_to_process),
                    config=config
                )
                
                st.success(
                    f"Created batch job #{job.id} for "
                    f"{len(games_to_process)} games"
                )
                st.info(
                    "⚠️ **Note:** Actual LLM processing is not yet "
                    "implemented. This creates a job structure for "
                    "testing. To enable real processing:\n"
                    "1. Configure an LLM provider in "
                    "`src/utils/llm_enrichment.py`\n"
                    "2. Add API keys to environment variables\n"
                    "3. Implement the API call methods"
                )
                
                # Run job in background (would need threading/celery for real)
                with st.spinner("Processing batch..."):
                    try:
                        processor.run_batch_job(job)
                        st.rerun()
                    except Exception as e:
                        st.error(f"Batch processing failed: {e}")
    
    # Job history
    st.markdown("---")
    st.markdown("### 📜 Recent Jobs")
    
    recent_jobs = db.query(BatchProcessingJob).order_by(
        BatchProcessingJob.created_at.desc()
    ).limit(5).all()
    
    if recent_jobs:
        jobs_data = []
        for job in recent_jobs:
            duration = None
            if job.completed_at and job.started_at:
                duration = (job.completed_at - job.started_at).seconds / 60
            
            jobs_data.append({
                'ID': job.id,
                'Status': job.status,
                'Total': job.total_items,
                'Processed': job.processed_items,
                'Failed': job.failed_items,
                'Progress': f"{job.progress_percentage:.1f}%",
                'Duration (min)': f"{duration:.1f}" if duration else "-",
                'Created': job.created_at.strftime('%Y-%m-%d %H:%M')
            })
        
        st.dataframe(
            pd.DataFrame(jobs_data),
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("No batch jobs yet. Start one above!")
    
    # Sample enriched data
    if enriched_games > 0:
        st.markdown("---")
        st.markdown("### 🔍 Sample Enriched Data")
        
        sample = db.query(
            Game, GameEnrichment
        ).join(
            GameEnrichment,
            Game.id == GameEnrichment.game_id
        ).filter(
            GameEnrichment.error_message.is_(None)
        ).limit(5).all()
        
        if sample:
            for game, enrichment in sample:
                with st.expander(f"🎮 {game.name}"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("**Mechanics:**")
                        try:
                            mechanics = json.loads(enrichment.mechanics)
                            for m in mechanics:
                                st.write(f"• {m}")
                        except:
                            st.write(enrichment.mechanics)
                        
                        st.markdown("**Themes:**")
                        try:
                            themes = json.loads(enrichment.themes)
                            for t in themes:
                                st.write(f"• {t}")
                        except:
                            st.write(enrichment.themes)
                    
                    with col2:
                        st.markdown("**Features:**")
                        try:
                            features = json.loads(enrichment.features)
                            for f in features:
                                st.write(f"• {f}")
                        except:
                            st.write(enrichment.features)
                        
                        if enrichment.sentiment_score is not None:
                            st.metric(
                                "Sentiment",
                                f"{enrichment.sentiment_score:.2f}"
                            )
                        
                        st.caption(
                            f"Processed: {enrichment.processed_at.strftime('%Y-%m-%d')}"
                        )
