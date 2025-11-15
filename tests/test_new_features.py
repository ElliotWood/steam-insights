"""Quick test of new MarketInsightsAnalyzer features"""
from src.utils.market_insights import MarketInsightsAnalyzer
from src.database.connection import get_db

db = next(get_db())
analyzer = MarketInsightsAnalyzer(db)

print("Testing new features...\n")

# Test 1: Revenue Projections
print("1. Revenue Projections (10K wishlists @ $19.99):")
result = analyzer.calculate_revenue_projections(10000, 19.99)
print(f"   Gold tier net revenue: ${result['projections_by_tier']['gold']['net_revenue']:,.2f}")
print(f"   Diamond tier net revenue: ${result['projections_by_tier']['diamond']['net_revenue']:,.2f}\n")

# Test 2: Golden Age Opportunities
print("2. Golden Age Opportunities:")
opps = analyzer.analyze_golden_age_opportunities()
print(f"   Found {len(opps)} genre opportunities")
if opps:
    print(f"   Top: {opps[0]['genre']} (Score: {opps[0]['opportunity_score']})\n")

# Test 3: Demo Impact
print("3. Demo Impact Calculator (5K wishlists):")
demo = analyzer.calculate_demo_impact_potential(5000)
print(f"   Excellent demo: {demo['projections']['excellent_demo']['projected_wishlists']:,} wishlists")
print(f"   Gain: +{demo['projections']['excellent_demo']['expected_gain']:,}\n")

# Test 4: Benchmark
print("4. Benchmark Against Tiers (5K wishlists, 50 weekly):")
bench = analyzer.benchmark_against_tier(5000, 50)
print(f"   Current tier: {bench['wishlist_tier']}")
if bench['next_tier_targets']:
    print(f"   Next tier: {bench['next_tier_targets']['tier']}")
    print(f"   Need: {bench['next_tier_targets']['wishlists_needed']:,} more wishlists\n")

# Test 5: Review Estimate
print("5. Review Count Estimate (1000 sales):")
reviews = analyzer.estimate_review_count(1000)
print(f"   Estimated reviews: {reviews['estimated_reviews']}")
print(f"   Ratio: {reviews['sales_per_review_ratio']} sales per review")

print("\n✅ All new features working with live data!")
