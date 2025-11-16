"""
Streamlit dashboard for Steam Insights.
"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from sqlalchemy import func

from src.database.connection import get_db, init_db
from src.models.database import Game, Genre, PlayerStats, PricingHistory
from src.api.steam_client import SteamAPIClient
from src.etl.game_importer import GameDataImporter
from src.dashboard.modules.data_management import (
    show_top_charts, show_market_analytics, show_llm_mining
)
from src.dashboard.modules.concept_research import (
    show_market_opportunities, show_genre_analysis,
    show_revenue_projections, show_competition_analysis, show_tag_strategy
)
from src.dashboard.modules.preproduction import (
    show_pricing_strategy, show_competitor_tracking, show_genre_trends,
    show_similar_games, show_demo_calculator, show_benchmark_game,
    show_review_estimator
)
from src.dashboard.modules.production_pages import (
    show_overview, show_game_performance, show_market_position
)
from src.dashboard.modules.postlaunch_pages import (
    show_game_search, show_analytics, show_market_analysis,
    show_data_management
)
from src.dashboard.modules.analysis_pages import (
    show_genre_saturation, show_rising_trends,
    show_competition_calculator, show_market_positioning
)
from src.dashboard.modules.feedback import (
    show_feedback_button, show_feedback_management, render_feedback_modal
)
from src.dashboard.modules.steam_page_builder import show_steam_page_builder

# Page configuration
st.set_page_config(
    page_title="Steam Insights Dashboard",
    page_icon=".streamlit/static/logo_icon_small_54x54.png",
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
    # Logo and title header
    col1, col2, col3 = st.columns([1, 6, 1])
    with col1:
        st.image(".streamlit/static/logo_icon_large_103x103.png", width=80)
    with col2:
        st.title("Steam Insights Dashboard")
        st.markdown("*Data-driven game development & marketing intelligence*")
    with col3:
        st.markdown("<br>", unsafe_allow_html=True)
        show_feedback_button()
    
    # Render feedback modal if active
    render_feedback_modal()
    
    st.markdown("---")
    
    # Sidebar with logo and development stage navigation
    with st.sidebar:
        # Sidebar logo
        st.image(".streamlit/static/logo_name_330x100.png", use_container_width=True)
        st.markdown("---")
        
        st.header("🎯 Development Stage")
        st.markdown("*Navigate by your current phase*")
        
        # Stage-based navigation
        stage = st.selectbox(
            "Where are you in development?",
            [
                "💡 Concept & Research",
                "🎨 Pre-Production & Validation",
                "🔨 Production & Tracking",
                "📢 Pre-Launch Marketing",
                "🚀 Launch & Analytics",
                "⚙️ Data Management"
            ],
            key="dev_stage_selector"
        )
        
        st.markdown("---")
        
        # Show relevant pages for selected stage
        if stage == "💡 Concept & Research":
            st.markdown("### Available Tools")
            page = st.radio(
                "Select analysis:",
                [
                    "🌟 Market Opportunities",
                    "📊 Genre Analysis",
                    "🎮 Game Explorer",
                    "📈 Google Trends",
                    "📊 Genre Saturation",
                    "🔥 Rising Trends"
                ],
                label_visibility="collapsed",
                key="concept_research_nav"
            )
            
        elif stage == "🎨 Pre-Production & Validation":
            st.markdown("### Available Tools")
            page = st.radio(
                "Select analysis:",
                [
                    "💎 Revenue Projections",
                    "🎯 Competition Analysis",
                    "🏷️ Tag Strategy",
                    "💰 Pricing Strategy",
                    "🎨 Steam Page Builder"
                ],
                label_visibility="collapsed",
                key="preproduction_nav"
            )
            
        elif stage == "🔨 Production & Tracking":
            st.markdown("### Available Tools")
            page = st.radio(
                "Select analysis:",
                [
                    "👀 Competitor Tracking",
                    "📈 Genre Trends",
                    "🔍 Similar Games",
                    "⚔️ Competition Calculator",
                    "📊 Market Positioning"
                ],
                label_visibility="collapsed",
                key="production_nav"
            )
            
        elif stage == "📢 Pre-Launch Marketing":
            st.markdown("### Available Tools")
            page = st.radio(
                "Select analysis:",
                [
                    "🚀 Demo Impact Calculator",
                    "💎 Benchmark Your Game",
                    "📊 Review Estimator",
                    "📈 Trend Validation"
                ],
                label_visibility="collapsed",
                key="prelaunch_nav"
            )
            
        elif stage == "🚀 Launch & Analytics":
            st.markdown("### Available Tools")
            page = st.radio(
                "Select analysis:",
                [
                    "📊 Dashboard Overview",
                    "🎮 Game Performance",
                    "📈 Market Position",
                    "🔍 Post-Mortem Analysis"
                ],
                label_visibility="collapsed",
                key="launch_analytics_nav"
            )
            
        else:  # Data Management
            st.markdown("### Available Tools")
            page = st.radio(
                "Select tool:",
                [
                    "⚙️ System Settings",
                    "📊 Top Charts",
                    "🔍 Market Analytics",
                    "🤖 LLM Data Mining",
                    "💬 Feedback Management"
                ],
                label_visibility="collapsed",
                key="data_mgmt_nav"
            )
        
        st.markdown("---")
        st.markdown("### 💡 Quick Guide")
        
        if stage == "💡 Concept & Research":
            st.info(
                "**Find your niche!**\n\n"
                "• Discover golden age genres\n"
                "• Analyze market saturation\n"
                "• Research successful games\n"
                "• Validate trends with Google"
            )
        elif stage == "🎨 Pre-Production & Validation":
            st.info(
                "**Validate your idea!**\n\n"
                "• Project potential revenue\n"
                "• Assess competition level\n"
                "• Plan tag combinations\n"
                "• Set optimal pricing"
            )
        elif stage == "🔨 Production & Tracking":
            st.info(
                "**Stay informed!**\n\n"
                "• Monitor competitors\n"
                "• Track genre momentum\n"
                "• Study similar successes\n"
                "• Adapt to market shifts"
            )
        elif stage == "📢 Pre-Launch Marketing":
            st.info(
                "**Build momentum!**\n\n"
                "• Calculate demo impact\n"
                "• Benchmark wishlists\n"
                "• Estimate launch reviews\n"
                "• Optimize marketing timing"
            )
        elif stage == "🚀 Launch & Analytics":
            st.info(
                "**Track & optimize!**\n\n"
                "• Monitor real-time metrics\n"
                "• Compare to benchmarks\n"
                "• Analyze market position\n"
                "• Learn for next project"
            )
        else:
            st.info(
                "**Manage your data**\n\n"
                "• Import game databases\n"
                "• Update Steam data\n"
                "• Export analytics\n"
                "• Configure settings"
            )
    
    # Route to appropriate page based on selection
    route_to_page(page, stage)


def route_to_page(page: str, stage: str):
    """Route to the appropriate page based on user selection."""
    from src.dashboard.modules.marketing_pages import show_google_trends
    
    # Concept & Research Stage
    if page == "🌟 Market Opportunities":
        show_market_opportunities()
    elif page == "📊 Genre Analysis":
        show_genre_analysis()
    elif page == "🎮 Game Explorer":
        show_game_search()
    elif page == "📈 Google Trends":
        show_google_trends()
    
    elif page == "📊 Genre Saturation":
        show_genre_saturation()
    
    elif page == "🔥 Rising Trends":
        show_rising_trends()
    
    # Pre-Production & Validation Stage
    elif page == "💎 Revenue Projections":
        show_revenue_projections()
    elif page == "🎯 Competition Analysis":
        show_competition_analysis()
    elif page == "🏷️ Tag Strategy":
        show_tag_strategy()
    elif page == "💰 Pricing Strategy":
        show_pricing_strategy()
    elif page == "🎨 Steam Page Builder":
        show_steam_page_builder()
    
    # Production & Tracking Stage
    elif page == "👀 Competitor Tracking":
        show_competitor_tracking()
    elif page == "📈 Genre Trends":
        show_genre_trends()
    elif page == "🔍 Similar Games":
        show_similar_games()
    
    elif page == "⚔️ Competition Calculator":
        show_competition_calculator()
    
    elif page == "📊 Market Positioning":
        show_market_positioning()
    
    # Pre-Launch Marketing Stage
    elif page == "🚀 Demo Impact Calculator":
        show_demo_calculator()
    elif page == "💎 Benchmark Your Game":
        show_benchmark_game()
    elif page == "📊 Review Estimator":
        show_review_estimator()
    elif page == "📈 Trend Validation":
        show_google_trends()
    
    # Launch & Analytics Stage  
    elif page == "📊 Dashboard Overview":
        show_overview()
    elif page == "🎮 Game Performance":
        show_game_performance()
    elif page == "📈 Market Position":
        show_market_position()
    elif page == "🔍 Post-Mortem Analysis":
        show_analytics()
    
    # Data Management
    elif page == "⚙️ System Settings":
        show_data_management()
    elif page == "📊 Top Charts":
        show_top_charts()
    elif page == "🔍 Market Analytics":
        show_market_analytics()
    elif page == "🤖 LLM Data Mining":
        show_llm_mining()
    elif page == "💬 Feedback Management":
        show_feedback_management()
    
    else:
        # Default fallback
        show_overview()


# ============================================================================
# LAUNCH & ANALYTICS STAGE PAGES
# ============================================================================

def show_game_performance():
    """Show golden age opportunities and market gaps."""
    st.header("🌟 Market Opportunities")
    st.markdown("*Find emerging genres and underserved niches*")
    
    from datetime import datetime, timedelta
    from src.models.database import Game, PlayerStats
    
    db = get_session()
    from src.utils.market_insights import MarketInsightsAnalyzer
    analyzer = MarketInsightsAnalyzer(db)
    
    tab1, tab2 = st.tabs(["🌟 Golden Age Genres", "📊 Genre Saturation"])
    
    with tab1:
        st.subheader("Golden Age Opportunities")
        st.info(
            "**Chris Zukowski's 'Optimistic View' (Nov 2025)**\n\n"
            "Many genres are exploding in popularity with short dev cycles. "
            "Find genres with high success rates and low competition!"
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
                Game.release_date >= datetime.now() - timedelta(days=lookback_days)
            ).count()
        
        if opportunities:
            import pandas as pd
            df = pd.DataFrame(opportunities)
            
            st.dataframe(df, use_container_width=True, hide_index=True)
            
            # Visualization
            import plotly.express as px
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
            
            with st.expander("🔍 Diagnostic Information - What was analyzed?"):
                st.write(f"**Total games in database:** {total_games:,}")
                st.write(f"**Games with {min_owners:,}+ owners:** {games_with_owners:,}")
                st.write(f"**Recent releases (last {lookback_days} days):** {recent_games:,}")
                
                st.markdown("---")
                st.markdown("**Why no opportunities?**")
                st.write("The algorithm looks for genres that meet ALL criteria:")
                st.write(f"- ✓ At least {min_recent} releases in last {lookback_days} days")
                st.write(f"- ✓ Less than {max_competition:,} total games (low competition)")
                st.write(f"- ✓ Average {min_owners:,}+ owners (proven success)")
                st.write("- ✓ Growing trend (recent releases > 10% of total)")
                
                st.info("💡 **Suggestion:** Try adjusting the criteria above or import more recent games.")
    
    with tab2:
        st.subheader("Genre Saturation Analysis")
        st.info(
            "Lower saturation = easier to stand out. "
            "Find underserved niches!"
        )
        
        with st.spinner("Analyzing genre saturation..."):
            results = analyzer.analyze_genre_saturation()
        
        if results:
            import pandas as pd
            df = pd.DataFrame(results)
            
            # Color-coded display
            st.dataframe(df, use_container_width=True, hide_index=True)
            
            # Chart
            import plotly.express as px
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
    
    # Reuse existing analytics content
    show_analytics()


# ============================================================================
# PRE-PRODUCTION & VALIDATION STAGE PAGES
# ============================================================================

def show_revenue_projections():
    """Revenue projection calculator."""
    st.header("💎 Revenue Projections")
    st.markdown("*Calculate potential revenue using real benchmarks*")
    
    db = get_session()
    from src.utils.market_insights import MarketInsightsAnalyzer
    analyzer = MarketInsightsAnalyzer(db)
    
    st.markdown("""
    ### 📊 Conversion Benchmarks (Chris Zukowski)
    Based on 2020-2025 industry data:
    - **Bronze tier:** 11.93% conversion ($1K revenue)
    - **Silver tier:** 20.49% conversion ($10K revenue)
    - **Gold tier:** 25.35% conversion ($100K revenue)  
    - **Diamond tier:** 27.08% conversion ($1M revenue)
    """)
    
    col1, col2 = st.columns(2)
    with col1:
        wishlists = st.number_input(
            "Estimated wishlists at launch",
            min_value=100,
            max_value=None,
            value=10000,
            step=1000,
            help="Target wishlist count by launch day"
        )
    with col2:
        price = st.number_input(
            "Game price (USD)",
            min_value=1.0,
            max_value=100.0,
            value=19.99,
            step=0.50,
            help="Your planned launch price"
        )
    
    if st.button("Calculate Revenue Potential", type="primary"):
        with st.spinner("Running projections..."):
            projections = analyzer.calculate_revenue_projections(
                wishlists,
                price
            )
        
        st.success("✅ Projections calculated!")
        
        # Display results by tier
        import pandas as pd
        data = []
        for tier, proj in projections['projections_by_tier'].items():
            data.append({
                'Tier': tier.title(),
                'Conversion Rate': f"{proj['conversion_rate']}%",
                'Estimated Sales': f"{proj['estimated_sales']:,}",
                'Gross Revenue': f"${proj['gross_revenue']:,.2f}",
                'Net Revenue (after Steam 30%)': f"${proj['net_revenue']:,.2f}"
            })
        
        df = pd.DataFrame(data)
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        # Highlight gold/diamond tiers
        col1, col2 = st.columns(2)
        with col1:
            gold_net = projections['projections_by_tier']['gold']['net_revenue']
            st.metric(
                "Gold Tier Target",
                f"${gold_net:,.0f}",
                help="25.35% conversion rate"
            )
        with col2:
            diamond_net = projections['projections_by_tier']['diamond']['net_revenue']
            st.metric(
                "Diamond Tier Target", 
                f"${diamond_net:,.0f}",
                help="27.08% conversion rate"
            )
        
        st.info("💡 " + " | ".join(projections['notes']))
        
        st.markdown("""
        ### 🎯 How to Reach Higher Tiers
        - **Build more wishlists:** Marketing, demos, Steam Next Fest
        - **Improve conversion:** Polish, reviews, launch timing
        - **Optimize pricing:** Test different price points
        """)


def show_competition_analysis():
    """Competition scoring and analysis."""
    st.header("🎯 Competition Analysis") 
    st.markdown("*Evaluate how competitive your genre/tags are*")
    
    db = get_session()
    from src.utils.market_insights import MarketInsightsAnalyzer
    from src.models.database import Tag, Genre
    from sqlalchemy import func
    analyzer = MarketInsightsAnalyzer(db)
    
    st.info(
        "**Competition Index Formula:**\n\n"
        "More games + Lower average success = Higher competition\n\n"
        "Target 'Easy' or 'Moderate' markets for best chances!"
    )
    
    # Show available tags/genres
    with st.expander("📋 View Available Tags & Genres", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Top Tags:**")
            top_tags = db.query(Tag.name).join(Tag.games).group_by(Tag.name).order_by(
                func.count().desc()
            ).limit(15).all()
            if top_tags:
                st.write(", ".join([t[0] for t in top_tags]))
            else:
                st.write("No tags in database")
        
        with col2:
            st.markdown("**Top Genres:**")
            top_genres = db.query(Genre.name).join(Genre.games).group_by(Genre.name).order_by(
                func.count().desc()
            ).limit(15).all()
            if top_genres:
                st.write(", ".join([g[0] for g in top_genres]))
            else:
                st.write("No genres in database")
    
    # Tag input
    tag_input = st.text_input(
        "Enter your game tags/genres (comma-separated)",
        "Multi-player, Steam Achievements",
        help="Use tags or genres from the list above"
    )
    
    if st.button("Calculate Competition", type="primary"):
        tags = [t.strip() for t in tag_input.split(',')]
        
        with st.spinner("Analyzing competition..."):
            result = analyzer.calculate_competition_index(tags)
        
        # Display results
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Games", f"{result['total_games']:,}")
        with col2:
            st.metric("Average Owners", f"{result['avg_owners']:,}")
        with col3:
            difficulty = result['difficulty']
            color_map = {
                'Easy': '🟢',
                'Moderate': '🟡',
                'Hard': '🟠',
                'Very Hard': '🔴'
            }
            st.metric(
                "Difficulty",
                f"{color_map.get(difficulty, '⚪')} {difficulty}"
            )
        
        st.metric(
            "Competition Index",
            f"{result['competition_index']:.2f}",
            help="Lower is better"
        )
        
        # Show similar successful games
        st.subheader("🏆 Successful Games in This Space")
        if result['total_games'] > 0:
            with st.spinner("Finding similar successful games..."):
                similar = analyzer.find_similar_successful_games(tags)
            
            if similar:
                for game in similar[:10]:
                    with st.expander(
                        f"🎮 {game['name']} - {game['owners']:,} owners"
                    ):
                        st.write(f"**Tags:** {', '.join(game['matching_tags'])}")
                        st.write(f"**All Tags:** {', '.join(game['tags'])}")
                        st.write(f"**Steam ID:** {game['steam_appid']}")
            else:
                st.info("No successful games found with those exact tags. Try broader or different tags.")
        else:
            st.warning("⚠️ No games found matching those tags. Please check the available tags/genres above and try again.")


def show_tag_strategy():
    """Tag combination analysis."""
    st.header("🏷️ Tag Strategy")
    st.markdown("*Find winning tag combinations*")
    
    db = get_session()
    from src.utils.market_insights import MarketInsightsAnalyzer
    analyzer = MarketInsightsAnalyzer(db)
    
    st.info(
        "Discover which tag combinations lead to success. "
        "Learn from what works!"
    )
    
    min_owners = st.slider(
        "Minimum owners to consider 'successful'",
        10000,
        1000000,
        100000,
        10000
    )
    
    with st.spinner("Analyzing tag combinations..."):
        results = analyzer.find_tag_combinations(min_owners)
    
    if results:
        for combo in results[:15]:
            with st.expander(
                f"🏆 {combo['tag_combination']} - "
                f"{combo['successful_games']} successful games"
            ):
                st.metric("Average Owners", f"{combo['avg_owners']:,}")
                st.write(f"**Examples:** {', '.join(combo['examples'])}")


def show_pricing_strategy():
    """Pricing sweet spot analysis."""
    st.header("💰 Pricing Strategy")
    st.markdown("*Find optimal price points for your genre*")
    
    db = get_session()
    from src.utils.market_insights import MarketInsightsAnalyzer
    from src.models.database import PricingHistory
    analyzer = MarketInsightsAnalyzer(db)
    
    # Check if we have pricing data
    pricing_count = db.query(PricingHistory).filter(
        PricingHistory.price_usd.isnot(None)
    ).count()
    
    if pricing_count == 0:
        st.warning(
            "⚠️ **No Pricing Data Available**\n\n"
            "The database doesn't contain pricing information yet. "
            "Pricing data needs to be collected from the Steam API.\n\n"
            "**To add pricing data:**\n"
            "1. Go to 'Data Management' section\n"
            "2. Import games from Steam API (includes pricing)\n"
            "3. Or update existing games to fetch current prices"
        )
        
        st.info(
            "📊 **Price Recommendations (Industry Averages):**\n\n"
            "• **Indie games:** $5-$20\n"
            "• **Mid-tier:** $20-$40\n"
            "• **AAA titles:** $40-$70\n\n"
            "Lower prices can increase conversions but signal "
            "lower quality. Price according to production value "
            "and genre expectations!"
        )
        return
    
    st.info(
        f"Price signals quality and affects conversion rates. "
        f"Analyzing {pricing_count:,} games with pricing data..."
    )
    
    with st.spinner("Analyzing pricing data..."):
        results = analyzer.analyze_pricing_sweet_spots()
    
    if results:
        import pandas as pd
        df = pd.DataFrame(results)
        
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        # Chart
        import plotly.express as px
        
        # Add avg_price column for scatter plot
        df['avg_price'] = df['price_range'].map({
            'Free-$5': 2.5,
            '$5-$10': 7.5,
            '$10-$15': 12.5,
            '$15-$20': 17.5,
            '$20-$30': 25,
            '$30+': 40
        })
        
        fig = px.scatter(
            df,
            x='avg_price',
            y='avg_owners',
            size='game_count',
            color='revenue_estimate',
            hover_data=['price_range'],
            title='Price vs Success',
            labels={
                'avg_price': 'Average Price',
                'avg_owners': 'Average Owners',
                'revenue_estimate': 'Est. Revenue'
            }
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning(
            "Unable to generate pricing analysis. "
            "Not enough data in price ranges."
        )


# ============================================================================
# PRODUCTION & TRACKING STAGE PAGES
# ============================================================================

def show_competitor_tracking():
    """Track specific competitors."""
    st.header("👀 Competitor Tracking")
    st.markdown("*Monitor similar games during development*")
    
    show_game_search()


def show_genre_trends():
    """Show rising and falling genre trends."""
    st.header("📈 Genre Trends & Momentum")
    st.markdown("*Track what's hot and what's not*")
    
    db = get_session()
    from src.utils.market_insights import MarketInsightsAnalyzer
    analyzer = MarketInsightsAnalyzer(db)
    
    days = st.slider(
        "Time window (days)",
        7,
        180,
        90,
        help="How far back to look for trends"
    )
    
    with st.spinner("Analyzing genre momentum..."):
        results = analyzer.find_rising_trends(days)
    
    if results:
        import pandas as pd
        df = pd.DataFrame(results)
        
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        # Chart
        import plotly.express as px
        fig = px.bar(
            df.head(15),
            x='genre',
            y='momentum_score',
            title=f'Genre Momentum (Last {days} Days)',
            color='momentum_score',
            color_continuous_scale='Viridis'
        )
        st.plotly_chart(fig, use_container_width=True)


def show_similar_games():
    """Find and analyze similar successful games."""
    st.header("🔍 Similar Successful Games")
    st.markdown("*Learn from games like yours*")
    
    show_competition_analysis()


# ============================================================================
# PRE-LAUNCH MARKETING STAGE PAGES
# ============================================================================

def show_demo_calculator():
    """Demo impact calculator."""
    st.header("🚀 Demo Impact Calculator")
    st.markdown("*Estimate wishlist boost from releasing a demo*")
    
    db = get_session()
    from src.utils.market_insights import MarketInsightsAnalyzer
    analyzer = MarketInsightsAnalyzer(db)
    
    st.markdown("""
    ### 📊 The Demo Effect (Chris Zukowski, Aug 2025)
    **Case Study: Parcel Simulator**
    - Before demo: 7,000 wishlists
    - After demo: 42,000 wishlists
    - **6x multiplier!**
    
    Quality demos are powerful marketing tools.
    """)
    
    current_wl = st.number_input(
        "Current wishlist count",
        min_value=100,
        max_value=100000,
        value=5000,
        step=100
    )
    
    if st.button("Calculate Demo Impact", type="primary"):
        with st.spinner("Calculating potential..."):
            impact = analyzer.calculate_demo_impact_potential(current_wl)
        
        st.success("✅ Demo impact projections ready!")
        
        import pandas as pd
        data = []
        for quality, proj in impact['projections'].items():
            data.append({
                'Demo Quality': quality.replace('_', ' ').title(),
                'Multiplier': f"{proj['multiplier']}x",
                'Projected Wishlists': f"{proj['projected_wishlists']:,}",
                'Expected Gain': f"+{proj['expected_gain']:,}"
            })
        
        df = pd.DataFrame(data)
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        # Highlight excellent demo potential
        excellent = impact['projections']['excellent_demo']
        st.metric(
            "🌟 Excellent Demo Potential",
            f"{excellent['projected_wishlists']:,} wishlists",
            delta=f"+{excellent['expected_gain']:,}"
        )
        
        st.markdown("### 💡 Demo Best Practices")
        for rec in impact['recommendations']:
            st.info(f"✓ {rec}")


def show_benchmark_game():
    """Benchmark game against industry tiers."""
    st.header("💎 Benchmark Your Game")
    st.markdown("*Compare your metrics to industry benchmarks*")
    
    db = get_session()
    from src.utils.market_insights import MarketInsightsAnalyzer
    analyzer = MarketInsightsAnalyzer(db)
    
    st.markdown("""
    ### 📊 Industry Benchmark Tiers
    **Wishlist Targets:**
    - 🥉 Bronze: 6,000 wishlists
    - 🥈 Silver: 6,000 wishlists  
    - 🥇 Gold: 30,000 wishlists
    - 💎 Diamond: 150,000+ wishlists
    
    **Weekly Growth Targets:**
    - Bronze: 0-40/week
    - Silver: 40-100/week
    - Gold: 100-300/week
    - Diamond: 300-3,000/week
    """)
    
    col1, col2 = st.columns(2)
    with col1:
        total_wishlists = st.number_input(
            "Total wishlists",
            min_value=0,
            max_value=None,
            value=5000,
            step=100
        )
    with col2:
        weekly_wishlists = st.number_input(
            "Wishlists gained last week",
            min_value=0,
            max_value=10000,
            value=50,
            step=10
        )
    
    if st.button("Benchmark My Game", type="primary"):
        with st.spinner("Analyzing performance..."):
            benchmark = analyzer.benchmark_against_tier(
                total_wishlists,
                weekly_wishlists
            )
        
        tier = benchmark['wishlist_tier'].title()
        tier_icons = {
            'Bronze': '🥉',
            'Silver': '🥈',
            'Gold': '🥇',
            'Diamond': '💎',
            'Below_Bronze': '⚪'
        }
        
        st.markdown(
            f"## Your Tier: {tier_icons.get(tier, '❓')} {tier}"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric(
                "Total Wishlists",
                f"{benchmark['current_metrics']['total_wishlists']:,}"
            )
        with col2:
            st.metric(
                "Weekly Wishlists",
                f"{benchmark['current_metrics']['weekly_wishlists']:,}"
            )
        
        if benchmark['next_tier_targets']:
            st.markdown("### 🎯 Next Tier Goals")
            targets = benchmark['next_tier_targets']
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric(
                    f"Wishlists Needed for {targets['tier'].title()}",
                    f"{targets['wishlists_needed']:,}"
                )
            with col2:
                weeks = targets['weeks_at_current_rate']
                if weeks == float('inf'):
                    st.metric("Weeks at Current Rate", "∞")
                else:
                    st.metric("Weeks at Current Rate", f"{int(weeks)}")
        
        if benchmark['recommendations']:
            st.markdown("### 💡 Recommendations")
            for rec in benchmark['recommendations']:
                st.warning(rec)


def show_review_estimator():
    """Review count estimator."""
    st.header("📊 Review Count Estimator")
    st.markdown("*Estimate launch reviews using the Boxleiter Number*")
    
    db = get_session()
    from src.utils.market_insights import MarketInsightsAnalyzer
    analyzer = MarketInsightsAnalyzer(db)
    
    st.markdown("""
    ### 📊 The Boxleiter Number
    Industry metric for sales-to-review ratio:
    - **2021 median:** 31 sales per review
    - **Historical trend:** Declining from 79 (2013-2017)
    - **Varies by:** Genre, quality, engagement
    """)
    
    projected_sales = st.number_input(
        "Projected first-week sales",
        min_value=10,
        max_value=100000,
        value=1000,
        step=100
    )
    
    if st.button("Estimate Reviews", type="primary"):
        with st.spinner("Calculating..."):
            estimate = analyzer.estimate_review_count(projected_sales)
        
        st.success("✅ Review estimate calculated!")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(
                "Projected Sales",
                f"{estimate['projected_sales']:,}"
            )
        with col2:
            st.metric(
                "Estimated Reviews",
                f"{estimate['estimated_reviews']:,}"
            )
        with col3:
            st.metric(
                "Sales per Review",
                estimate['sales_per_review_ratio']
            )
        
        st.markdown("### 📝 Important Notes")
        for note in estimate['notes']:
            st.info(note)


# ============================================================================
# LAUNCH & ANALYTICS STAGE PAGES
# ============================================================================

# ============================================================================
# LAUNCH & ANALYTICS STAGE PAGES
# ============================================================================
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
        
        # Check data quality first
        total_games = db.query(func.count(Game.steam_appid)).scalar() or 0
        games_with_genres = db.query(
            func.count(func.distinct(Game.steam_appid))
        ).join(Genre.games).scalar() or 0
        coverage_pct = (
            games_with_genres / total_games * 100
        ) if total_games > 0 else 0
        
        # Show warning if coverage is poor
        if coverage_pct < 50:
            st.warning(
                f"⚠️ **Data Quality Issue**: Only "
                f"{games_with_genres:,} out of {total_games:,} games "
                f"({coverage_pct:.1f}%) have genre data.\n\n"
                f"**Why?** The current import uses SteamSpy API which "
                f"doesn't provide genre information.\n\n"
                f"**Solution:** Run the data enrichment script to "
                f"fetch genres from Steam Store API. "
                f"See `DATA_ENRICHMENT_STRATEGY.md` for details."
            )
            
            # Show minimal data anyway, but with clear labeling
            genre_counts = db.query(
                Genre.name,
                func.count(Game.steam_appid).label('count')
            ).join(Genre.games).group_by(Genre.name).order_by(
                func.count(Game.steam_appid).desc()
            ).all()
            
            if genre_counts:
                st.markdown(
                    f"**Current Genre Data** (from "
                    f"{games_with_genres:,} games only):"
                )
                df_genres = pd.DataFrame(
                    genre_counts,
                    columns=['Genre', 'Game Count']
                )
                st.dataframe(
                    df_genres,
                    use_container_width=True,
                    hide_index=True
                )
        else:
            # Normal visualization when data quality is good
            genre_counts = db.query(
                Genre.name,
                func.count(Game.steam_appid).label('count')
            ).join(Genre.games).group_by(Genre.name).order_by(
                func.count(Game.steam_appid).desc()
            ).limit(10).all()
            
            if genre_counts:
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    df_genres = pd.DataFrame(
                        genre_counts,
                        columns=['Genre', 'Game Count']
                    )
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
                st.info(
                    "📥 No genre data available yet. "
                    "Import some games first!"
                )
    
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


# ============================================================================
# EXTRACTED FUNCTIONS - NOW IN MODULE FILES
# ========================================================================
# The following functions have been moved to separate module files:
# - show_game_search, show_analytics, show_market_analysis,
#   show_data_management -> postlaunch_pages.py
# - show_genre_saturation, show_rising_trends,
#   show_competition_calculator, show_market_positioning
#   -> analysis_pages.py


if __name__ == "__main__":
    main()

