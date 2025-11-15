"""
Google Trends integration for video game search data.
Tracks game genre and keyword popularity over time.
"""
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class GoogleTrendsImporter:
    """
    Import Google Trends data for gaming keywords and genres.
    Note: This requires the pytrends library (pip install pytrends)
    """
    
    def __init__(self):
        try:
            from pytrends.request import TrendReq
            self.pytrends = TrendReq(hl='en-US', tz=360)
            self.available = True
        except ImportError:
            logger.warning(
                "pytrends not installed. Run: pip install pytrends"
            )
            self.available = False
    
    def get_genre_trends(
        self, 
        genres: List[str],
        timeframe: str = 'today 12-m'
    ) -> Dict:
        """
        Get search interest trends for game genres.
        
        Args:
            genres: List of genre keywords (e.g., ['roguelike', 'metroidvania'])
            timeframe: Google Trends timeframe (default: past 12 months)
        
        Returns:
            Dictionary with trend data and insights
        """
        if not self.available:
            return {'error': 'pytrends not installed'}
        
        try:
            # Build payload (max 5 keywords at a time)
            keywords = genres[:5]
            self.pytrends.build_payload(
                keywords,
                cat=0,  # All categories
                timeframe=timeframe,
                geo='',  # Worldwide
                gprop=''  # Web search (empty string for web)
            )
            
            # Get interest over time
            interest_df = self.pytrends.interest_over_time()
            
            if interest_df.empty:
                return {'error': 'No data available for these keywords'}
            
            # Calculate trends
            results = {
                'timeframe': timeframe,
                'keywords': keywords,
                'data': {}
            }
            
            for keyword in keywords:
                if keyword in interest_df.columns:
                    series = interest_df[keyword]
                    results['data'][keyword] = {
                        'current': int(series.iloc[-1]),
                        'avg': int(series.mean()),
                        'peak': int(series.max()),
                        'trend': 'Rising' if series.iloc[-1] > series.mean() else 'Falling',
                        'change_30d': int(series.iloc[-1] - series.iloc[-30]) if len(series) >= 30 else 0
                    }
            
            return results
            
        except Exception as e:
            logger.error(f"Failed to fetch Google Trends: {e}")
            return {'error': str(e)}
    
    def get_related_queries(self, keyword: str) -> Dict:
        """
        Get related and rising search queries for a keyword.
        
        Args:
            keyword: Gaming keyword to analyze
        
        Returns:
            Dictionary with related and rising queries
        """
        if not self.available:
            return {'error': 'pytrends not installed'}
        
        try:
            self.pytrends.build_payload([keyword], timeframe='today 12-m')
            related = self.pytrends.related_queries()
            
            if keyword not in related:
                return {'error': 'No related queries found'}
            
            result = {
                'keyword': keyword,
                'related': [],
                'rising': []
            }
            
            # Parse related queries
            if related[keyword]['top'] is not None:
                result['related'] = related[keyword]['top']['query'].head(10).tolist()
            
            # Parse rising queries
            if related[keyword]['rising'] is not None:
                result['rising'] = related[keyword]['rising']['query'].head(10).tolist()
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to fetch related queries: {e}")
            return {'error': str(e)}
    
    def compare_game_keywords(
        self,
        keywords: List[str],
        timeframe: str = 'today 3-m'
    ) -> Dict:
        """
        Compare search interest between multiple game-related keywords.
        
        Args:
            keywords: List of keywords to compare (max 5)
            timeframe: Time period to analyze
        
        Returns:
            Comparison data with winner and insights
        """
        if not self.available:
            return {'error': 'pytrends not installed'}
        
        try:
            keywords = keywords[:5]
            self.pytrends.build_payload(keywords, timeframe=timeframe)
            interest_df = self.pytrends.interest_over_time()
            
            if interest_df.empty:
                return {'error': 'No comparison data available'}
            
            # Calculate averages
            comparison = {}
            for keyword in keywords:
                if keyword in interest_df.columns:
                    avg_interest = interest_df[keyword].mean()
                    comparison[keyword] = {
                        'avg_interest': int(avg_interest),
                        'current': int(interest_df[keyword].iloc[-1]),
                        'peak': int(interest_df[keyword].max())
                    }
            
            # Find winner
            winner = max(comparison.items(), key=lambda x: x[1]['avg_interest'])
            
            return {
                'timeframe': timeframe,
                'comparison': comparison,
                'most_popular': winner[0],
                'popularity_score': winner[1]['avg_interest']
            }
            
        except Exception as e:
            logger.error(f"Failed to compare keywords: {e}")
            return {'error': str(e)}
    
    def get_regional_interest(
        self,
        keyword: str,
        timeframe: str = 'today 12-m'
    ) -> Dict:
        """
        Get regional breakdown of search interest.
        
        Args:
            keyword: Gaming keyword
            timeframe: Time period
        
        Returns:
            Regional interest data
        """
        if not self.available:
            return {'error': 'pytrends not installed'}
        
        try:
            self.pytrends.build_payload([keyword], timeframe=timeframe)
            regional_df = self.pytrends.interest_by_region(
                resolution='COUNTRY',
                inc_low_vol=False
            )
            
            if regional_df.empty:
                return {'error': 'No regional data available'}
            
            # Get top regions
            top_regions = regional_df[keyword].nlargest(20)
            
            return {
                'keyword': keyword,
                'timeframe': timeframe,
                'top_regions': {
                    region: int(score) 
                    for region, score in top_regions.items()
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to fetch regional data: {e}")
            return {'error': str(e)}


def install_pytrends():
    """Helper function to install pytrends if needed."""
    import subprocess
    import sys
    
    try:
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "pytrends"]
        )
        return True
    except Exception as e:
        logger.error(f"Failed to install pytrends: {e}")
        return False
