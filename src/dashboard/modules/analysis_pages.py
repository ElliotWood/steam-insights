"""
Additional analysis pages for Steam Insights Dashboard.
Contains genre saturation, rising trends, competition analysis, and positioning.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import func

from src.database.connection import get_db
from src.models.database import Game, Genre, PlayerStats, Tag


@st.cache_data(ttl=3600)
def get_genre_saturation_analysis():
    """Cached genre saturation analysis."""
    db = next(get_db())
    from src.utils.market_insights import MarketInsightsAnalyzer
    analyzer = MarketInsightsAnalyzer(db)
    return analyzer.analyze_genre_saturation()


@st.cache_data(ttl=3600)
def get_genre_stats():
    """Cached genre statistics."""
    db = next(get_db())
    results = db.query(
        Genre.name,
        func.count(Game.steam_appid).label('game_count'),
        func.avg(PlayerStats.estimated_owners).label('avg_owners')
    ).join(
        Game.genres
    ).outerjoin(
        PlayerStats
    ).group_by(
        Genre.name
    ).order_by(
        func.count(Game.steam_appid).desc()
    ).limit(30).all()
    
    return [{
        'genre': r.name,
        'game_count': r.game_count,
        'avg_owners': int(r.avg_owners) if r.avg_owners else 0
    } for r in results]


@st.cache_data(ttl=3600)
def get_tag_stats():
    """Cached tag statistics."""
    db = next(get_db())
    results = db.query(
        Tag.name,
        func.count(Game.steam_appid).label('game_count'),
        func.avg(PlayerStats.estimated_owners).label('avg_owners')
    ).join(
        Game.tags
    ).outerjoin(
        PlayerStats
    ).group_by(
        Tag.name
    ).order_by(
        func.count(Game.steam_appid).desc()
    ).limit(30).all()
    
    return [{
        'tag': r.name,
        'game_count': r.game_count,
        'avg_owners': int(r.avg_owners) if r.avg_owners else 0
    } for r in results]


def get_session():
    """Get database session."""
    return next(get_db())


def show_genre_saturation():
    """Genre saturation analysis - moved from Marketing Insights."""
    st.header("📊 Genre Saturation Analysis")
    st.markdown("*Lower saturation = easier to stand out*")
    
    st.info("Lower saturation = easier to stand out. Find underserved niches!")
    
    with st.spinner("Analyzing genres..."):
        results = get_genre_saturation_analysis()
    
    if results:
        df = pd.DataFrame(results)
        
        # Color code by opportunity (light theme)
        def highlight_opportunity(row):
            if row['opportunity'] == 'High':
                return ['background-color: #d4edda'] * len(row)
            elif row['opportunity'] == 'Medium':
                return ['background-color: #fff3cd'] * len(row)
            return ['background-color: #f8d7da'] * len(row)
        
        st.dataframe(
            df.style.apply(highlight_opportunity, axis=1),
            use_container_width=True,
            hide_index=True
        )
        
        # Visualization
        fig = px.bar(
            df.head(15),
            x='genre',
            y='game_count',
            color='opportunity',
            title='Top Genres by Game Count',
            color_discrete_map={
                'High': '#00ff00',
                'Medium': '#ffff00',
                'Low': '#ff0000'
            }
        )
        st.plotly_chart(fig, use_container_width=True)


def show_rising_trends():
    """Genre and tag performance analysis."""
    st.header("🔥 Genre Performance Analysis")
    st.markdown("*Discover high-performing genres and tags*")
    
    st.info(
        "Analyze genre and tag (sub-genre) performance based on "
        "player engagement and game success!"
    )
    
    # Toggle between genres and tags
    analysis_type = st.radio(
        "Analyze by:",
        ["Genres", "Tags (Sub-genres)"],
        horizontal=True,
        key="performance_analysis_type"
    )
    
    min_games = st.slider(
        "Minimum games per category",
        5, 50, 10, 5,
        key="rising_trends_min_games"
    )
    
    with st.spinner("Analyzing performance..."):
        if analysis_type == "Genres":
            results = get_genre_stats()
            type_col = 'genre'
        else:
            results = get_tag_stats()
            type_col = 'tag'
        
        # Filter by min games
        df = pd.DataFrame(results)
        df = df[df['game_count'] >= min_games]
    
    if not df.empty:
        # Format numbers
        df_display = df.copy()
        df_display['avg_owners'] = df_display['avg_owners'].apply(
            lambda x: f"{int(x):,}"
        )
        df_display['game_count'] = df_display['game_count'].apply(
            lambda x: f"{int(x):,}"
        )
        
        st.dataframe(df_display, use_container_width=True, hide_index=True)
        
        # Export functionality
        from src.utils.export_helpers import add_export_buttons
        with st.expander("📥 Export Results"):
            add_export_buttons(df, "genre_performance")
        
        # Visualization
        fig = px.bar(
            df.head(20),
            x=type_col,
            y='avg_owners',
            color='game_count',
            title=f'Top {analysis_type} by Average Owners',
            labels={'avg_owners': 'Average Owners', type_col: analysis_type}
        )
        st.plotly_chart(fig, use_container_width=True)
        
        st.caption(
            f"📊 Showing {len(df)} categories with at least "
            f"{min_games} games"
        )
    else:
        st.warning(
            f"No categories found with at least {min_games} games"
        )


def show_competition_calculator():
    """Competition calculator - analyze genre and tag combinations."""
    st.header("⚔️ Competition Index Calculator")
    st.markdown(
        "*Calculate how competitive your genre and "
        "sub-genre (tag) combination is*"
    )
    
    db = get_session()
    
    st.info(
        "Explore competition across genres and tags - "
        "auto-loaded with popular selections!"
    )
    
    # Get available genres
    available_genres = db.query(Genre.name).join(
        Game.genres
    ).distinct().order_by(Genre.name).all()
    genre_list = [g[0] for g in available_genres]
    
    # Get popular tags (top 100 by game count)
    popular_tags = db.query(Tag.name).join(
        Tag.games
    ).group_by(Tag.name).order_by(
        func.count(Game.steam_appid).desc()
    ).limit(100).all()
    tag_list = [t[0] for t in popular_tags]
    
    # Default selections for auto-loading
    default_genres = (
        ["Action", "Indie"]
        if "Action" in genre_list and "Indie" in genre_list
        else genre_list[:2]
    )
    default_tags = (
        ["Singleplayer", "Multi-player"]
        if "Singleplayer" in tag_list
        else tag_list[:2]
    )
    
    # Genre multi-select with defaults
    selected_genres = st.multiselect(
        "Select genres",
        options=genre_list,
        default=default_genres,
        key="competition_calc_genres",
        help="Select one or more genres to analyze competition"
    )
    
    # Tag multi-select with defaults (sub-genres)
    selected_tags = st.multiselect(
        "Select tags (sub-genres)",
        options=tag_list,
        default=default_tags,
        key="competition_calc_tags",
        help="Select one or more tags to narrow down the competition analysis"
    )
    
    if selected_genres or selected_tags:
        with st.spinner("Calculating competition..."):
            # Build query for games matching genres and/or tags
            query = db.query(func.count(func.distinct(Game.steam_appid)))
            
            if selected_genres and selected_tags:
                # Games with ANY selected genre AND ANY selected tag
                total_games = query.join(Game.genres).join(Game.tags).filter(
                    Genre.name.in_(selected_genres),
                    Tag.name.in_(selected_tags)
                ).scalar() or 0
            elif selected_genres:
                # Only genres selected
                total_games = query.join(Game.genres).filter(
                    Genre.name.in_(selected_genres)
                ).scalar() or 0
            else:
                # Only tags selected
                total_games = query.join(Game.tags).filter(
                    Tag.name.in_(selected_tags)
                ).scalar() or 0
            
            # Get average owners with same filters
            avg_query = db.query(
                func.avg(PlayerStats.estimated_owners)
            ).join(Game)
            
            if selected_genres and selected_tags:
                avg_owners_result = avg_query.join(
                    Game.genres
                ).join(Game.tags).filter(
                    Genre.name.in_(selected_genres),
                    Tag.name.in_(selected_tags),
                    PlayerStats.estimated_owners > 0
                ).scalar()
            elif selected_genres:
                avg_owners_result = avg_query.join(Game.genres).filter(
                    Genre.name.in_(selected_genres),
                    PlayerStats.estimated_owners > 0
                ).scalar()
            else:
                avg_owners_result = avg_query.join(Game.tags).filter(
                    Tag.name.in_(selected_tags),
                    PlayerStats.estimated_owners > 0
                ).scalar()
            
            avg_owners = int(avg_owners_result) if avg_owners_result else 0
            
            # Calculate competition index and difficulty
            if avg_owners > 0:
                competition_index = (total_games / avg_owners) * 100000
                if competition_index < 50:
                    difficulty = "Easy"
                elif competition_index < 150:
                    difficulty = "Medium"
                else:
                    difficulty = "Hard"
            else:
                competition_index = 0
                difficulty = "Easy"
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Games", f"{total_games:,}")
        with col2:
            st.metric("Average Owners", f"{avg_owners:,}")
        with col3:
            st.metric("Difficulty", difficulty)
        
        st.info(f"Competition Index: {competition_index:.2f}")
        
        # Auto-show top games (always visible)
        st.subheader("🎯 Top Successful Games in This Space")
        
        # Build query for top games
        top_games_query = db.query(
            Game.name,
            Game.steam_appid,
            PlayerStats.estimated_owners
        ).join(PlayerStats)
        
        if selected_genres and selected_tags:
            top_games = top_games_query.join(
                Game.genres
            ).join(Game.tags).filter(
                Genre.name.in_(selected_genres),
                Tag.name.in_(selected_tags),
                PlayerStats.estimated_owners.isnot(None)
            ).order_by(
                PlayerStats.estimated_owners.desc()
            ).limit(10).all()
        elif selected_genres:
            top_games = top_games_query.join(Game.genres).filter(
                Genre.name.in_(selected_genres),
                PlayerStats.estimated_owners.isnot(None)
            ).order_by(
                PlayerStats.estimated_owners.desc()
            ).limit(10).all()
        else:
            top_games = top_games_query.join(Game.tags).filter(
                Tag.name.in_(selected_tags),
                PlayerStats.estimated_owners.isnot(None)
            ).order_by(
                PlayerStats.estimated_owners.desc()
            ).limit(10).all()
            
        if top_games:
            for game_name, appid, owners in top_games:
                expander_title = f"{game_name} - {owners:,} owners"
                with st.expander(expander_title):
                    st.write(f"**Steam ID:** {appid}")
                    
                    # Get genres and tags for this game
                    game_obj = db.query(Game).filter(
                        Game.steam_appid == appid
                    ).first()
                    if game_obj:
                        genre_names = [g.name for g in game_obj.genres]
                        tag_names = [t.name for t in game_obj.tags]
                        
                        if selected_genres:
                            matching_genres = [
                                g for g in genre_names
                                if g in selected_genres
                            ]
                            genres_text = ', '.join(genre_names)
                            st.write(f"**All Genres:** {genres_text}")
                            if matching_genres:
                                matching_text = ', '.join(matching_genres)
                                st.write(
                                    f"**Matching Genres:** {matching_text}"
                                )
                        
                        if selected_tags:
                            matching_tags = [
                                t for t in tag_names
                                if t in selected_tags
                            ]
                            # Show first 10 tags to avoid clutter
                            tags_text = ', '.join(tag_names[:10])
                            if len(tag_names) > 10:
                                tags_text += f" (+{len(tag_names)-10} more)"
                            st.write(f"**Tags:** {tags_text}")
                            if matching_tags:
                                matching_text = ', '.join(matching_tags)
                                st.write(
                                    f"**Matching Tags:** {matching_text}"
                                )
        else:
            st.warning(
                "No highly successful games found with these criteria. "
                "Try adjusting your selections."
            )
    else:
        st.info("👆 Select genres and/or tags above to explore competition")
    
    db.close()
    
    db.close()


def show_market_positioning():
    """Market positioning report - explore by genres and tags."""
    st.header("📊 Market Positioning Report")
    st.markdown("*Comprehensive strategic analysis for your game concept*")
    
    db = get_session()
    from src.utils.market_insights import MarketInsightsAnalyzer
    analyzer = MarketInsightsAnalyzer(db)
    
    st.info(
        "Explore market positioning by genres and tags - "
        "auto-loaded for easy exploration!"
    )
    
    # Get available genres
    available_genres = db.query(Genre.name).join(
        Game.genres
    ).distinct().order_by(Genre.name).all()
    genre_list = [g[0] for g in available_genres]
    
    # Get popular tags (top 100)
    popular_tags = db.query(Tag.name).join(
        Tag.games
    ).group_by(Tag.name).order_by(
        func.count(Game.steam_appid).desc()
    ).limit(100).all()
    tag_list = [t[0] for t in popular_tags]
    
    # Default selections
    default_genres = (
        ["Indie"] if "Indie" in genre_list else genre_list[:1]
    )
    default_tags = (
        ["Singleplayer"]
        if "Singleplayer" in tag_list
        else tag_list[:1]
    )
    
    # Genre and tag selection
    col1, col2 = st.columns(2)
    with col1:
        selected_genres = st.multiselect(
            "Select genres",
            options=genre_list,
            default=default_genres,
            key="positioning_genres"
        )
    with col2:
        selected_tags = st.multiselect(
            "Select tags (sub-genres)",
            options=tag_list,
            default=default_tags,
            key="positioning_tags"
        )
    
    if selected_genres or selected_tags:
        # Combine for analysis (tags list expected by analyzer)
        analysis_criteria = selected_genres + selected_tags
        
        with st.spinner("Generating comprehensive report..."):
            report = analyzer.generate_positioning_report(analysis_criteria)
        
        # Competition section
        st.markdown("### Competition Analysis")
        comp = report['competition']
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Games", f"{comp['total_games']:,}")
            st.metric("Difficulty", comp['difficulty'])
        with col2:
            st.metric("Average Owners", f"{comp['avg_owners']:,}")
            comp_idx = comp['competition_index']
            st.metric("Competition Index", f"{comp_idx:.2f}")
        
        # Recommendations section
        if 'recommendations' in report:
            st.markdown("### 💡 Strategic Recommendations")
            for rec in report['recommendations']:
                st.info(rec)
        
        # Similar games
        if 'similar_games' in report and report['similar_games']:
            st.markdown("### 🎯 Study These Successful Games")
            for game in report['similar_games'][:5]:
                expander_title = f"{game['name']} - {game['owners']:,} owners"
                with st.expander(expander_title):
                    tags_text = ', '.join(game['tags'])
                    st.write(f"**Tags:** {tags_text}")
                    matching_text = ', '.join(game['matching_tags'])
                    st.write(f"**Matching Tags:** {matching_text}")
                    st.write(f"**Steam ID:** {game['steam_appid']}")
    
    db.close()
