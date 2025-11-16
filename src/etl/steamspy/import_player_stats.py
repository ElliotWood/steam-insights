"""
SteamSpy API - Player Stats Enrichment
Imports player statistics from SteamSpy to enrich database.

Target: 80,000+ games with player stats
Rate Limit: 4 requests/second
Execution Time: ~6 hours
"""
import time
import requests
from datetime import datetime
from sqlalchemy import text
from src.database.connection import SessionLocal


class SteamSpyImporter:
    """Import player stats from SteamSpy API."""
    
    def __init__(self):
        self.base_url = "https://steamspy.com/api.php"
        self.rate_limit = 0.25  # 4 req/sec = 0.25 seconds between
        self.batch_size = 1000
        self.session = SessionLocal()
        
    def get_game_stats(self, appid):
        """Fetch stats for a single game from SteamSpy."""
        try:
            response = requests.get(
                self.base_url,
                params={'request': 'appdetails', 'appid': appid},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Check if we got valid data
                if 'appid' in data and data.get('appid') != 0:
                    return {
                        'steam_appid': int(data['appid']),
                        'estimated_owners': self._parse_owners(
                            data.get('owners', '0')
                        ),
                        'peak_players_24h': data.get('ccu', 0),
                        'current_players': data.get('players_forever', 0),
                        'average_playtime': data.get('average_forever', 0),
                        'median_playtime': data.get('median_forever', 0),
                        'positive_reviews': data.get('positive', 0),
                        'negative_reviews': data.get('negative', 0),
                        'timestamp': datetime.now()
                    }
                    
            return None
            
        except Exception as e:
            print(f"    Error fetching {appid}: {e}")
            return None
    
    def _parse_owners(self, owners_str):
        """
        Parse owner string like '20000 .. 50000' to midpoint.
        """
        try:
            if '..' in owners_str:
                low, high = owners_str.split('..')
                low = int(low.strip().replace(',', ''))
                high = int(high.strip().replace(',', ''))
                return (low + high) // 2
            else:
                return int(owners_str.replace(',', ''))
        except:
            return 0
    
    def get_games_needing_stats(self, limit=None):
        """Get games that don't have recent player stats."""
        query = text("""
            SELECT g.steam_appid, g.name
            FROM games g
            LEFT JOIN player_stats ps ON g.steam_appid = ps.steam_appid
            WHERE ps.steam_appid IS NULL
            ORDER BY g.steam_appid
        """)
        
        if limit:
            query = text(f"""
                SELECT g.steam_appid, g.name
                FROM games g
                LEFT JOIN player_stats ps ON g.steam_appid = ps.steam_appid
                WHERE ps.steam_appid IS NULL
                ORDER BY g.steam_appid
                LIMIT {limit}
            """)
        
        result = self.session.execute(query).fetchall()
        return [(row[0], row[1]) for row in result]
    
    def insert_player_stats(self, stats_list):
        """Insert player stats ONE AT A TIME for fault tolerance."""
        if not stats_list:
            return 0
        
        inserted = 0
        for stats in stats_list:
            try:
                # Simple insert - no conflict handling
                insert_sql = text("""
                    INSERT INTO player_stats (
                        steam_appid, timestamp, current_players,
                        peak_players_24h, average_playtime_minutes,
                        peak_playtime_minutes, estimated_owners,
                        estimated_revenue
                    )
                    VALUES (
                        :appid, :ts, :curr, :peak24, :avg_time,
                        :peak_time, :owners, NULL
                    )
                """)
                
                self.session.execute(insert_sql, {
                    'appid': stats['steam_appid'],
                    'ts': stats['timestamp'],
                    'curr': stats['current_players'],
                    'peak24': stats['peak_players_24h'],
                    'avg_time': stats['average_playtime'],
                    'peak_time': stats['median_playtime'],
                    'owners': stats['estimated_owners']
                })
                self.session.commit()
                inserted += 1
                
            except Exception as e:
                # Skip duplicates silently
                if 'duplicate' not in str(e).lower():
                    print(f"  Error inserting {stats['steam_appid']}: {e}")
                self.session.rollback()
                continue
        
        return inserted
    
    def run_import(self, max_games=None, resume_from=None):
        """
        Run the import process with fault tolerance.
        
        Args:
            max_games: Maximum number of games to process (for testing)
            resume_from: Steam AppID to resume from
        """
        print("=== SteamSpy Player Stats Import ===\n")
        
        # Get games needing stats
        print("Loading games...")
        games = self.get_games_needing_stats(limit=max_games)
        
        if resume_from:
            games = [(aid, name) for aid, name in games if aid >= resume_from]
        
        total_games = len(games)
        print(f"Games to process: {total_games:,}\n")
        
        if total_games == 0:
            print("No games need stats!")
            return
        
        # Calculate time estimate
        est_time = (total_games * self.rate_limit) / 3600
        print(f"Estimated time: {est_time:.1f} hours")
        print(f"Rate: {1/self.rate_limit:.1f} requests/second\n")
        
        # Auto-start for automation
        print("Starting import automatically...\n")
        
        # Process with small batches and commit each one
        processed = 0
        inserted = 0
        batch_stats = []
        batch_size = 50  # Smaller batches for fault tolerance
        start_time = time.time()
        
        for i, (appid, name) in enumerate(games, 1):
            try:
                # Fetch stats
                stats = self.get_game_stats(appid)
                
                if stats:
                    batch_stats.append(stats)
                
                # Rate limiting
                time.sleep(self.rate_limit)
                
                # Insert small batch frequently for fault tolerance
                if len(batch_stats) >= batch_size or i == total_games:
                    inserted += self.insert_player_stats(batch_stats)
                    batch_stats = []
                
                processed += 1
                
                # Progress update every 100 games
                if processed % 100 == 0 or processed == total_games:
                    elapsed = time.time() - start_time
                    rate = processed / elapsed if elapsed > 0 else 0
                    remaining = ((total_games - processed) / rate / 3600) if rate > 0 else 0
                    
                    print(
                        f"Processed {processed:,}/{total_games:,} "
                        f"({processed/total_games*100:.1f}%) | "
                        f"Inserted: {inserted:,} | "
                        f"Last: {appid} | "
                        f"ETA: {remaining:.1f}h"
                    )
                    
            except KeyboardInterrupt:
                print(f"\n\nInterrupted at AppID {appid}")
                print(f"Resume with: resume_from={appid}")
                break
            except Exception as e:
                print(f"Error processing {appid}: {e}")
                continue
        
        # Final summary
        elapsed = time.time() - start_time
        print(f"\n=== Import Complete ===")
        print(f"Processed: {processed:,} games")
        print(f"Inserted: {inserted:,} stats")
        print(f"Time: {elapsed/3600:.1f} hours")
        if processed > 0:
            print(f"Success rate: {inserted/processed*100:.1f}%")
        
        self.session.close()


def main():
    """Run SteamSpy import."""
    importer = SteamSpyImporter()
    
    # Run import for all games without stats
    importer.run_import()


if __name__ == '__main__':
    main()
