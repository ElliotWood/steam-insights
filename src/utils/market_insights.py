"""
Market insights from Chris Zukowski's game marketing research.
Implements features from howtomarketagame.com benchmarks.

Key Insights from Chris Zukowski (howtomarketagame.com):
- Cycle of Hit Genres: Genres go through popularity cycles
- Demo Effect: Demos increase wishlists (7K -> 42K case study)
- Wishlist Benchmarks: Diamond tier = 150K+ at launch
- Conversion Rates: 25-27% for successful games in week 1
- Rising Trends: Quick dev (10mo) can hit $367K+
- Steam Next Fest: Top tier = 10K+ wishlists gained
"""
from datetime import datetime, timedelta
from typing import Dict, List
from sqlalchemy import func, and_
from sqlalchemy.orm import Session
import logging

from src.models.database import Game, Genre, Tag, PlayerStats, PricingHistory

logger = logging.getLogger(__name__)


# Chris Zukowski Benchmarks (from howtomarketagame.com/benchmarks)
BENCHMARK_TIERS = {
    'wishlist_at_launch': {
        'bronze': 6000,
        'silver': 6000,
        'gold': 30000,
        'diamond': 150000
    },
    'weekly_wishlists': {
        'bronze': (0, 40),
        'silver': (15, 120),
        'gold': (100, 700),
        'diamond': (300, 3000)
    },
    'demo_playtime_minutes': {
        'bronze': 7,
        'silver': 18,
        'gold': 38,
        'diamond': 65
    },
    'steam_next_fest_wishlists': {
        'bronze': 999,
        'silver': 6999,
        'gold': 9999,
        'diamond': 10000
    },
    'conversion_rate': {
        'bronze': 11.93,  # $1K revenue
        'silver': 20.49,  # $10K revenue
        'gold': 25.35,    # $100K revenue
        'diamond': 27.08  # $1M revenue
    },
    'sales_per_review': {
        '2021_median': 31,
        '2020': 31,
        '2019': 36,
        '2018': 38
    }
}


