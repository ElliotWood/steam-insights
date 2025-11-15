"""
Streamlit dashboard for Steam Insights.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from src.database.connection import get_db, init_db
from src.models.database import Game, Genre, PlayerStats, PricingHistory
from src.api.steam_client import SteamAPIClient
from src.etl.game_importer import GameDataImporter

# Page configuration
st.set_page_config(
    page_title="Steam Insights Dashboard",
    page_icon="🎮",
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
    st.title("🎮 Steam Insights Dashboard")
    st.markdown("---")
    
    # Sidebar
    with st.sidebar:
        st.header("Navigation")
        page = st.radio(
            "Select a page:",
            ["Overview", "Game Search", "Analytics", "Market Analysis", "Data Management"]
        )
        
        st.markdown("---")
        st.markdown("### About")
        st.info(
            "Steam Insights provides analytics and insights "
            "for Steam games, including player counts, pricing history, "
            "genre analysis, and market overlap analysis."
        )
    
    # Route to different pages
    if page == "Overview":
        show_overview()
    elif page == "Game Search":
        show_game_search()
    elif page == "Analytics":
        show_analytics()
    elif page == "Market Analysis":
        show_market_analysis()
    elif page == "Data Management":
        show_data_management()


def show_overview():
    """Show overview page with key statistics."""
    st.header("Overview")
    
    db = get_session()
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_games = db.query(Game).count()
        st.metric("Total Games", f"{total_games:,}")
    
    with col2:
        total_genres = db.query(Genre).count()
        st.metric("Genres", f"{total_genres:,}")
    
    with col3:
        recent_stats = db.query(PlayerStats).filter(
            PlayerStats.timestamp >= datetime.utcnow() - timedelta(hours=24)
        ).count()
        st.metric("Recent Updates (24h)", f"{recent_stats:,}")
    
    with col4:
        avg_players = db.query(PlayerStats).filter(
            PlayerStats.timestamp >= datetime.utcnow() - timedelta(hours=1)
        ).with_entities(
            db.func.avg(PlayerStats.current_players)
        ).scalar()
        st.metric("Avg Current Players", f"{int(avg_players or 0):,}")
    
    st.markdown("---")
    
    # Top genres
    st.subheader("Top Genres by Game Count")
    
    genre_counts = db.query(
        Genre.name,
        db.func.count(Game.id).label('count')
    ).join(Genre.games).group_by(Genre.name).order_by(
        db.func.count(Game.id).desc()
    ).limit(10).all()
    
    if genre_counts:
        df_genres = pd.DataFrame(genre_counts, columns=['Genre', 'Game Count'])
        fig = px.bar(df_genres, x='Genre', y='Game Count', color='Game Count')
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No genre data available yet. Import some games first!")
    
    # Recently added games
    st.subheader("Recently Added Games")
    
    recent_games = db.query(Game).order_by(
        Game.created_at.desc()
    ).limit(10).all()
    
    if recent_games:
        games_data = []
        for game in recent_games:
            games_data.append({
                'Name': game.name,
                'Developer': game.developer or 'Unknown',
                'Release Date': game.release_date.strftime('%Y-%m-%d') if game.release_date else 'N/A',
                'Added': game.created_at.strftime('%Y-%m-%d %H:%M')
            })
        
        df_recent = pd.DataFrame(games_data)
        st.dataframe(df_recent, use_container_width=True)
    else:
        st.info("No games in database yet. Import some games to get started!")
    
    db.close()


def show_game_search():
    """Show game search and details page."""
    st.header("Game Search")
    
    db = get_session()
    
    # Search input
    search_term = st.text_input("Search for a game:", placeholder="Enter game name...")
    
    if search_term:
        games = db.query(Game).filter(
            Game.name.ilike(f"%{search_term}%")
        ).limit(20).all()
        
        if games:
            st.write(f"Found {len(games)} game(s)")
            
            # Display games
            for game in games:
                with st.expander(f"🎮 {game.name}"):
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.write(f"**Developer:** {game.developer or 'Unknown'}")
                        st.write(f"**Publisher:** {game.publisher or 'Unknown'}")
                        st.write(f"**Release Date:** {game.release_date.strftime('%Y-%m-%d') if game.release_date else 'N/A'}")
                        st.write(f"**Steam App ID:** {game.steam_appid}")
                        
                        if game.short_description:
                            st.write("**Description:**")
                            st.write(game.short_description)
                        
                        if game.genres:
                            genres = [g.name for g in game.genres]
                            st.write(f"**Genres:** {', '.join(genres)}")
                    
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
                    stats = db.query(PlayerStats).filter(
                        PlayerStats.game_id == game.id,
                        PlayerStats.timestamp >= datetime.utcnow() - timedelta(days=30)
                    ).order_by(PlayerStats.timestamp).all()
                    
                    if stats:
                        st.write("**Player Count (Last 30 Days)**")
                        df_stats = pd.DataFrame([
                            {'Date': s.timestamp, 'Players': s.current_players}
                            for s in stats
                        ])
                        fig = px.line(df_stats, x='Date', y='Players')
                        st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning(f"No games found matching '{search_term}'")
    
    db.close()


def show_analytics():
    """Show analytics page with charts and insights."""
    st.header("Analytics")
    
    db = get_session()
    
    # Time range selector
    time_range = st.selectbox(
        "Select time range:",
        ["Last 24 Hours", "Last 7 Days", "Last 30 Days", "Last 90 Days"]
    )
    
    days_map = {
        "Last 24 Hours": 1,
        "Last 7 Days": 7,
        "Last 30 Days": 30,
        "Last 90 Days": 90
    }
    days = days_map[time_range]
    
    since = datetime.utcnow() - timedelta(days=days)
    
    # Most active games
    st.subheader("Most Active Games")
    
    active_games = db.query(
        Game.name,
        db.func.max(PlayerStats.current_players).label('max_players'),
        db.func.avg(PlayerStats.current_players).label('avg_players')
    ).join(PlayerStats).filter(
        PlayerStats.timestamp >= since
    ).group_by(Game.name).order_by(
        db.func.max(PlayerStats.current_players).desc()
    ).limit(15).all()
    
    if active_games:
        df_active = pd.DataFrame(
            active_games,
            columns=['Game', 'Peak Players', 'Avg Players']
        )
        df_active['Peak Players'] = df_active['Peak Players'].astype(int)
        df_active['Avg Players'] = df_active['Avg Players'].astype(int)
        
        fig = px.bar(
            df_active,
            x='Game',
            y=['Peak Players', 'Avg Players'],
            barmode='group',
            title=f"Top 15 Games by Player Count ({time_range})"
        )
        fig.update_xaxis(tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No player statistics available for the selected time range.")
    
    db.close()


def show_market_analysis():
    """Show market analysis page for game ownership overlap."""
    st.header("Market Analysis - Game Ownership Overlap")
    
    st.markdown("""
    Analyze the overlap between game audiences to determine addressable markets 
    when combining different game types or genres.
    """)
    
    db = get_session()
    
    # Get all games with ownership data
    games_with_owners = db.query(
        Game.id,
        Game.name,
        Game.steam_appid,
        db.func.max(PlayerStats.estimated_owners).label('owners')
    ).join(PlayerStats).filter(
        PlayerStats.estimated_owners.isnot(None)
    ).group_by(Game.id, Game.name, Game.steam_appid).order_by(
        Game.name
    ).all()
    
    if not games_with_owners or len(games_with_owners) < 2:
        st.warning(
            "⚠️ Not enough games with ownership data. "
            "Import games and ensure they have player statistics with estimated_owners populated."
        )
        st.info(
            "💡 Tip: The estimated_owners field tracks how many users own each game. "
            "This data is typically available from SteamSpy or similar services."
        )
        db.close()
        return
    
    st.markdown("---")
    
    # Game selection for comparison
    st.subheader("📊 Select Games to Compare")
    
    col1, col2 = st.columns(2)
    
    game_options = {f"{g.name} ({g.owners:,} owners)": g for g in games_with_owners}
    
    with col1:
        game1_name = st.selectbox(
            "Game A:",
            options=list(game_options.keys()),
            help="Select the first game"
        )
        game1 = game_options[game1_name]
    
    with col2:
        # Filter out the first game from second selection
        game2_options = {k: v for k, v in game_options.items() if v.id != game1.id}
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
        options=[k for k, v in game_options.items() if v.id not in [game1.id, game2.id]],
        help="Select additional games to include in the analysis"
    )
    
    # Build list of all selected games
    selected_games = [game1, game2]
    for game_name in additional_games:
        selected_games.append(game_options[game_name])
    
    st.markdown("---")
    
    # Market overlap analysis
    st.subheader("🎯 Market Overlap Analysis")
    
    # Calculate overlap estimates
    # Note: Since we don't have actual user-level data, we estimate overlap
    # based on genre similarity and market penetration
    
    # Get genres for each game
    game_genres = {}
    for game in selected_games:
        game_obj = db.query(Game).filter(Game.id == game.id).first()
        game_genres[game.id] = [g.name for g in game_obj.genres]
    
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
            if game.id in game_genres and game_genres[game.id]:
                st.caption(f"Genres: {', '.join(game_genres[game.id][:3])}")
    
    st.markdown("---")
    
    # Two-game comparison
    if len(selected_games) == 2:
        st.markdown("### 🔄 Ownership Overlap (2-Game Analysis)")
        
        overlap_factor = calculate_overlap_factor(game1.id, game2.id)
        
        # Estimate overlap
        smaller_audience = min(game1.owners, game2.owners)
        estimated_overlap = int(smaller_audience * overlap_factor)
        
        # Addressable market (people who own one but not the other)
        addressable_for_game1 = game2.owners - estimated_overlap
        addressable_for_game2 = game1.owners - estimated_overlap
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "Estimated Overlap",
                f"{estimated_overlap:,}",
                help=f"Users estimated to own both games (~{overlap_factor*100:.1f}% of smaller audience)"
            )
        
        with col2:
            st.metric(
                f"Addressable from {game1.name}",
                f"{addressable_for_game1:,}",
                help=f"Users who own {game1.name} but not {game2.name}"
            )
        
        with col3:
            st.metric(
                f"Addressable from {game2.name}",
                f"{addressable_for_game2:,}",
                help=f"Users who own {game2.name} but not {game1.name}"
            )
        
        # Visualization
        st.markdown("### 📊 Overlap Visualization")
        
        # Create a simple overlap visualization
        fig = go.Figure()
        
        # Create overlapping circles representation
        fig.add_trace(go.Bar(
            x=[game1.name, 'Overlap', game2.name],
            y=[addressable_for_game2, estimated_overlap, addressable_for_game1],
            marker_color=['#636EFA', '#EF553B', '#00CC96'],
            text=[f"{addressable_for_game2:,}", f"{estimated_overlap:,}", f"{addressable_for_game1:,}"],
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
        
        st.info(f"""
        **Combined Addressable Market**: {total_combined:,} unique owners
        
        **Overlap Analysis**:
        - {overlap_pct:.1f}% of {game1.name if game1.owners < game2.owners else game2.name} owners also own the other game
        - If you create a game combining elements of both, you have a potential market of {total_combined:,} users
        - {addressable_for_game1:,} users familiar with {game1.name} might be interested in content similar to {game2.name}
        - {addressable_for_game2:,} users familiar with {game2.name} might be interested in content similar to {game1.name}
        """)
        
    else:
        # Multi-game comparison
        st.markdown(f"### 🔄 Multi-Game Overlap ({len(selected_games)} Games)")
        
        st.info(
            "💡 Multi-game overlap analysis estimates the intersection of audiences "
            "across multiple games. The more games you add, the smaller the overlap typically becomes."
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
        
        # Conservative estimate: assume some overlap between all games
        total_owners = sum(g.owners for g in selected_games)
        # Assume average 20% overlap reduction for multi-game scenario
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
        
        st.info(f"""
        **Market Opportunity**: Creating a game that combines elements from these {len(selected_games)} games 
        could address an estimated market of **{estimated_unique:,}** unique users.
        """)
    
    # Additional insights
    st.markdown("---")
    st.markdown("### ℹ️ About This Analysis")
    st.caption("""
    **Methodology**: This analysis estimates ownership overlap based on genre similarity and market data. 
    Actual overlap may vary based on factors like:
    - Player preferences and gaming habits
    - Game popularity and release timing  
    - Marketing and discoverability
    - Genre and gameplay mechanics
    
    **Note**: These are estimates based on available data. For precise market research, 
    consider conducting user surveys or accessing detailed analytics platforms.
    """)
    
    db.close()


def show_data_management():
    """Show data management page for importing games."""
    st.header("Data Management")
    
    st.write("Import games from Steam to populate the database.")
    
    # Import single game
    st.subheader("Import Single Game")
    
    app_id = st.number_input(
        "Enter Steam App ID:",
        min_value=1,
        step=1,
        help="You can find the App ID in the Steam store URL"
    )
    
    if st.button("Import Game"):
        with st.spinner(f"Importing game {app_id}..."):
            db = get_session()
            importer = GameDataImporter(db)
            
            try:
                game = importer.import_game(app_id)
                if game:
                    st.success(f"✅ Successfully imported: {game.name}")
                    
                    # Also try to import player stats
                    stats = importer.update_player_stats(app_id)
                    if stats:
                        st.info(f"Current players: {stats.current_players}")
                else:
                    st.error("Failed to import game. Check the App ID and try again.")
            except Exception as e:
                st.error(f"Error: {str(e)}")
            finally:
                db.close()
    
    st.markdown("---")
    
    # Popular game suggestions
    st.subheader("Popular Games to Import")
    st.write("Try importing these popular games:")
    
    popular_games = [
        ("Counter-Strike 2", 730),
        ("Dota 2", 570),
        ("Team Fortress 2", 440),
        ("Rust", 252490),
        ("Apex Legends", 1172470),
        ("Grand Theft Auto V", 271590),
    ]
    
    cols = st.columns(3)
    for idx, (name, appid) in enumerate(popular_games):
        with cols[idx % 3]:
            if st.button(f"Import {name}", key=f"popular_{appid}"):
                with st.spinner(f"Importing {name}..."):
                    db = get_session()
                    importer = GameDataImporter(db)
                    
                    try:
                        game = importer.import_game(appid)
                        if game:
                            st.success(f"✅ Imported: {game.name}")
                        else:
                            st.error("Failed to import game")
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
                    finally:
                        db.close()


if __name__ == "__main__":
    main()
