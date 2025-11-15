"""
Additional analysis pages for Steam Insights Dashboard.
Contains genre saturation, rising trends, competition analysis, and positioning.
"""

import streamlit as st
import pandas as pd
import plotly.express as px

from src.database.connection import get_db


def get_session():
    """Get database session."""
    return next(get_db())


def show_genre_saturation():
    """Genre saturation analysis - moved from Marketing Insights."""
    st.header("📊 Genre Saturation Analysis")
    st.markdown("*Lower saturation = easier to stand out*")
    
    db = get_session()
    from src.utils.market_insights import MarketInsightsAnalyzer
    analyzer = MarketInsightsAnalyzer(db)
    
    st.info("Lower saturation = easier to stand out. Find underserved niches!")
    
    with st.spinner("Analyzing genres..."):
        results = analyzer.analyze_genre_saturation()
    
    if results:
        df = pd.DataFrame(results)
        
        # Color code by opportunity
        def highlight_opportunity(row):
            if row['opportunity'] == 'High':
                return ['background-color: #1e3a1e'] * len(row)
            elif row['opportunity'] == 'Medium':
                return ['background-color: #3a3a1e'] * len(row)
            return ['background-color: #3a1e1e'] * len(row)
        
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
    
    db.close()


def show_rising_trends():
    """Rising trends analysis - moved from Marketing Insights."""
    st.header("🔥 Emerging Genre Trends")
    st.markdown("*Catch trends early for better visibility*")
    
    db = get_session()
    from src.utils.market_insights import MarketInsightsAnalyzer
    analyzer = MarketInsightsAnalyzer(db)
    
    st.info("Catch trends early for better visibility. New releases in hot genres!")
    
    days = st.slider(
        "Analyze last N days",
        30, 180, 90, 30,
        key="rising_trends_days"
    )
    
    with st.spinner(f"Analyzing trends from last {days} days..."):
        results = analyzer.find_rising_trends(days)
    
    if results:
        df = pd.DataFrame(results)
        
        fig = px.scatter(
            df,
            x='new_releases',
            y='avg_success',
            size='momentum_score',
            text='trend',
            title='Genre Momentum (size = momentum score)',
            labels={
                'new_releases': 'New Releases',
                'avg_success': 'Avg Success (owners)'
            }
        )
        st.plotly_chart(fig, use_container_width=True)
        
        st.dataframe(df, use_container_width=True, hide_index=True)
    
    db.close()


def show_competition_calculator():
    """Competition calculator - moved from Marketing Insights."""
    st.header("⚔️ Competition Index Calculator")
    st.markdown("*Calculate how competitive your genre combination is*")
    
    db = get_session()
    from src.utils.market_insights import MarketInsightsAnalyzer
    analyzer = MarketInsightsAnalyzer(db)
    
    st.info("Calculate how competitive your genre combination is!")
    
    # Tag input
    tags_input = st.text_input(
        "Enter tags (comma-separated)",
        placeholder="roguelike, platformer, pixel art",
        key="competition_calc_tags"
    )
    
    if tags_input:
        tags = [t.strip() for t in tags_input.split(',')]
        
        with st.spinner("Calculating competition..."):
            result = analyzer.calculate_competition_index(tags)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Games", f"{result['total_games']:,}")
        with col2:
            st.metric("Average Owners", f"{result['avg_owners']:,}")
        with col3:
            st.metric("Difficulty", result['difficulty'])
        
        comp_index = result['competition_index']
        st.info(f"Competition Index: {comp_index:.2f}")
        
        # Show similar successful games
        if st.button("Find Successful Games with These Tags"):
            similar = analyzer.find_similar_successful_games(tags)
            if similar:
                st.subheader("🎯 Study These Successful Games")
                for game in similar:
                    expander_title = (
                        f"{game['name']} - {game['owners']:,} owners"
                    )
                    with st.expander(expander_title):
                        tags_text = ', '.join(game['tags'])
                        st.write(f"**Tags:** {tags_text}")
                        matching_text = ', '.join(game['matching_tags'])
                        st.write(f"**Matching:** {matching_text}")
                        st.write(f"**Steam ID:** {game['steam_appid']}")
    
    db.close()


def show_market_positioning():
    """Market positioning report - moved from Marketing Insights."""
    st.header("📊 Market Positioning Report")
    st.markdown("*Comprehensive strategic analysis for your game concept*")
    
    db = get_session()
    from src.utils.market_insights import MarketInsightsAnalyzer
    analyzer = MarketInsightsAnalyzer(db)
    
    st.info("Full strategic analysis for your game concept!")
    
    tags_input = st.text_input(
        "Enter your game's tags",
        placeholder="metroidvania, souls-like, indie",
        key="positioning_tags"
    )
    
    if tags_input and st.button("Generate Report"):
        tags = [t.strip() for t in tags_input.split(',')]
        
        with st.spinner("Generating comprehensive report..."):
            report = analyzer.generate_positioning_report(tags)
        
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
