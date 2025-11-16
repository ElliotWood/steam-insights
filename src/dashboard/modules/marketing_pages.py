"""
Marketing Insights and Google Trends dashboard pages.
"""


def show_marketing_insights():
    """
    Display Chris Zukowski-inspired marketing insights.
    Additional analysis tools - main features are in the stage-based navigation.
    """
    import streamlit as st
    from src.database.connection import get_db
    from src.utils.market_insights import MarketInsightsAnalyzer
    
    st.header("🎯 Marketing Insights - Additional Tools")
    st.markdown(
        "**Note:** The main benchmark features (Revenue Projections, Demo Calculator, etc.) "
        "are now integrated into the stage-based navigation above. "
        "This page contains supplementary analysis tools."
    )
    
    db = next(get_db())
    analyzer = MarketInsightsAnalyzer(db)
    
    # Analysis selector - removed the 5 new features that have dedicated pages
    analysis_type = st.selectbox(
        "Choose Analysis",
        [
            "Genre Saturation",
            "Successful Tag Combinations", 
            "Pricing Sweet Spots",
            "Rising Trends",
            "Competition Calculator",
            "Market Positioning Report"
        ],
        key="marketing_insights_selector"
    )
    
    # SUPPLEMENTARY ANALYSIS TOOLS
    if analysis_type == "Genre Saturation":
        st.subheader("📊 Genre Saturation Analysis")
        st.info("Lower saturation = easier to stand out. Find underserved niches!")
        
        with st.spinner("Analyzing genres..."):
            results = analyzer.analyze_genre_saturation()
        
        if results:
            import pandas as pd
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
            import plotly.express as px
            fig = px.bar(
                df.head(15),
                x='genre',
                y='game_count',
                color='opportunity',
                title='Top Genres by Game Count',
                color_discrete_map={'High': '#00ff00', 'Medium': '#ffff00', 'Low': '#ff0000'}
            )
            st.plotly_chart(fig, use_container_width=True)
    
    elif analysis_type == "Successful Tag Combinations":
        st.subheader("🎮 Winning Tag Combinations")
        st.info("Genre mashups that worked. Unique combos help you stand out!")
        
        min_owners = st.number_input("Minimum owners for 'successful'", min_value=1000, value=100000, step=10000)
        
        with st.spinner("Finding successful combos..."):
            results = analyzer.find_tag_combinations(min_owners)
        
        if results:
            for combo in results[:10]:
                with st.expander(f"🏆 {combo['tag_combination']} ({combo['successful_games']} games)"):
                    st.metric("Average Owners", f"{combo['avg_owners']:,}")
                    st.write("**Examples:**")
                    for example in combo['examples']:
                        st.write(f"• {example}")
    
    elif analysis_type == "Pricing Sweet Spots":
        st.subheader("💰 Optimal Price Points")
        st.info("Price signals quality. Find the sweet spot for maximum revenue!")
        
        with st.spinner("Analyzing pricing..."):
            results = analyzer.analyze_pricing_sweet_spots()
        
        if results:
            import pandas as pd
            df = pd.DataFrame(results)
            
            col1, col2 = st.columns(2)
            with col1:
                st.dataframe(df, use_container_width=True, hide_index=True)
            
            with col2:
                import plotly.express as px
                fig = px.bar(
                    df,
                    x='price_range',
                    y='revenue_estimate',
                    title='Estimated Revenue by Price Range'
                )
                st.plotly_chart(fig, use_container_width=True)
    
    elif analysis_type == "Rising Trends":
        st.subheader("📈 Emerging Genre Trends")
        st.info("Catch trends early for better visibility. New releases in hot genres!")
        
        days = st.slider("Analyze last N days", 30, 180, 90, 30)
        
        with st.spinner(f"Analyzing trends from last {days} days..."):
            results = analyzer.find_rising_trends(days)
        
        if results:
            import pandas as pd
            df = pd.DataFrame(results)
            
            import plotly.express as px
            fig = px.scatter(
                df,
                x='new_releases',
                y='avg_success',
                size='momentum_score',
                text='trend',
                title='Genre Momentum (size = momentum score)',
                labels={'new_releases': 'New Releases', 'avg_success': 'Avg Success (owners)'}
            )
            st.plotly_chart(fig, use_container_width=True)
            
            st.dataframe(df, use_container_width=True, hide_index=True)
    
    elif analysis_type == "Competition Calculator":
        st.subheader("⚔️ Competition Index Calculator")
        st.info("Calculate how competitive your genre combination is!")
        
        # Tag input
        tags_input = st.text_input(
            "Enter tags (comma-separated)",
            placeholder="roguelike, platformer, pixel art"
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
            
            st.info(f"Competition Index: {result['competition_index']:.2f}")
            
            # Show similar successful games
            if st.button("Find Successful Games with These Tags"):
                similar = analyzer.find_similar_successful_games(tags)
                if similar:
                    st.subheader("🎯 Study These Successful Games")
                    for game in similar:
                        with st.expander(f"{game['name']} - {game['owners']:,} owners"):
                            st.write(f"**Tags:** {', '.join(game['tags'])}")
                            st.write(f"**Matching:** {', '.join(game['matching_tags'])}")
                            st.write(f"**Steam ID:** {game['steam_appid']}")
    
    elif analysis_type == "Market Positioning Report":
        st.subheader("📋 Comprehensive Market Report")
        st.info("Full strategic analysis for your game concept!")
        
        tags_input = st.text_input(
            "Enter your game's tags",
            placeholder="metroidvania, souls-like, indie"
        )
        
        if tags_input and st.button("Generate Report"):
            tags = [t.strip() for t in tags_input.split(',')]
            
            with st.spinner("Generating comprehensive report..."):
                report = analyzer.generate_positioning_report(tags)
            
            # Competition section
            st.markdown("### Competition Analysis")
            comp = report['competition']
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Market Size", f"{comp['total_games']:,} games")
            with col2:
                st.metric("Avg Performance", f"{comp['avg_owners']:,} owners")
            with col3:
                st.metric("Difficulty", comp['difficulty'])
            
            # Successful examples
            st.markdown("### Learn From These Games")
            examples = report['successful_examples']
            if examples:
                for game in examples[:5]:
                    st.write(f"• **{game['name']}** - {game['owners']:,} owners")
            
            # Download report
            import json
            report_json = json.dumps(report, indent=2, default=str)
            st.download_button(
                "📥 Download Full Report (JSON)",
                report_json,
                file_name=f"market_report_{'-'.join(tags)}.json",
                mime="application/json"
            )
    
    db.close()


def show_google_trends():
    """
    Display Google Trends analysis for gaming keywords with auto-loaded data.
    """
    import streamlit as st
    from src.utils.google_trends_importer import GoogleTrendsImporter
    
    st.header("📊 Google Trends Analysis")
    st.markdown("*Real-time search interest trends for gaming genres*")
    
    trends = GoogleTrendsImporter()
    
    if not trends.available:
        st.error("⚠️ pytrends library not installed")
        st.code("pip install pytrends", language="bash")
        if st.button("Install pytrends now"):
            from src.utils.google_trends_importer import install_pytrends
            with st.spinner("Installing pytrends..."):
                if install_pytrends():
                    st.success("✅ Installed! Please refresh the page.")
                else:
                    st.error("❌ Installation failed. Try manually: pip install pytrends")
        return
    
    # Auto-load default genre trends
    default_genres = ["Action", "RPG", "Strategy", "Indie", "Adventure"]
    default_timeframe = "today 12-m"
    
    # Initialize defaults
    analysis_type = "Genre Trends"
    genre_list = default_genres
    timeframe = default_timeframe
    
    # Customization in expandable section
    with st.expander("🔧 Customize Analysis", expanded=False):
        analysis_type = st.selectbox(
            "Analysis Type",
            ["Genre Trends", "Related Queries", "Keyword Comparison", "Regional Interest"],
            key="trends_analysis_type"
        )
        
        if analysis_type == "Genre Trends":
            custom_genres = st.text_input(
                "Custom genres (comma-separated, max 5)",
                placeholder="roguelike, metroidvania, souls-like, platformer, rpg",
                key="custom_genres"
            )
            custom_timeframe = st.selectbox(
                "Timeframe",
                ["today 3-m", "today 12-m", "today 5-y", "all"],
                index=1,
                key="custom_timeframe"
            )
            
            if custom_genres:
                genre_list = [g.strip() for g in custom_genres.split(',')][:5]
                timeframe = custom_timeframe
    
    # Auto-fetch and display genre trends by default
    if analysis_type == "Genre Trends":
        st.subheader("📈 Genre Search Trends")
        st.info(f"Showing trends for: {', '.join(genre_list)} (last 12 months)")
        
        with st.spinner("Fetching Google Trends data..."):
            result = trends.get_genre_trends(genre_list, timeframe)
        
        if 'error' in result:
            st.error(f"Error: {result['error']}")
            st.info("💡 Try different keywords or check your internet connection")
        else:
            import pandas as pd
            import plotly.express as px
            
            # Create comparison table
            data = []
            for keyword, stats in result['data'].items():
                data.append({
                    'Genre': keyword,
                    'Current': stats['current'],
                    'Average': stats['avg'],
                    'Peak': stats['peak'],
                    'Trend': stats['trend'],
                    '30-Day Change': stats.get('change_30d', 'N/A')
                })
            
            df = pd.DataFrame(data)
            st.dataframe(df, use_container_width=True, hide_index=True)
            
            # Visualization - Bar chart showing current vs average
            fig = px.bar(
                df,
                x='Genre',
                y=['Current', 'Average', 'Peak'],
                title='Search Interest Comparison',
                barmode='group',
                labels={'value': 'Search Interest', 'variable': 'Metric'},
                color_discrete_map={
                    'Current': '#1f77b4',
                    'Average': '#ff7f0e',
                    'Peak': '#2ca02c'
                }
            )
            fig.update_layout(
                xaxis_title="Genre",
                yaxis_title="Search Interest (0-100)",
                legend_title="Metrics",
                hovermode='x unified'
            )
            st.plotly_chart(fig, use_container_width=True)
    
    elif analysis_type == "Related Queries":
        st.subheader("🔍 Related & Rising Searches")
        
        keyword = st.text_input(
            "Enter keyword",
            placeholder="roguelike"
        )
        
        if keyword and st.button("Find Related"):
            with st.spinner("Fetching related queries..."):
                result = trends.get_related_queries(keyword)
            
            if 'error' in result:
                st.error(f"Error: {result['error']}")
            else:
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("### Top Related Queries")
                    for query in result['related']:
                        st.write(f"• {query}")
                
                with col2:
                    st.markdown("### Rising Queries")
                    for query in result['rising']:
                        st.write(f"• {query}")
    
    elif analysis_type == "Keyword Comparison":
        st.subheader("⚔️ Compare Keywords")
        
        keywords = st.text_input(
            "Enter keywords to compare (max 5)",
            placeholder="dark souls, bloodborne, elden ring, sekiro"
        )
        
        timeframe = st.selectbox(
            "Timeframe",
            ["today 1-m", "today 3-m", "today 12-m"],
            index=1
        )
        
        if keywords and st.button("Compare"):
            keyword_list = [k.strip() for k in keywords.split(',')][:5]
            
            with st.spinner("Comparing keywords..."):
                result = trends.compare_game_keywords(keyword_list, timeframe)
            
            if 'error' in result:
                st.error(f"Error: {result['error']}")
            else:
                st.success(f"🏆 Winner: **{result['most_popular']}** (Score: {result['popularity_score']})")
                
                import pandas as pd
                df = pd.DataFrame(result['comparison']).T.reset_index()
                df.columns = ['Keyword', 'Avg Interest', 'Current', 'Peak']
                st.dataframe(df, use_container_width=True, hide_index=True)
    
    elif analysis_type == "Regional Interest":
        st.subheader("🌍 Regional Search Interest")
        
        keyword = st.text_input(
            "Enter keyword",
            placeholder="indie games"
        )
        
        timeframe = st.selectbox(
            "Timeframe",
            ["today 3-m", "today 12-m", "today 5-y"],
            index=1
        )
        
        if keyword and st.button("Analyze Regions"):
            with st.spinner("Fetching regional data..."):
                result = trends.get_regional_interest(keyword, timeframe)
            
            if 'error' in result:
                st.error(f"Error: {result['error']}")
            else:
                import pandas as pd
                df = pd.DataFrame(
                    list(result['top_regions'].items()),
                    columns=['Region', 'Interest Score']
                )
                
                col1, col2 = st.columns([1, 2])
                
                with col1:
                    st.dataframe(df, use_container_width=True, hide_index=True)
                
                with col2:
                    import plotly.express as px
                    fig = px.choropleth(
                        df,
                        locations='Region',
                        locationmode='country names',
                        color='Interest Score',
                        title=f'Search Interest: {keyword}'
                    )
                    st.plotly_chart(fig, use_container_width=True)
