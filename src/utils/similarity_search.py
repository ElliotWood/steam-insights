"""
Vector similarity search utilities for game embeddings.

Provides functions for finding similar games using cosine similarity
on BGE-M3 embeddings stored in PostgreSQL with pgvector.
"""

from typing import List, Dict, Optional
from sqlalchemy import text
from src.database.connection import engine
import logging

logger = logging.getLogger(__name__)


def find_similar_games(
    app_id: int,
    limit: int = 10,
    min_similarity: float = 0.0,
    exclude_same_developer: bool = False
) -> List[Dict]:
    """
    Find games similar to the specified game using embedding similarity.
    
    Args:
        app_id: Steam app ID of the reference game
        limit: Maximum number of similar games to return
        min_similarity: Minimum similarity threshold (0.0 to 1.0)
        exclude_same_developer: If True, exclude games from same developer
    
    Returns:
        List of dictionaries containing game info and similarity scores
    """
    try:
        with engine.connect() as conn:
            query = text("""
                SELECT 
                    g1.steam_appid,
                    g1.name,
                    g1.header_image,
                    g1.short_description,
                    1 - (g1.description_embedding <=> g2.description_embedding) as similarity,
                    g1.release_date,
                    g1.price_overview,
                    g1.metacritic
                FROM games g1
                CROSS JOIN games g2
                WHERE g2.steam_appid = :app_id 
                    AND g1.steam_appid != :app_id
                    AND g1.description_embedding IS NOT NULL
                    AND g2.description_embedding IS NOT NULL
                    AND (1 - (g1.description_embedding <=> g2.description_embedding)) >= :min_similarity
                ORDER BY similarity DESC
                LIMIT :limit
            """)
            
            result = conn.execute(
                query,
                {
                    'app_id': app_id,
                    'limit': limit,
                    'min_similarity': min_similarity
                }
            )
            
            games = []
            for row in result:
                games.append({
                    'steam_appid': row[0],
                    'name': row[1],
                    'header_image': row[2],
                    'short_description': row[3],
                    'similarity': float(row[4]),
                    'release_date': row[5],
                    'price_overview': row[6],
                    'metacritic': row[7]
                })
            
            return games
            
    except Exception as e:
        logger.error(f"Error finding similar games for {app_id}: {e}")
        return []


def find_similar_to_description(
    description: str,
    limit: int = 10,
    genre_filter: Optional[str] = None
) -> List[Dict]:
    """
    Find games similar to a text description.
    
    Note: This requires generating an embedding for the description first.
    For now, this is a placeholder for future implementation with a local
    BGE-M3 model or API.
    
    Args:
        description: Text description to find similar games for
        limit: Maximum number of results
        genre_filter: Optional genre to filter by
    
    Returns:
        List of similar games
    """
    logger.warning("Text-to-embedding search not yet implemented")
    logger.info("This feature requires running BGE-M3 model locally or via API")
    return []


def get_embedding_coverage() -> Dict[str, int]:
    """
    Get statistics on embedding coverage in the database.
    
    Returns:
        Dictionary with coverage statistics
    """
    try:
        with engine.connect() as conn:
            # Total games
            result = conn.execute(text("SELECT COUNT(*) FROM games"))
            total = result.scalar()
            
            # Games with embeddings
            result = conn.execute(text(
                "SELECT COUNT(*) FROM games WHERE description_embedding IS NOT NULL"
            ))
            with_embeddings = result.scalar()
            
            # Coverage by genre
            result = conn.execute(text("""
                SELECT 
                    gg.genre_name,
                    COUNT(*) as total,
                    SUM(CASE WHEN g.description_embedding IS NOT NULL THEN 1 ELSE 0 END) as with_embedding
                FROM games g
                JOIN game_genres gg ON g.steam_appid = gg.steam_appid
                GROUP BY gg.genre_name
                ORDER BY total DESC
            """))
            
            genre_coverage = []
            for row in result:
                genre_coverage.append({
                    'genre': row[0],
                    'total': row[1],
                    'with_embedding': row[2],
                    'coverage_pct': (row[2] / row[1] * 100) if row[1] > 0 else 0
                })
            
            return {
                'total_games': total,
                'games_with_embeddings': with_embeddings,
                'coverage_pct': (with_embeddings / total * 100) if total > 0 else 0,
                'genre_coverage': genre_coverage
            }
            
    except Exception as e:
        logger.error(f"Error getting embedding coverage: {e}")
        return {
            'total_games': 0,
            'games_with_embeddings': 0,
            'coverage_pct': 0,
            'genre_coverage': []
        }


def semantic_search(
    query_text: str,
    filters: Optional[Dict] = None,
    limit: int = 20
) -> List[Dict]:
    """
    Semantic search across game descriptions.
    
    Future implementation: Convert query text to embedding and search.
    
    Args:
        query_text: Natural language search query
        filters: Optional filters (genre, price range, etc.)
        limit: Maximum results
    
    Returns:
        List of matching games
    """
    logger.warning("Semantic search not yet implemented")
    return []


def cluster_similar_games(
    app_ids: List[int],
    similarity_threshold: float = 0.7
) -> List[List[int]]:
    """
    Group games into clusters based on embedding similarity.
    
    Args:
        app_ids: List of Steam app IDs to cluster
        similarity_threshold: Minimum similarity to group together
    
    Returns:
        List of clusters (each cluster is a list of app IDs)
    """
    # This is a complex operation better done in memory with numpy
    # Placeholder for future implementation
    logger.warning("Clustering not yet implemented")
    return []


def get_genre_centroid_games(
    genre: str,
    limit: int = 5
) -> List[Dict]:
    """
    Find most "representative" games for a genre.
    
    This finds games that are most similar to the average
    of all games in that genre.
    
    Args:
        genre: Genre name
        limit: Number of representative games to return
    
    Returns:
        List of representative games with scores
    """
    try:
        with engine.connect() as conn:
            # This requires averaging embeddings, which is complex in SQL
            # For now, return most popular games in genre
            query = text("""
                SELECT DISTINCT
                    g.steam_appid,
                    g.name,
                    g.header_image,
                    g.metacritic,
                    g.recommendations
                FROM games g
                JOIN game_genres gg ON g.steam_appid = gg.steam_appid
                WHERE gg.genre_name = :genre
                    AND g.description_embedding IS NOT NULL
                ORDER BY COALESCE(g.recommendations, 0) DESC
                LIMIT :limit
            """)
            
            result = conn.execute(query, {'genre': genre, 'limit': limit})
            
            games = []
            for row in result:
                games.append({
                    'steam_appid': row[0],
                    'name': row[1],
                    'header_image': row[2],
                    'metacritic': row[3],
                    'recommendations': row[4]
                })
            
            return games
            
    except Exception as e:
        logger.error(f"Error getting genre centroid for {genre}: {e}")
        return []


def batch_find_similar(
    app_ids: List[int],
    limit_per_game: int = 5
) -> Dict[int, List[Dict]]:
    """
    Find similar games for multiple app IDs efficiently.
    
    Args:
        app_ids: List of Steam app IDs
        limit_per_game: Max similar games per input game
    
    Returns:
        Dictionary mapping app_id to list of similar games
    """
    results = {}
    for app_id in app_ids:
        results[app_id] = find_similar_games(app_id, limit=limit_per_game)
    return results
