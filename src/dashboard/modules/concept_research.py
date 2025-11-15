"""
Concept Research stage pages: Market opportunities and analysis.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

from src.database.connection import get_db
from src.models.database import Game, PlayerStats


def get_session():
    """Get database session."""
    return next(get_db())


def show_market_opportunities():
    """Show golden age opportunities and market gaps."""
    st.header("🌟 Market Opportunities")
    st.markdown("*Find emerging genres and underserved niches*")
    
    db = get_session()
    from src.utils.market_insights import MarketInsightsAnalyzer
    analyzer = MarketInsightsAnalyzer(db)
    
    tab1, tab2 = st.tabs(["🌟 Golden Age Genres", "📊 Genre Saturation"])
    
    with tab1:
        st.subheader("Golden Age Opportunities")
        st.info(
            "**Chris Zukowski's 'Optimistic View' (Nov 2025)**\n\n"
            "Many genres are exploding in popularity with short dev "
            "cycles. Find genres with high success rates and low "
            "competition!"
        )
        
        # Interactive filters
        with st.expander("⚙️ Adjust Search Criteria", expanded=False):
            col1, col2 = st.columns(2)
            with col1:
                min_owners = st.number_input(
                    "Min. avg owners (success threshold)",
                    min_value=1000,
                    max_value=100000,
                    value=10000,
                    step=5000,
                    key="golden_min_owners"
                )
                max_competition = st.number_input(
                    "Max. total games (competition limit)",
                    min_value=100,
                    max_value=5000,
                    value=1000,
                    step=100,
                    key="golden_max_games"
                )
            with col2:
                min_recent = st.number_input(
                    "Min. recent releases (activity)",
                    min_value=1,
                    max_value=20,
                    value=3,
                    step=1,
                    key="golden_min_recent"
                )
                lookback_days = st.number_input(
                    "Lookback period (days)",
                    min_value=30,
                    max_value=365,
                    value=180,
                    step=30,
                    key="golden_lookback"
                )
        
        with st.spinner("Analyzing market opportunities..."):
            opportunities = analyzer.analyze_golden_age_opportunities(
                min_owners=min_owners,
                max_total_games=max_competition,
                min_recent_releases=min_recent,
                lookback_days=lookback_days
            )
            
            # Get diagnostic info
            total_games = db.query(Game).count()
            games_with_owners = db.query(Game).join(PlayerStats).filter(
                PlayerStats.estimated_owners > min_owners
            ).count()
            recent_games = db.query(Game).filter(
                Game.release_date >=
                datetime.now() - timedelta(days=lookback_days)
            ).count()
        
        if opportunities:
            df = pd.DataFrame(opportunities)
            
            st.dataframe(df, use_container_width=True, hide_index=True)
            
            # Visualization
            fig = px.scatter(
                df.head(15),
                x='total_games',
                y='avg_owners',
                size='opportunity_score',
                color='competition_level',
                hover_data=['genre', 'recent_releases', 'trend'],
                title='Market Opportunities Map',
                labels={
                    'total_games': 'Competition Level (Total Games)',
                    'avg_owners': 'Success Potential (Avg Owners)',
                    'opportunity_score': 'Opportunity Score'
                },
                color_discrete_map={
                    'Low': '#00ff00',
                    'Medium': '#ffff00',
                    'High': '#ff6b6b'
                }
            )
            st.plotly_chart(fig, use_container_width=True)
            
            st.success(
                "💡 **Best opportunities:** High avg_owners + "
                "Low total_games + Growing trend"
            )
        else:
            st.warning("⚠️ No clear opportunities found in current data.")
            
            with st.expander(
                "🔍 Diagnostic Information - What was analyzed?"
            ):
                st.write(f"**Total games in database:** {total_games:,}")
                st.write(
                    f"**Games with {min_owners:,}+ owners:** "
                    f"{games_with_owners:,}"
                )
                st.write(
                    f"**Recent releases (last {lookback_days} days):** "
                    f"{recent_games:,}"
                )
                
                st.markdown("---")
                st.markdown("**Why no opportunities?**")
                st.write(
                    "The algorithm looks for genres that meet ALL criteria:"
                )
                st.write(
                    f"- ✓ At least {min_recent} releases in last "
                    f"{lookback_days} days"
                )
                st.write(
                    f"- ✓ Less than {max_competition:,} total games "
                    "(low competition)"
                )
                st.write(
                    f"- ✓ Average {min_owners:,}+ owners "
                    "(proven success)"
                )
                st.write(
                    "- ✓ Growing trend (recent releases > 10% of total)"
                )
                
                st.info(
                    "💡 **Suggestion:** Try adjusting the criteria above "
                    "or import more recent games."
                )
    
    with tab2:
        st.subheader("Genre Saturation Analysis")
        st.info(
            "Lower saturation = easier to stand out. "
            "Find underserved niches!"
        )
        
        with st.spinner("Analyzing genre saturation..."):
            results = analyzer.analyze_genre_saturation()
        
        if results:
            df = pd.DataFrame(results)
            
            # Color-coded display
            st.dataframe(df, use_container_width=True, hide_index=True)
            
            # Chart
            fig = px.bar(
                df.head(15),
                x='genre',
                y='game_count',
                color='opportunity',
                title='Top Genres by Competition Level',
                color_discrete_map={
                    'High': '#00ff00',
                    'Medium': '#ffff00',
                    'Low': '#ff6b6b'
                }
            )
            st.plotly_chart(fig, use_container_width=True)


def show_genre_analysis():
    """Detailed genre performance analysis."""
    st.header("📊 Genre Analysis")
    st.markdown("*Deep dive into genre performance and trends*")
    
    # Import and delegate to analytics
    from src.dashboard.app import show_analytics
    show_analytics()


def show_revenue_projections():
    """Revenue projection calculator."""
    st.header("💰 Revenue Projections")
    st.markdown("*Estimate potential revenue based on market data*")
    
    db = get_session()
    from src.utils.market_insights import MarketInsightsAnalyzer
    analyzer = MarketInsightsAnalyzer(db)
    
    st.markdown("""
    ### 📊 Revenue Estimation
    Based on wishlist conversion rates and pricing data.
    """)
    
    col1, col2 = st.columns(2)
    with col1:
        wishlists = st.number_input(
            "Expected wishlists at launch",
            min_value=100,
            max_value=500000,
            value=10000,
            step=1000
        )
        price = st.number_input(
            "Launch price (USD)",
            min_value=1.0,
            max_value=100.0,
            value=19.99,
            step=1.0
        )
    
    with col2:
        conversion_low = st.slider(
            "Conservative conversion rate (%)",
            1,
            50,
            15,
            help="Typical range: 15-25%"
        )
        conversion_high = st.slider(
            "Optimistic conversion rate (%)",
            1,
            50,
            25,
            help="For strong launches"
        )
    
    if st.button("Calculate Projections", type="primary"):
        # Calculate
        sales_low = int(wishlists * (conversion_low / 100))
        sales_high = int(wishlists * (conversion_high / 100))
        
        revenue_low = sales_low * price * 0.7  # Steam's cut
        revenue_high = sales_high * price * 0.7
        
        st.success("✅ Revenue projections calculated!")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(
                "Conservative Estimate",
                f"${revenue_low:,.0f}",
                f"{sales_low:,} copies"
            )
        with col2:
            st.metric(
                "Expected Estimate",
                f"${(revenue_low + revenue_high) / 2:,.0f}",
                f"{(sales_low + sales_high) // 2:,} copies"
            )
        with col3:
            st.metric(
                "Optimistic Estimate",
                f"${revenue_high:,.0f}",
                f"{sales_high:,} copies"
            )
        
        st.info(
            "💡 **Note:** Revenue assumes 30% platform cut. "
            "Actual results vary based on marketing, reviews, and timing."
        )


def show_competition_analysis():
    """Competition analysis and market positioning."""
    st.header("🎯 Competition Analysis")
    st.markdown("*Analyze your competitive landscape*")
    
    db = get_session()
    from src.utils.market_insights import MarketInsightsAnalyzer
    analyzer = MarketInsightsAnalyzer(db)
    
    st.info(
        "Understand your competition to position your game effectively."
    )
    
    # Genre selection
    from src.models.database import Genre
    genres = db.query(Genre).all()
    selected_genre = st.selectbox(
        "Select genre to analyze",
        genres,
        format_func=lambda x: x.name
    )
    
    if st.button("Analyze Competition", type="primary"):
        with st.spinner("Analyzing competitive landscape..."):
            analysis = analyzer.analyze_genre_competition(
                selected_genre.name
            )
        
        if analysis:
            st.subheader(f"Competition in {selected_genre.name}")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Games", f"{analysis['total_games']:,}")
            with col2:
                st.metric(
                    "Avg Owners",
                    f"{analysis.get('avg_owners', 0):,.0f}"
                )
            with col3:
                st.metric(
                    "Top Game Owners",
                    f"{analysis.get('max_owners', 0):,.0f}"
                )
            
            if 'market_leaders' in analysis:
                st.markdown("### 🏆 Market Leaders")
                leaders_df = pd.DataFrame(analysis['market_leaders'])
                st.dataframe(
                    leaders_df,
                    use_container_width=True,
                    hide_index=True
                )


def show_tag_strategy():
    """Tag selection and optimization strategy."""
    st.header("🏷️ Tag Strategy")
    st.markdown("*Choose the right tags to get discovered*")
    
    db = get_session()
    from src.models.database import Tag, game_tags
    from sqlalchemy import func
    
    st.info(
        "Popular tags = more searches, but also more competition. "
        "Find the balance!"
    )
    
    # Get tag usage statistics
    tag_stats = db.query(
        Tag.name,
        func.count(game_tags.c.game_id).label('game_count')
    ).join(
        game_tags,
        Tag.id == game_tags.c.tag_id
    ).group_by(
        Tag.name
    ).order_by(
        func.count(game_tags.c.game_id).desc()
    ).limit(50).all()
    
    if tag_stats:
        df = pd.DataFrame([
            {'Tag': name, 'Games Using Tag': count}
            for name, count in tag_stats
        ])
        
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        # Visualization
        fig = px.bar(
            df.head(20),
            x='Tag',
            y='Games Using Tag',
            title='Most Popular Tags',
            color='Games Using Tag',
            color_continuous_scale='Viridis'
        )
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)
        
        st.success(
            "💡 **Strategy:** Mix popular tags (discoverability) "
            "with niche tags (less competition)"
        )
