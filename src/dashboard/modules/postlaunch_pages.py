"""
Post-launch and analytics pages for Steam Insights Dashboard.
Contains game search, analytics, market analysis, and data management.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta, timezone
from sqlalchemy import func

from src.database.connection import get_db
from src.models.database import Game, Genre, PlayerStats
from src.api.steam_client import SteamAPIClient
from src.etl.game_importer import GameDataImporter


def get_session():
    """Get database session."""
    return next(get_db())


def show_game_search():
    """Show game explorer board with browsable games and optional search."""
    st.header("🎮 Game Explorer")
    st.markdown("*Browse and discover games in the database*")
    
    db = get_session()
    
    # Get total count and available genres
    total_games = db.query(Game).count()
    all_genres = db.query(Genre).order_by(Genre.name).all()
    genre_names = [g.name for g in all_genres]
    
    # Filters in sidebar/expander
    with st.expander("🔍 Filter & Search Options", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            search_term = st.text_input(
                "Search by name:",
                placeholder="Enter game name (optional)...",
                key="game_explorer_search"
            )
            
            genre_filter = st.multiselect(
                "Filter by genre:",
                options=genre_names,
                key="game_explorer_genre"
            )
        
        with col2:
            platform_filter = st.multiselect(
                "Filter by platform:",
                options=["Windows", "Mac", "Linux"],
                key="game_explorer_platform"
            )
            
            sort_by = st.selectbox(
                "Sort by:",
                options=[
                    "Most Popular (Owners)",
                    "Recently Released",
                    "Name (A-Z)",
                    "Name (Z-A)"
                ],
                key="game_explorer_sort"
            )
    
    # Build query with filters
    query = db.query(Game).join(PlayerStats)
    
    if search_term:
        query = query.filter(Game.name.ilike(f"%{search_term}%"))
    
    if genre_filter:
        query = query.join(Game.genres).filter(Genre.name.in_(genre_filter))
    
    if platform_filter:
        for platform in platform_filter:
            if platform == "Windows":
                query = query.filter(Game.windows == True)
            elif platform == "Mac":
                query = query.filter(Game.mac == True)
            elif platform == "Linux":
                query = query.filter(Game.linux == True)
    
    # Apply sorting
    if sort_by == "Most Popular (Owners)":
        query = query.order_by(PlayerStats.estimated_owners.desc())
    elif sort_by == "Recently Released":
        query = query.order_by(Game.release_date.desc())
    elif sort_by == "Name (A-Z)":
        query = query.order_by(Game.name.asc())
    elif sort_by == "Name (Z-A)":
        query = query.order_by(Game.name.desc())
    
    # Pagination controls
    col1, col2 = st.columns([1, 3])
    with col1:
        items_per_page = st.selectbox(
            "Games per page",
            options=[50, 100, 200, 500],
            index=0,
            key="game_browser_page_size"
        )
    
    # Get total count for pagination
    total_matching = query.count()
    total_pages = (total_matching + items_per_page - 1) // items_per_page
    
    with col2:
        if total_pages > 1:
            page_number = st.number_input(
                f"Page (1-{total_pages})",
                min_value=1,
                max_value=total_pages,
                value=1,
                key="game_browser_page"
            )
        else:
            page_number = 1
            st.info(f"Page 1 of 1")
    
    # Get results with pagination
    offset = (page_number - 1) * items_per_page
    games = query.offset(offset).limit(items_per_page).all()
    
    # Display summary
    filter_info = []
    if search_term:
        filter_info.append(f"name: '{search_term}'")
    if genre_filter:
        filter_info.append(f"genres: {', '.join(genre_filter)}")
    if platform_filter:
        filter_info.append(f"platforms: {', '.join(platform_filter)}")
    
    if filter_info:
        st.info(f"📊 Showing {len(games)} games on page {page_number} of {total_pages} ({total_matching:,} matching games, filtered by {'; '.join(filter_info)})")
    else:
        st.info(f"📊 Showing {len(games)} games on page {page_number} of {total_pages} ({total_games:,} total games)")
    
    if games:
        # Display games in expandable cards
        for game in games:
            # Get player stats for this game
            latest_stats = db.query(PlayerStats).filter(
                PlayerStats.steam_appid == game.steam_appid
            ).order_by(PlayerStats.timestamp.desc()).first()
            
            # Build card header with key metrics
            owners_text = f"{latest_stats.estimated_owners:,}" if latest_stats and latest_stats.estimated_owners else "N/A"
            
            with st.expander(f"🎮 {game.name} | 👥 {owners_text} owners"):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    dev_text = game.developer or 'Unknown'
                    st.write(f"**Developer:** {dev_text}")
                    pub_text = game.publisher or 'Unknown'
                    st.write(f"**Publisher:** {pub_text}")
                    release = game.release_date
                    date_text = (
                        release.strftime('%Y-%m-%d')
                        if release else 'N/A'
                    )
                    st.write(f"**Release Date:** {date_text}")
                    st.write(f"**Steam App ID:** {game.steam_appid}")
                    
                    if latest_stats:
                        st.write(f"**Estimated Owners:** {latest_stats.estimated_owners:,}")
                        if latest_stats.peak_players_24h:
                            st.write(f"**Peak Players (24h):** {latest_stats.peak_players_24h:,}")
                    
                    if game.short_description:
                        st.write("**Description:**")
                        st.write(game.short_description)
                    
                    if game.genres:
                        genres = [g.name for g in game.genres]
                        st.write(f"**Genres:** {', '.join(genres)}")
                    
                    if game.tags:
                        tags = [t.name for t in game.tags[:10]]  # Show first 10 tags
                        st.write(f"**Tags:** {', '.join(tags)}")
                
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
                cutoff = datetime.now(timezone.utc) - timedelta(days=30)
                stats = db.query(PlayerStats).filter(
                    PlayerStats.steam_appid == game.steam_appid,
                    PlayerStats.timestamp >= cutoff,
                    PlayerStats.current_players.isnot(None)
                ).order_by(PlayerStats.timestamp).all()
                
                if stats:
                    st.write("**Player Count (Last 30 Days)**")
                    df_stats = pd.DataFrame([
                        {
                            'Date': s.timestamp,
                            'Players': s.current_players
                        }
                        for s in stats
                    ])
                    fig = px.line(df_stats, x='Date', y='Players')
                    st.plotly_chart(
                        fig, 
                        use_container_width=True,
                        key=f"player_chart_{game.steam_appid}"
                    )
    else:
        st.warning("⚠️ No games found with the selected filters. Try adjusting your criteria.")
    
    db.close()


def show_analytics():
    """Show analytics page with charts and insights."""
    st.header("📈 Advanced Analytics")
    
    db = get_session()
    
    # Filters sidebar
    with st.sidebar:
        st.markdown("### 🔍 Filters")
        time_range = st.selectbox(
            "Time Range:",
            [
                "Last 24 Hours", "Last 7 Days",
                "Last 30 Days", "Last 90 Days"
            ],
            index=2
        )
        
        # Genre filter
        all_genres = db.query(Genre.name).order_by(Genre.name).all()
        genre_names = [g[0] for g in all_genres]
        selected_genres = st.multiselect(
            "Filter by Genre:",
            options=genre_names,
            help="Leave empty to show all genres"
        )
    
    days_map = {
        "Last 24 Hours": 1,
        "Last 7 Days": 7,
        "Last 30 Days": 30,
        "Last 90 Days": 90
    }
    days = days_map[time_range]
    since = datetime.now(timezone.utc) - timedelta(days=days)
    
    # Create tabs for different analytics views
    tabs = st.tabs([
        "🎮 Player Analytics",
        "💰 Market Insights",
        "📊 Trend Analysis"
    ])
    tab1, tab2, tab3 = tabs
    
    with tab1:
        st.markdown(f"#### Top Performing Games ({time_range})")
        
        # Query for active games by peak players
        query = db.query(
            Game.name,
            func.max(PlayerStats.peak_players_24h).label('max_players'),
            func.avg(PlayerStats.peak_players_24h).label('avg_players'),
            func.count(PlayerStats.id).label('data_points')
        ).join(PlayerStats).filter(
            PlayerStats.timestamp >= since,
            PlayerStats.peak_players_24h.isnot(None),
            PlayerStats.peak_players_24h > 0
        )
        
        # Apply genre filter if selected
        if selected_genres:
            query = query.join(Game.genres).filter(
                Genre.name.in_(selected_genres)
            )
        
        active_games = query.group_by(Game.name).order_by(
            func.max(PlayerStats.peak_players_24h).desc()
        ).limit(15).all()
        
        if active_games:
            col1, col2 = st.columns([2, 1])
            
            with col1:
                # Interactive bar chart
                df_active = pd.DataFrame(
                    active_games,
                    columns=[
                        'Game', 'Peak Players',
                        'Avg Players', 'Data Points'
                    ]
                )
                # Handle None values before converting to int
                df_active['Peak Players'] = (
                    df_active['Peak Players'].fillna(0).astype(int)
                )
                df_active['Avg Players'] = (
                    df_active['Avg Players'].fillna(0).astype(int)
                )
                
                fig = go.Figure()
                fig.add_trace(go.Bar(
                    name='Peak Players',
                    x=df_active['Game'],
                    y=df_active['Peak Players'],
                    marker_color='#00d4ff'
                ))
                fig.add_trace(go.Bar(
                    name='Avg Players',
                    x=df_active['Game'],
                    y=df_active['Avg Players'],
                    marker_color='#4da6ff'
                ))
                
                fig.update_layout(
                    barmode='group',
                    title="Top 15 Games by Player Count",
                    xaxis_tickangle=-45,
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font_color='#ffffff',
                    height=500,
                    hovermode='x unified'
                )
                
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Statistics summary
                st.markdown("##### 📊 Summary Statistics")
                
                total_peak = df_active['Peak Players'].sum()
                avg_peak = df_active['Peak Players'].mean()
                top_game = df_active.iloc[0]
                
                st.metric("Total Peak Players", f"{total_peak:,}")
                st.metric("Average Peak", f"{int(avg_peak):,}")
                st.metric("Top Game", f"{top_game['Game'][:20]}...")
                st.metric("Peak", f"{int(top_game['Peak Players']):,}")
                
                # Market share visualization
                st.markdown("##### Market Share (Top 5)")
                top_5 = df_active.head(5)
                fig_pie = px.pie(
                    top_5,
                    values='Peak Players',
                    names='Game',
                    hole=0.4
                )
                fig_pie.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font_color='#ffffff',
                    height=300,
                    showlegend=False
                )
                st.plotly_chart(fig_pie, use_container_width=True)
        else:
            msg = "📊 No player statistics available for the selected filters."
            st.info(msg)
    
    with tab2:
        st.markdown("#### Market Insights & Ownership Data")
        
        # Get games with ownership data
        ownership_query = db.query(
            Game.name,
            Game.developer,
            func.max(PlayerStats.estimated_owners).label('owners'),
            func.max(PlayerStats.estimated_revenue).label('revenue')
        ).join(PlayerStats).filter(
            PlayerStats.estimated_owners.isnot(None),
            PlayerStats.timestamp >= since
        )
        
        if selected_genres:
            ownership_query = ownership_query.join(Game.genres).filter(
                Genre.name.in_(selected_genres)
            )
        
        ownership_data = ownership_query.group_by(
            Game.name, Game.developer
        ).order_by(
            func.max(PlayerStats.estimated_owners).desc()
        ).limit(20).all()
        
        if ownership_data:
            df_ownership = pd.DataFrame([
                {
                    'Game': o.name,
                    'Developer': o.developer or 'Unknown',
                    'Est. Owners': int(o.owners) if o.owners else 0,
                    'Est. Revenue': (
                        f"${int(o.revenue):,}"
                        if o.revenue else 'N/A'
                    )
                }
                for o in ownership_data
            ])
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Ownership distribution
                fig_owners = px.bar(
                    df_ownership.head(10),
                    x='Game',
                    y='Est. Owners',
                    color='Est. Owners',
                    color_continuous_scale='Viridis',
                    title="Top 10 Games by Ownership"
                )
                fig_owners.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font_color='#ffffff',
                    xaxis_tickangle=-45,
                    height=400
                )
                st.plotly_chart(fig_owners, use_container_width=True)
            
            with col2:
                # Treemap visualization
                fig_tree = px.treemap(
                    df_ownership.head(15),
                    path=['Developer', 'Game'],
                    values='Est. Owners',
                    title="Ownership by Developer"
                )
                fig_tree.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font_color='#ffffff',
                    height=400
                )
                st.plotly_chart(fig_tree, use_container_width=True)
            
            # Data table
            st.markdown("##### 📋 Detailed Ownership Data")
            st.dataframe(
                df_ownership,
                use_container_width=True,
                height=300,
                hide_index=True
            )
        else:
            msg = (
                "💡 No ownership data available. "
                "Import games with estimated_owners to see market insights."
            )
            st.info(msg)
    
    with tab3:
        st.markdown("#### Trend Analysis")
        
        # Get time series data for selected games
        st.markdown("##### Select games to visualize trends:")
        
        available_games = db.query(
            Game.name, Game.steam_appid
        ).join(PlayerStats).group_by(
            Game.name, Game.steam_appid
        ).limit(50).all()
        
        if available_games:
            game_dict = {g.name: g.steam_appid for g in available_games}
            default_games = (
                list(game_dict.keys())[:3]
                if len(game_dict) >= 3
                else list(game_dict.keys())
            )
            selected_trend_games = st.multiselect(
                "Choose games:",
                options=list(game_dict.keys()),
                default=default_games
            )
            
            if selected_trend_games:
                # Fetch time series data
                selected_ids = [
                    game_dict[name] for name in selected_trend_games
                ]
                
                trend_data = db.query(
                    Game.name,
                    PlayerStats.timestamp,
                    PlayerStats.current_players
                ).join(PlayerStats).filter(
                    Game.steam_appid.in_(selected_ids),
                    PlayerStats.timestamp >= since,
                    PlayerStats.current_players.isnot(None)
                ).order_by(PlayerStats.timestamp).all()
                
                if trend_data:
                    df_trend = pd.DataFrame([
                        {
                            'Game': t.name,
                            'Timestamp': t.timestamp,
                            'Players': t.current_players
                        }
                        for t in trend_data
                    ])
                    
                    # Line chart with multiple series
                    fig_trend = px.line(
                        df_trend,
                        x='Timestamp',
                        y='Players',
                        color='Game',
                        title=f"Player Count Trends ({time_range})",
                        markers=True
                    )
                    fig_trend.update_layout(
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        font_color='#ffffff',
                        height=500,
                        hovermode='x unified',
                        legend=dict(
                            orientation="h",
                            yanchor="bottom",
                            y=1.02,
                            xanchor="right",
                            x=1
                        )
                    )
                    st.plotly_chart(fig_trend, use_container_width=True)
                    
                    # Statistics table
                    st.markdown("##### 📈 Trend Statistics")
                    stats_data = []
                    for game_name in selected_trend_games:
                        game_df = df_trend[df_trend['Game'] == game_name]
                        if (not game_df.empty and
                                game_df['Players'].notna().all()):
                            current = game_df['Players'].iloc[-1]
                            peak = game_df['Players'].max()
                            avg = game_df['Players'].mean()
                            minimum = game_df['Players'].min()
                            first = game_df['Players'].iloc[0]
                            
                            checks = [
                                pd.notna(current), pd.notna(peak),
                                pd.notna(avg), pd.notna(minimum),
                                pd.notna(first)
                            ]
                            if all(checks):
                                stats_data.append({
                                    'Game': game_name,
                                    'Current': f"{int(current):,}",
                                    'Peak': f"{int(peak):,}",
                                    'Average': f"{int(avg):,}",
                                    'Min': f"{int(minimum):,}",
                                    'Trend': '📈' if current > first else '📉'
                                })
                    
                    if stats_data:
                        df_stats = pd.DataFrame(stats_data)
                        st.dataframe(
                            df_stats,
                            use_container_width=True,
                            hide_index=True
                        )
                else:
                    st.info("No trend data available for selected games.")
            else:
                msg = "Select games above to visualize player count trends."
                st.info(msg)
        else:
            st.info("📊 No games with player statistics available.")
    
    db.close()


def show_market_analysis():
    """Show market analysis page for game ownership overlap."""
    st.header("Market Analysis - Game Ownership Overlap")
    
    st.markdown("""
    Analyze the overlap between game audiences to determine addressable
    markets when combining different game types or genres.
    """)
    
    db = get_session()
    
    # Get all games with ownership data
    games_with_owners = db.query(
        Game.steam_appid,
        Game.name,
        Game.steam_appid,
        func.max(PlayerStats.estimated_owners).label('owners')
    ).join(PlayerStats).filter(
        PlayerStats.estimated_owners.isnot(None),
        PlayerStats.estimated_owners > 0
    ).group_by(
        Game.steam_appid, Game.name, Game.steam_appid
    ).order_by(Game.name).all()
    
    if not games_with_owners or len(games_with_owners) < 2:
        st.warning(
            "⚠️ Not enough games with ownership data. "
            "Run import_all_games.py to fetch ownership data from SteamSpy."
        )
        st.code("python import_all_games.py", language="bash")
        db.close()
        return
    
    st.markdown("---")
    
    # Game selection for comparison
    st.subheader("📊 Select Games to Compare")
    
    col1, col2 = st.columns(2)
    
    game_options = {
        f"{g.name} ({g.owners:,} owners)": g
        for g in games_with_owners
    }
    
    with col1:
        game1_name = st.selectbox(
            "Game A:",
            options=list(game_options.keys()),
            help="Select the first game"
        )
        game1 = game_options[game1_name]
    
    with col2:
        # Filter out the first game from second selection
        game2_options = {
            k: v for k, v in game_options.items()
            if v.steam_appid != game1.steam_appid
        }
        game2_name = st.selectbox(
            "Game B:",
            options=list(game2_options.keys()),
            help="Select the second game to compare"
        )
        game2 = game2_options[game2_name]
    
    # Option for additional games
    st.markdown("---")
    additional_games = st.multiselect(
        "➕ Add more games (optional):",
        options=[
            k for k, v in game_options.items()
            if v.steam_appid not in [game1.steam_appid, game2.steam_appid]
        ],
        help="Select additional games to include in the analysis"
    )
    
    # Build list of all selected games
    selected_games = [game1, game2]
    for game_name in additional_games:
        selected_games.append(game_options[game_name])
    
    st.markdown("---")
    
    # Market overlap analysis
    st.subheader("🎯 Market Overlap Analysis")
    
    # Get genres for each game
    game_genres = {}
    for game in selected_games:
        game_obj = db.query(Game).filter(Game.steam_appid == game.steam_appid).first()
        game_genres[game.steam_appid] = [g.name for g in game_obj.genres]
    
    # Calculate genre overlap score
    def calculate_overlap_factor(game1_id, game2_id):
        """Estimate overlap factor based on genre similarity."""
        genres1 = set(game_genres.get(game1_id, []))
        genres2 = set(game_genres.get(game2_id, []))
        
        if not genres1 or not genres2:
            return 0.15  # Default 15% overlap if no genre data
        
        # Calculate Jaccard similarity
        intersection = len(genres1 & genres2)
        union = len(genres1 | genres2)
        
        if union == 0:
            return 0.15
        
        jaccard = intersection / union
        
        # Scale to 10-40% overlap range based on similarity
        # More similar genres = higher overlap
        overlap = 0.10 + (jaccard * 0.30)
        return overlap
    
    # Display individual game statistics
    st.markdown("### 📈 Individual Game Statistics")
    
    cols = st.columns(len(selected_games))
    for idx, game in enumerate(selected_games):
        with cols[idx]:
            st.metric(
                f"**{game.name}**",
                f"{game.owners:,}",
                help=f"Estimated owners for {game.name}"
            )
            if game.steam_appid in game_genres and game_genres[game.steam_appid]:
                genres_text = ', '.join(game_genres[game.steam_appid][:3])
                st.caption(f"Genres: {genres_text}")
    
    st.markdown("---")
    
    # Two-game comparison
    if len(selected_games) == 2:
        st.markdown("### 🔄 Ownership Overlap (2-Game Analysis)")
        
        overlap_factor = calculate_overlap_factor(
            game1.steam_appid, game2.steam_appid
        )
        
        # Estimate overlap
        smaller_audience = min(game1.owners, game2.owners)
        estimated_overlap = int(smaller_audience * overlap_factor)
        
        # Addressable market
        addressable_for_game1 = game2.owners - estimated_overlap
        addressable_for_game2 = game1.owners - estimated_overlap
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            help_text = (
                f"Users estimated to own both games "
                f"(~{overlap_factor*100:.1f}% of smaller audience)"
            )
            st.metric(
                "Estimated Overlap",
                f"{estimated_overlap:,}",
                help=help_text
            )
        
        with col2:
            help_text = (
                f"Users who own {game1.name} but not {game2.name}"
            )
            st.metric(
                f"Addressable from {game1.name}",
                f"{addressable_for_game1:,}",
                help=help_text
            )
        
        with col3:
            help_text = (
                f"Users who own {game2.name} but not {game1.name}"
            )
            st.metric(
                f"Addressable from {game2.name}",
                f"{addressable_for_game2:,}",
                help=help_text
            )
        
        # Visualization
        st.markdown("### 📊 Overlap Visualization")
        
        # Create a simple overlap visualization
        fig = go.Figure()
        
        # Create overlapping circles representation
        fig.add_trace(go.Bar(
            x=[game1.name, 'Overlap', game2.name],
            y=[
                addressable_for_game2,
                estimated_overlap,
                addressable_for_game1
            ],
            marker_color=['#636EFA', '#EF553B', '#00CC96'],
            text=[
                f"{addressable_for_game2:,}",
                f"{estimated_overlap:,}",
                f"{addressable_for_game1:,}"
            ],
            textposition='auto',
        ))
        
        fig.update_layout(
            title="Audience Distribution",
            xaxis_title="Segment",
            yaxis_title="Estimated Owners",
            showlegend=False,
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Market insights
        st.markdown("### 💡 Market Insights")
        
        total_combined = game1.owners + game2.owners - estimated_overlap
        overlap_pct = (estimated_overlap / smaller_audience) * 100
        
        smaller_game_name = (
            game1.name if game1.owners < game2.owners else game2.name
        )
        
        st.info(f"""
        **Combined Addressable Market**: {total_combined:,} unique owners

        **Overlap Analysis**:
        - {overlap_pct:.1f}% of {smaller_game_name} owners also own
          the other game
        - If you create a game combining elements of both, you have a
          potential market of {total_combined:,} users
        - {addressable_for_game1:,} users familiar with {game1.name}
          might be interested in content similar to {game2.name}
        - {addressable_for_game2:,} users familiar with {game2.name}
          might be interested in content similar to {game1.name}
        """)
        
    else:
        # Multi-game comparison
        msg = f"### 🔄 Multi-Game Overlap ({len(selected_games)} Games)"
        st.markdown(msg)
        
        st.info(
            "💡 Multi-game overlap analysis estimates the intersection "
            "of audiences across multiple games. The more games you add, "
            "the smaller the overlap typically becomes."
        )
        
        # Calculate pairwise overlaps
        st.markdown("#### Pairwise Overlap Estimates")
        
        overlap_data = []
        for i in range(len(selected_games)):
            for j in range(i + 1, len(selected_games)):
                g1 = selected_games[i]
                g2 = selected_games[j]
                overlap_factor = calculate_overlap_factor(g1.id, g2.id)
                smaller = min(g1.owners, g2.owners)
                overlap = int(smaller * overlap_factor)
                
                overlap_data.append({
                    'Game A': g1.name,
                    'Game B': g2.name,
                    'Estimated Overlap': overlap,
                    'Overlap %': f"{overlap_factor*100:.1f}%"
                })
        
        df_overlap = pd.DataFrame(overlap_data)
        st.dataframe(df_overlap, use_container_width=True)
        
        # Total unique audience
        st.markdown("#### Combined Market Analysis")
        
        # Conservative estimate
        total_owners = sum(g.owners for g in selected_games)
        avg_overlap_reduction = 0.20
        estimated_unique = int(total_owners * (1 - avg_overlap_reduction))
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Owners (Sum)", f"{total_owners:,}")
        with col2:
            st.metric(
                "Est. Unique Owners",
                f"{estimated_unique:,}",
                help="Estimated unique owners accounting for overlap"
            )
        
        num_games = len(selected_games)
        st.info(f"""
        **Market Opportunity**: Creating a game that combines elements
        from these {num_games} games could address an estimated market
        of **{estimated_unique:,}** unique users.
        """)
    
    # Additional insights
    st.markdown("---")
    st.markdown("### ℹ️ About This Analysis")
    st.caption("""
    **Methodology**: This analysis estimates ownership overlap based on
    genre similarity and market data. Actual overlap may vary based on
    factors like:
    - Player preferences and gaming habits
    - Game popularity and release timing
    - Marketing and discoverability
    - Genre and gameplay mechanics

    **Note**: These are estimates based on available data. For precise
    market research, consider conducting user surveys or accessing
    detailed analytics platforms.
    """)
    
    db.close()


def show_data_management():
    """Show enhanced data management page."""
    st.header("📥 Data Management & Export")
    
    # Create tabs for different management features
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Import Single", "📦 Bulk Import",
        "📤 Export Data", "📈 Database Stats"
    ])
    
    with tab1:
        st.markdown("### Import Single Game")
        st.write("Import individual games by Steam App ID.")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            app_id = st.number_input(
                "Enter Steam App ID:",
                min_value=1,
                step=1,
                help=(
                    "You can find the App ID in the Steam store URL "
                    "(e.g., 730 for CS2)"
                ),
                key="single_import_id"
            )
        
        with col2:
            import_stats = st.checkbox(
                "Import player stats",
                value=True,
                key="import_stats_checkbox"
            )
        
        if st.button("🚀 Import Game", key="import_single_btn"):
            with st.spinner(f"Importing game {app_id}..."):
                db = get_session()
                importer = GameDataImporter(db)
                
                try:
                    game = importer.import_game(app_id)
                    if game:
                        st.success(
                            f"✅ Successfully imported: **{game.name}**"
                        )
                        
                        # Display game info
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            dev_text = game.developer or "Unknown"
                            st.metric("Developer", dev_text)
                        with col2:
                            st.metric("Genres", len(game.genres))
                        with col3:
                            platforms = []
                            if game.windows:
                                platforms.append("🪟")
                            if game.mac:
                                platforms.append("🍎")
                            if game.linux:
                                platforms.append("🐧")
                            st.metric("Platforms", " ".join(platforms))
                        
                        # Import player stats if requested
                        if import_stats:
                            with st.spinner("Fetching player statistics..."):
                                stats = importer.update_player_stats(app_id)
                                if stats:
                                    current = stats.current_players
                                    msg = f"📊 Current players: **{current:,}**"
                                    st.info(msg)
                                else:
                                    msg = "Could not fetch player statistics"
                                    st.warning(msg)
                    else:
                        msg = (
                            "❌ Failed to import game. "
                            "Check the App ID and try again."
                        )
                        st.error(msg)
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
                finally:
                    db.close()
        
        st.markdown("---")
        
        # Quick import popular games
        st.markdown("### 🎮 Quick Import - Popular Games")
        
        popular_games = [
            ("Counter-Strike 2", 730),
            ("Dota 2", 570),
            ("Team Fortress 2", 440),
            ("Rust", 252490),
            ("Apex Legends", 1172470),
            ("GTA V", 271590),
            ("PUBG", 578080),
            ("Stardew Valley", 413150),
        ]
        
        cols = st.columns(4)
        for idx, (name, appid) in enumerate(popular_games):
            with cols[idx % 4]:
                btn_key = f"popular_{appid}"
                if st.button(name, key=btn_key, use_container_width=True):
                    with st.spinner(f"Importing {name}..."):
                        db = get_session()
                        importer = GameDataImporter(db)
                        
                        try:
                            game = importer.import_game(appid)
                            if game:
                                st.success(f"✅ {game.name}")
                                # Update stats in background
                                importer.update_player_stats(appid)
                            else:
                                st.error("❌ Failed")
                        except Exception:
                            st.error("❌ Error")
                        finally:
                            db.close()
                            st.rerun()
    
    with tab2:
        st.markdown("### 📦 Bulk Import Operations")
        st.write("Import multiple games at once.")
        
        # Import method selection
        import_method = st.radio(
            "Select import method:",
            ["Top 50 Popular Games", "Custom List", "By Genre"],
            horizontal=True
        )
        
        if import_method == "Top 50 Popular Games":
            st.info("💡 This will import the top 50 most popular Steam games.")
            
            col1, col2 = st.columns(2)
            with col1:
                num_games = st.slider("Number of games:", 10, 50, 25, 5)
            with col2:
                import_delay = st.slider(
                    "Delay (seconds):", 0.5, 5.0, 1.0, 0.5
                )
            
            if st.button("🚀 Start Bulk Import", key="bulk_import_top50"):
                from src.utils.bulk_import import BulkImporter
                
                db = get_session()
                bulk_importer = BulkImporter(db)
                
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                try:
                    status_text.text("Starting bulk import...")
                    results = bulk_importer.import_top_games(
                        limit=num_games, delay=import_delay
                    )
                    progress_bar.progress(100)
                    
                    # Show results
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("✅ Success", len(results['success']))
                    with col2:
                        st.metric("⏭️ Skipped", len(results['skipped']))
                    with col3:
                        st.metric("❌ Failed", len(results['failed']))
                    
                    # Show report
                    with st.expander("📄 View Detailed Report"):
                        st.text(bulk_importer.get_import_report())
                    
                    st.success("Bulk import completed!")
                    
                except Exception as e:
                    st.error(f"Error during bulk import: {str(e)}")
                finally:
                    db.close()
        
        elif import_method == "Custom List":
            st.info("💡 Enter a comma-separated list of Steam App IDs.")
            
            app_ids_input = st.text_area(
                "App IDs (comma-separated):",
                placeholder="730, 570, 440, 252490",
                help="Example: 730, 570, 440"
            )
            
            import_delay = st.slider(
                "Delay (seconds):",
                0.5, 5.0, 1.0, 0.5,
                key="custom_delay"
            )
            
            if st.button("🚀 Import Custom List", key="bulk_import_custom"):
                if app_ids_input:
                    try:
                        # Parse app IDs
                        app_ids = [
                            int(x.strip())
                            for x in app_ids_input.split(',')
                            if x.strip()
                        ]
                        
                        if not app_ids:
                            st.error("No valid App IDs found")
                        else:
                            from src.utils.bulk_import import BulkImporter
                            
                            db = get_session()
                            bulk_importer = BulkImporter(db)
                            
                            progress_bar = st.progress(0)
                            status_text = st.empty()
                            
                            try:
                                msg = f"Importing {len(app_ids)} games..."
                                status_text.text(msg)
                                results = bulk_importer.import_games_batch(
                                    app_ids,
                                    delay=import_delay,
                                    update_stats=True
                                )
                                progress_bar.progress(100)
                                
                                # Show results
                                col1, col2, col3 = st.columns(3)
                                with col1:
                                    num_success = len(results['success'])
                                    st.metric("✅ Success", num_success)
                                with col2:
                                    num_skip = len(results['skipped'])
                                    st.metric("⏭️ Skipped", num_skip)
                                with col3:
                                    num_fail = len(results['failed'])
                                    st.metric("❌ Failed", num_fail)
                                
                                st.success("Import completed!")
                                
                            finally:
                                db.close()
                    
                    except ValueError:
                        msg = "Invalid input. Please enter comma-separated numbers."
                        st.error(msg)
                else:
                    st.warning("Please enter some App IDs")
    
    with tab3:
        st.markdown("### 📤 Export Data")
        st.write("Export your data in various formats.")
        
        export_type = st.selectbox(
            "Select data to export:",
            [
                "Games Catalog",
                "Player Statistics",
                "Genre Analysis",
                "Market Report"
            ]
        )
        
        db = get_session()
        
        try:
            from src.utils.data_export import DataExporter
            exporter = DataExporter(db)
            
            if export_type == "Games Catalog":
                st.markdown("#### 🎮 Export Games Catalog")
                
                # Filters
                with st.expander("🔍 Filters (Optional)"):
                    all_genre_names = [
                        g[0]
                        for g in db.query(Genre.name).distinct().all()
                    ]
                    filter_genre = st.selectbox(
                        "Genre:", ["All"] + all_genre_names
                    )
                    filter_developer = st.text_input(
                        "Developer contains:", ""
                    )
                
                export_format = st.radio(
                    "Format:", ["CSV", "JSON"], horizontal=True
                )
                
                if st.button("📥 Export Games", key="export_games"):
                    filters = {}
                    if filter_genre != "All":
                        filters['genre'] = filter_genre
                    if filter_developer:
                        filters['developer'] = filter_developer
                    
                    with st.spinner("Preparing export..."):
                        df = exporter.export_games_to_csv(filters)
                        
                        if not df.empty:
                            if export_format == "CSV":
                                csv = df.to_csv(index=False)
                                timestamp = datetime.now()
                                filename = (
                                    "steam_games_"
                                    f"{timestamp.strftime('%Y%m%d_%H%M%S')}.csv"
                                )
                                st.download_button(
                                    label="⬇️ Download CSV",
                                    data=csv,
                                    file_name=filename,
                                    mime="text/csv"
                                )
                            else:
                                json_str = df.to_json(
                                    orient='records', indent=2
                                )
                                timestamp = datetime.now()
                                filename = (
                                    "steam_games_"
                                    f"{timestamp.strftime('%Y%m%d_%H%M%S')}"
                                    ".json"
                                )
                                st.download_button(
                                    label="⬇️ Download JSON",
                                    data=json_str,
                                    file_name=filename,
                                    mime="application/json"
                                )
                            
                            msg = f"✅ Prepared {len(df)} games for export"
                            st.success(msg)
                            st.dataframe(df.head(10), use_container_width=True)
                        else:
                            st.warning("No games found matching filters")
            
            elif export_type == "Player Statistics":
                st.markdown("#### 📊 Export Player Statistics")
                
                # Date range
                col1, col2 = st.columns(2)
                with col1:
                    start_date = st.date_input("Start Date:", value=None)
                with col2:
                    end_date = st.date_input("End Date:", value=None)
                
                if st.button("📥 Export Stats", key="export_stats"):
                    with st.spinner("Preparing export..."):
                        start_dt = (
                            datetime.combine(start_date, datetime.min.time())
                            if start_date else None
                        )
                        end_dt = (
                            datetime.combine(end_date, datetime.max.time())
                            if end_date else None
                        )
                        df = exporter.export_player_stats_to_csv(
                            start_date=start_dt,
                            end_date=end_dt
                        )
                        
                        if not df.empty:
                            csv = df.to_csv(index=False)
                            timestamp = datetime.now()
                            filename = (
                                "player_stats_"
                                f"{timestamp.strftime('%Y%m%d_%H%M%S')}.csv"
                            )
                            st.download_button(
                                label="⬇️ Download CSV",
                                data=csv,
                                file_name=filename,
                                mime="text/csv"
                            )
                            msg = (
                                f"✅ Prepared {len(df)} stat records "
                                "for export"
                            )
                            st.success(msg)
                            st.dataframe(df.head(10), use_container_width=True)
                        else:
                            st.warning("No stats found for selected period")
            
            elif export_type == "Genre Analysis":
                st.markdown("#### 🎯 Export Genre Analysis")
                
                if st.button("📥 Export Genres", key="export_genres"):
                    with st.spinner("Preparing export..."):
                        json_data = exporter.export_genres_to_json()
                        timestamp = datetime.now()
                        filename = (
                            "genres_"
                            f"{timestamp.strftime('%Y%m%d_%H%M%S')}.json"
                        )
                        st.download_button(
                            label="⬇️ Download JSON",
                            data=json_data,
                            file_name=filename,
                            mime="application/json"
                        )
                        st.success("✅ Genre data ready for export")
                        st.json(json_data)
        
        finally:
            db.close()
    
    with tab4:
        st.markdown("### 📈 Database Statistics")
        
        db = get_session()
        
        try:
            from src.utils.data_export import DataExporter
            exporter = DataExporter(db)
            stats = exporter.get_summary_statistics()
            
            # Display stats
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("🎮 Total Games", f"{stats['total_games']:,}")
            with col2:
                st.metric("🎯 Genres", f"{stats['total_genres']:,}")
            with col3:
                total_stats = stats['total_player_stats']
                st.metric("📊 Player Stats", f"{total_stats:,}")
            with col4:
                games_stats = stats['games_with_stats']
                st.metric("📈 Games w/ Stats", f"{games_stats:,}")
            
            st.markdown("---")
            
            # Date range info
            date_range = stats['date_range']
            if date_range['earliest'] and date_range['latest']:
                st.markdown("#### 📅 Data Coverage")
                col1, col2 = st.columns(2)
                with col1:
                    earliest = date_range['earliest'][0]
                    date_str = earliest.strftime('%Y-%m-%d %H:%M')
                    st.info(f"**Earliest Data:** {date_str}")
                with col2:
                    latest = date_range['latest'][0]
                    date_str = latest.strftime('%Y-%m-%d %H:%M')
                    st.info(f"**Latest Data:** {date_str}")
            
            # Database health
            st.markdown("#### 🏥 Database Health")
            
            health_metrics = []
            
            # Check data completeness
            if stats['total_games'] > 0:
                completeness = (
                    (stats['games_with_stats'] / stats['total_games']) * 100
                )
                status = "success" if completeness > 50 else "warning"
                health_metrics.append((
                    "Data Completeness",
                    f"{completeness:.1f}%",
                    status
                ))
            
            # Check recent activity
            if stats['date_range']['latest']:
                latest_time = stats['date_range']['latest'][0]
                time_diff = datetime.utcnow() - latest_time
                hours_since_update = time_diff.total_seconds() / 3600
                if hours_since_update < 24:
                    health_metrics.append((
                        "Recent Activity",
                        "Active",
                        "success"
                    ))
                else:
                    health_metrics.append((
                        "Recent Activity",
                        f"{int(hours_since_update)}h ago",
                        "warning"
                    ))
            
            for metric_name, value, status in health_metrics:
                if status == "success":
                    st.success(f"✅ **{metric_name}:** {value}")
                else:
                    st.warning(f"⚠️ **{metric_name}:** {value}")
            
            # Cleanup actions
            st.markdown("#### 🧹 Maintenance")
            if st.button("🔄 Refresh All Player Stats"):
                msg = (
                    "This feature updates stats for all games "
                    "(can take a while)"
                )
                st.info(msg)
                st.warning("Feature coming soon!")
        
        finally:
            db.close()
