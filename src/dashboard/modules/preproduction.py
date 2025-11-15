"""
Preproduction & Pre-Launch stage pages.
"""

import streamlit as st
import pandas as pd
import plotly.express as px

from src.database.connection import get_db


def get_session():
    """Get database session."""
    return next(get_db())


def show_pricing_strategy():
    """Pricing sweet spot analysis."""
    st.header("💰 Pricing Strategy")
    st.markdown("*Find optimal price points for your genre*")
    
    db = get_session()
    from src.utils.market_insights import MarketInsightsAnalyzer
    analyzer = MarketInsightsAnalyzer(db)
    
    st.info(
        "Price signals quality and affects conversion rates. "
        "Find the sweet spot!"
    )
    
    with st.spinner("Analyzing pricing data..."):
        results = analyzer.analyze_pricing_sweet_spots()
    
    if results:
        df = pd.DataFrame(results)
        
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        # Chart
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


def show_competitor_tracking():
    """Track specific competitors."""
    st.header("👀 Competitor Tracking")
    st.markdown("*Monitor similar games during development*")
    
    from src.dashboard.app import show_game_search
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
        df = pd.DataFrame(results)
        
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        # Chart
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
    
    from src.dashboard.modules.concept_research import (
        show_competition_analysis
    )
    show_competition_analysis()


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
            max_value=500000,
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