class MarketInsightsAnalyzer:
    """
    Analyze Steam game data using proven market insights strategies.
    Based on Chris Zukowski's research on successful indie game marketing.
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def analyze_genre_saturation(self) -> List[Dict]:
        """
        Identify saturated vs. underserved genres.
        Key insight: Niche genres often have better visibility.
        """
        genre_stats = self.db.query(
            Genre.name,
            func.count(Game.id).label('game_count'),
            func.avg(PlayerStats.estimated_owners).label('avg_owners'),
            func.max(PlayerStats.estimated_owners).label('max_owners')
        ).join(Game.genres).join(PlayerStats).filter(
            PlayerStats.estimated_owners.isnot(None),
            PlayerStats.estimated_owners > 0
        ).group_by(Genre.name).all()
        
        results = []
        for genre_name, count, avg_owners, max_owners in genre_stats:
            # Calculate saturation score (higher = more saturated)
            saturation = count / (avg_owners or 1)
            
            results.append({
                'genre': genre_name,
                'game_count': count,
                'avg_owners': int(avg_owners or 0),
                'max_owners': int(max_owners or 0),
                'saturation_score': saturation,
                'opportunity': (
                    'Low' if saturation > 0.01 else
                    'Medium' if saturation > 0.001 else
                    'High'
                )
            })
        
        return sorted(results, key=lambda x: x['saturation_score'])
    
    def find_tag_combinations(
        self,
        min_success_rate: int = 100000
    ) -> List[Dict]:
        """
        Find successful tag combinations (genre mashups).
        Key insight: Unique tag combos help games stand out.
        """
        # Get games with multiple tags and good performance
        successful_games = self.db.query(Game).join(PlayerStats).filter(
            PlayerStats.estimated_owners >= min_success_rate
        ).all()
        
        tag_combos = {}
        for game in successful_games:
            if len(game.tags) >= 2:
                # Sort tags to ensure consistent combo keys
                tag_names = sorted([t.name for t in game.tags[:5]])
                combo_key = ' + '.join(tag_names[:3])  # Top 3 tags
                
                if combo_key not in tag_combos:
                    tag_combos[combo_key] = {
                        'tags': combo_key,
                        'games': [],
                        'total_owners': 0
                    }
                
                owners = max([s.estimated_owners for s in game.player_stats if s.estimated_owners], default=0)
                tag_combos[combo_key]['games'].append(game.name)
                tag_combos[combo_key]['total_owners'] += owners
        
        # Calculate averages and filter
        results = []
        for combo_data in tag_combos.values():
            if len(combo_data['games']) >= 2:
                results.append({
                    'tag_combination': combo_data['tags'],
                    'successful_games': len(combo_data['games']),
                    'avg_owners': combo_data['total_owners'] // len(combo_data['games']),
                    'examples': combo_data['games'][:3]
                })
        
        return sorted(results, key=lambda x: x['avg_owners'], reverse=True)[:20]
    
    def analyze_pricing_sweet_spots(self) -> List[Dict]:
        """
        Identify optimal price points by genre.
        Key insight: Price signals genre and quality expectations.
        """
        # Get games with pricing data
        price_ranges = [
            (0, 5, 'Free-$5'),
            (5, 10, '$5-$10'),
            (10, 15, '$10-$15'),
            (15, 20, '$15-$20'),
            (20, 30, '$20-$30'),
            (30, 100, '$30+')
        ]
        
        results = []
        for min_price, max_price, label in price_ranges:
            # Query games with price and owner data
            games = self.db.query(Game).join(
                PlayerStats
            ).outerjoin(
                PricingHistory
            ).filter(
                and_(
                    PricingHistory.price_usd.isnot(None),
                    PricingHistory.price_usd >= min_price,
                    PricingHistory.price_usd < max_price,
                    PlayerStats.estimated_owners > 0
                )
            ).distinct().all()
            
            if games:
                total_owners = sum([
                    max([s.estimated_owners for s in g.player_stats if s.estimated_owners], default=0)
                    for g in games
                ])
                avg_owners = total_owners // len(games) if len(games) > 0 else 0
                
                results.append({
                    'price_range': label,
                    'game_count': len(games),
                    'avg_owners': avg_owners,
                    'revenue_estimate': avg_owners * ((min_price + max_price) / 2)
                })
        
        return sorted(results, key=lambda x: x['revenue_estimate'], reverse=True)
    
    def find_rising_trends(self, days: int = 90) -> List[Dict]:
        """
        Identify genres/tags gaining momentum.
        Key insight: Ride emerging trends early for better visibility.
        """
        cutoff_date = datetime.now() - timedelta(days=days)
        
        # Get recently released games with good traction
        recent_games = self.db.query(Game).filter(
            Game.release_date >= cutoff_date
        ).join(PlayerStats).filter(
            PlayerStats.estimated_owners > 10000
        ).all()
        
        tag_momentum = {}
        for game in recent_games:
            for tag in game.tags[:3]:
                if tag.name not in tag_momentum:
                    tag_momentum[tag.name] = {
                        'tag': tag.name,
                        'new_games': 0,
                        'total_owners': 0
                    }
                
                owners = max([s.estimated_owners for s in game.player_stats if s.estimated_owners], default=0)
                tag_momentum[tag.name]['new_games'] += 1
                tag_momentum[tag.name]['total_owners'] += owners
        
        results = []
        for data in tag_momentum.values():
            if data['new_games'] >= 3:
                results.append({
                    'trend': data['tag'],
                    'new_releases': data['new_games'],
                    'avg_success': data['total_owners'] // data['new_games'],
                    'momentum_score': data['new_games'] * (data['total_owners'] // data['new_games'])
                })
        
        return sorted(results, key=lambda x: x['momentum_score'], reverse=True)[:15]
    
    def calculate_competition_index(self, tags: List[str]) -> Dict:
        """
        Calculate how competitive a genre/tag combination is.
        Key insight: Lower competition = easier to get noticed.
        """
        # Count games with these tags
        total_games = self.db.query(func.count(Game.id)).join(
            Game.tags
        ).filter(Tag.name.in_(tags)).scalar()
        
        # Get average performance
        avg_owners = self.db.query(
            func.avg(PlayerStats.estimated_owners)
        ).join(Game).join(Game.tags).filter(
            Tag.name.in_(tags),
            PlayerStats.estimated_owners > 0
        ).scalar()
        
        # Competition index: more games with lower avg success = high competition
        competition_score = total_games / (avg_owners or 1) * 100000
        
        return {
            'tags': tags,
            'total_games': total_games,
            'avg_owners': int(avg_owners or 0),
            'competition_index': competition_score,
            'difficulty': 'Very Hard' if competition_score > 100 else 
                         'Hard' if competition_score > 50 else
                         'Moderate' if competition_score > 20 else
                         'Easy'
        }
    
    def find_similar_successful_games(
        self, 
        tags: List[str], 
        min_owners: int = 50000,
        limit: int = 10
    ) -> List[Dict]:
        """
        Find successful games with similar tags for inspiration.
        Key insight: Study what worked for similar games.
        """
        games = self.db.query(Game).join(Game.tags).join(
            PlayerStats
        ).filter(
            Tag.name.in_(tags),
            PlayerStats.estimated_owners >= min_owners
        ).distinct().limit(limit).all()
        
        results = []
        for game in games:
            owners = max([s.estimated_owners for s in game.player_stats if s.estimated_owners], default=0)
            game_tags = [t.name for t in game.tags[:5]]
            
            results.append({
                'name': game.name,
                'owners': owners,
                'tags': game_tags,
                'matching_tags': [t for t in game_tags if t in tags],
                'steam_appid': game.steam_appid
            })
        
        return sorted(results, key=lambda x: x['owners'], reverse=True)
    
    def generate_positioning_report(self, proposed_tags: List[str]) -> Dict:
        """
        Generate comprehensive market positioning report.
        Combines multiple insights for strategic game planning.
        """
        return {
            'competition': self.calculate_competition_index(proposed_tags),
            'successful_examples': self.find_similar_successful_games(
                proposed_tags
            ),
            'saturation': self.analyze_genre_saturation(),
            'pricing': self.analyze_pricing_sweet_spots(),
            'timestamp': datetime.now().isoformat()
        }
    
    def calculate_revenue_projections(
        self, 
        estimated_wishlists: int,
        price: float
    ) -> Dict:
        """
        Project revenue using Chris Zukowski's conversion benchmarks.
        Based on: https://howtomarketagame.com/benchmarks/
        
        Key insights:
        - Bronze tier: 11.93% conversion ($1K revenue)
        - Silver tier: 20.49% conversion ($10K revenue)  
        - Gold tier: 25.35% conversion ($100K revenue)
        - Diamond tier: 27.08% conversion ($1M revenue)
        """
        projections = {}
        
        for tier, rate in BENCHMARK_TIERS['conversion_rate'].items():
            sales = int(estimated_wishlists * (rate / 100))
            gross_revenue = sales * price
            steam_cut = gross_revenue * 0.30
            net_revenue = gross_revenue - steam_cut
            
            projections[tier] = {
                'conversion_rate': rate,
                'estimated_sales': sales,
                'gross_revenue': round(gross_revenue, 2),
                'steam_cut': round(steam_cut, 2),
                'net_revenue': round(net_revenue, 2)
            }
        
        return {
            'wishlists': estimated_wishlists,
            'price': price,
            'projections_by_tier': projections,
            'notes': [
                'First week sales only',
                'Does not include long-tail sales',
                'Steam takes 30% cut',
                'Based on HTMAG benchmarks 2020-2025'
            ]
        }
    
    def analyze_golden_age_opportunities(
        self,
        min_owners: int = 10000,
        max_total_games: int = 1000,
        min_recent_releases: int = 3,
        lookback_days: int = 180
    ) -> List[Dict]:
        """
        Identify 'golden age' opportunities - emerging genres with 
        low competition.
        
        Based on Chris Zukowski's "Optimistic View" (Nov 2025):
        - Many genres exploding in popularity
        - Most can be made in short periods
        - Current golden age for indie games
        
        Args:
            min_owners: Minimum average owners to consider successful
            max_total_games: Maximum total games (competition threshold)
            min_recent_releases: Minimum recent releases to show activity
            lookback_days: Days to look back for "recent" releases
        """
        from sqlalchemy import case
        
        cutoff_date = datetime.now() - timedelta(days=lookback_days)
        
        # Count recent games (released in lookback period)
        recent_game_case = case(
            (Game.release_date >= cutoff_date, Game.id),
            else_=None
        )
        
        genre_stats = self.db.query(
            Genre.name,
            func.count(Game.id).label('total_games'),
            func.count(func.distinct(recent_game_case)).label('recent_games'),
            func.avg(PlayerStats.estimated_owners).label('avg_owners')
        ).join(Game.genres).join(PlayerStats).filter(
            PlayerStats.estimated_owners > min_owners
        ).group_by(Genre.name).all()
        
        opportunities = []
        for genre_name, total, recent, avg_owners in genre_stats:
            if total > 0 and avg_owners:
                # Golden Age Score: High success rate, low competition
                opportunity_score = (
                    (avg_owners / total) * (recent / total * 100)
                )
                
                if recent >= min_recent_releases and total < max_total_games:
                    opportunities.append({
                        'genre': genre_name,
                        'opportunity_score': round(opportunity_score, 2),
                        'total_games': total,
                        'recent_releases': recent,
                        'avg_owners': int(avg_owners),
                        'competition_level': (
                            'Low' if total < 100 else 
                            'Medium' if total < 500 else 
                            'High'
                        ),
                        'trend': (
                            'Growing' if recent / total > 0.1 
                            else 'Stable'
                        )
                    })
        
        return sorted(
            opportunities, 
            key=lambda x: x['opportunity_score'], 
            reverse=True
        )[:15]
    
    def calculate_demo_impact_potential(
        self, 
        current_wishlists: int
    ) -> Dict:
        """
        Estimate potential wishlist growth from releasing a demo.
        
        Based on Chris Zukowski's "Demo Effect" case study (Aug 2025):
        - Parcel Simulator: 7,000 -> 42,000 wishlists
        - 6x multiplier from successful demo
        """
        multipliers = {
            'poor_demo': 1.2,
            'average_demo': 2.5,
            'good_demo': 4.0,
            'excellent_demo': 6.0
        }
        
        projections = {}
        for quality, multiplier in multipliers.items():
            new_wishlists = int(current_wishlists * multiplier)
            gain = new_wishlists - current_wishlists
            
            projections[quality] = {
                'multiplier': multiplier,
                'projected_wishlists': new_wishlists,
                'expected_gain': gain
            }
        
        return {
            'current_wishlists': current_wishlists,
            'projections': projections,
            'recommendations': [
                'Target 30+ min playtime for gold tier demo',
                'Release demo during Steam Next Fest for max visibility',
                'Iterate based on player feedback before launch',
                'Demo can provide 2-6x wishlist multiplier'
            ]
        }
    
    def benchmark_against_tier(
        self, 
        wishlists: int,
        weekly_wishlists: int
    ) -> Dict:
        """
        Compare game performance against Chris Zukowski's benchmark tiers.
        Helps developers understand where they stand.
        """
        def get_tier(value, benchmark_dict):
            if value >= benchmark_dict['diamond']:
                return 'diamond'
            elif value >= benchmark_dict['gold']:
                return 'gold'
            elif value >= benchmark_dict['silver']:
                return 'silver'
            elif value >= benchmark_dict['bronze']:
                return 'bronze'
            return 'below_bronze'
        
        wishlist_tier = get_tier(
            wishlists, 
            BENCHMARK_TIERS['wishlist_at_launch']
        )
        
        # Find next tier target
        tier_order = ['bronze', 'silver', 'gold', 'diamond']
        next_tier_targets = {}
        
        if wishlist_tier in tier_order and wishlist_tier != 'diamond':
            next_tier_idx = tier_order.index(wishlist_tier) + 1
            next_tier = tier_order[next_tier_idx]
            target = BENCHMARK_TIERS['wishlist_at_launch'][next_tier]
            gap = target - wishlists
            
            next_tier_targets = {
                'tier': next_tier,
                'wishlists_needed': gap,
                'weeks_at_current_rate': (
                    gap // weekly_wishlists 
                    if weekly_wishlists > 0 
                    else float('inf')
                )
            }
        
        recommendations = []
        if wishlists < 30000:
            recommendations.append(
                'Aim for 30K+ wishlists for gold tier (25%+ conversion)'
            )
        if weekly_wishlists < 100:
            recommendations.append(
                'Increase marketing - target 100+ weekly wishlists'
            )
        
        return {
            'wishlist_tier': wishlist_tier,
            'current_metrics': {
                'total_wishlists': wishlists,
                'weekly_wishlists': weekly_wishlists
            },
            'next_tier_targets': next_tier_targets,
            'recommendations': recommendations
        }
    
    def estimate_review_count(self, projected_sales: int) -> Dict:
        """
        Estimate number of reviews based on Boxleiter number.
        
        From Chris Zukowski benchmarks:
        - 2021 median: 31 sales per review
        - Trend: Decreasing over time (was 79 in 2013-2017)
        """
        boxleiter = BENCHMARK_TIERS['sales_per_review']
        current_ratio = boxleiter['2021_median']
        estimated_reviews = projected_sales // current_ratio
        
        return {
            'projected_sales': projected_sales,
            'estimated_reviews': estimated_reviews,
            'sales_per_review_ratio': current_ratio,
            'notes': [
                'Boxleiter number declining over time',
                '2021 median: 31 sales per review',
                'Actual ratio varies by genre and quality'
            ]
        }
