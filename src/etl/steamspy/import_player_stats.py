"""
SteamSpy API - Player Stats Enrichment (BULK MODE)
Imports player statistics from SteamSpy using bulk API.

NEW BULK API: Returns 1,000 games per request!
Rate Limit: 1 request per 60 seconds for 'all' endpoint
Execution Time: ~4 hours for 200K games (vs 14 hours one-by-one)
"""
import time
import requests
from datetime import datetime
from sqlalchemy import text
from src.database.connection import SessionLocal


class SteamSpyImporter:
    """Import player stats from SteamSpy API using BULK mode."""
    
    def __init__(self):
        self.base_url = "https://steamspy.com/api.php"
        self.bulk_rate_limit = 60  # 1 req per 60 sec for 'all' endpoint
        self.session = SessionLocal()
        
    def get_bulk_games(self, page):
        """
        Fetch 1,000 games at once from SteamSpy bulk API.
        
        Returns dict of {appid: game_data}
        """
        try:
            print(f"  Fetching page {page} (games {page*1000}-{(page+1)*1000})...")
            response = requests.get(
                self.base_url,
                params={'request': 'all', 'page': page},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Response is dict with appids as keys
                games = {}
                for appid_str, game_data in data.items():
                    try:
                        appid = int(appid_str)
                        if appid > 0 and game_data.get('appid', 0) > 0:
                            games[appid] = {
                                'steam_appid': appid,
                                'estimated_owners': self._parse_owners(
                                    game_data.get('owners', '0')
                                ),
                                'peak_players_24h': game_data.get('ccu', 0),
                                'current_players': game_data.get('players_forever', 0),
                                'average_playtime': game_data.get('average_forever', 0),
                                'median_playtime': game_data.get('median_forever', 0),
                                'positive_reviews': game_data.get('positive', 0),
                                'negative_reviews': game_data.get('negative', 0),
                                'timestamp': datetime.now()
                            }
                    except (ValueError, KeyError, TypeError):
                        continue
                
                print(f"  Retrieved {len(games)} valid games")
                return games
            else:
                print(f"  HTTP {response.status_code}")
                return {}
            
        except Exception as e:
            print(f"  Error fetching page {page}: {e}")
            return {}
    
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
    
    def get_games_needing_stats(self):
        """Get set of AppIDs that need player stats."""
        query = text("""
            SELECT g.steam_appid
            FROM games g
            LEFT JOIN player_stats ps ON g.steam_appid = ps.steam_appid
            WHERE ps.steam_appid IS NULL
            ORDER BY g.steam_appid
        """)
        
        result = self.session.execute(query).fetchall()
        return set(row[0] for row in result)
    
    def insert_bulk_stats(self, stats_dict, needed_appids):
        """
        Insert stats from bulk fetch, filtering to only needed games.
        
        Args:
            stats_dict: Dict of {appid: stats} from bulk API
            needed_appids: Set of AppIDs that need stats
            
        Returns:
            Number of records inserted
        """
        if not stats_dict:
            return 0
        
        inserted = 0
        for appid, stats in stats_dict.items():
            # Only insert if this game needs stats
            if appid not in needed_appids:
                continue
                
            try:
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
    
    def run_bulk_import(self, start_page=0, max_pages=None):
        """
        Run BULK import using 'all' endpoint (1,000 games per request).
        
        Args:
            start_page: Page number to start from (for resume)
            max_pages: Maximum pages to process (None = all)
        """
        print("=" * 70)
        print("SteamSpy BULK Import (1,000 games per request)")
        print("=" * 70)
        print()
        
        # Get games needing stats
        print("Loading games that need stats...")
        needed_appids = self.get_games_needing_stats()
        print(f"Games needing stats: {len(needed_appids):,}\n")
        
        if len(needed_appids) == 0:
            print("No games need stats!")
            return
        
        # Estimate pages needed (SteamSpy has ~200 pages of 1000 games each)
        estimated_pages = 220  # ~220K games total on SteamSpy
        if max_pages:
            estimated_pages = min(estimated_pages, max_pages)
        
        print(f"Starting from page: {start_page}")
        print(f"Estimated pages: {estimated_pages}")
        print(f"Rate limit: 1 request per 60 seconds")
        est_time = (estimated_pages * 60) / 3600
        print(f"Estimated time: {est_time:.1f} hours")
        print(f"(Much faster than 14 hours one-by-one!)\n")
        
        # Auto-start
        print("Starting bulk import...\n")
        
        start_time = time.time()
        total_inserted = 0
        pages_processed = 0
        
        try:
            for page in range(start_page, start_page + estimated_pages):
                # Fetch bulk page (1,000 games)
                games_dict = self.get_bulk_games(page)
                
                if not games_dict:
                    print(f"  Page {page} returned no data (end of list?)")
                    break
                
                # Insert games that need stats
                inserted = self.insert_bulk_stats(games_dict, needed_appids)
                total_inserted += inserted
                pages_processed += 1
                
                # Remove inserted AppIDs from needed set
                for appid in games_dict.keys():
                    needed_appids.discard(appid)
                
                # Progress
                elapsed = time.time() - start_time
                rate = pages_processed / (elapsed / 60) if elapsed > 0 else 0
                remaining_pages = estimated_pages - pages_processed
                remaining_time = (remaining_pages / rate / 60) if rate > 0 else 0
                
                print(
                    f"  Inserted: {inserted} | "
                    f"Total: {total_inserted:,} | "
                    f"Page {page} | "
                    f"Still need: {len(needed_appids):,} | "
                    f"ETA: {remaining_time:.1f}h"
                )
                
                # Rate limiting - 60 seconds between requests
                if page < start_page + estimated_pages - 1:
                    print(f"  Waiting 60 seconds...")
                    time.sleep(self.bulk_rate_limit)
                
        except KeyboardInterrupt:
            print(f"\n\nInterrupted at page {page}")
            print(f"Resume with: start_page={page + 1}")
        
        # Final summary
        elapsed = time.time() - start_time
        print(f"\n" + "=" * 70)
        print("BULK IMPORT COMPLETE")
        print("=" * 70)
        print(f"Pages processed: {pages_processed}")
        print(f"Stats inserted: {total_inserted:,}")
        print(f"Games still needing stats: {len(needed_appids):,}")
        print(f"Time: {elapsed/3600:.2f} hours")
        
        self.session.close()


def main():
    """Run SteamSpy BULK import."""
    import sys
    
    importer = SteamSpyImporter()
    
    # Support resume from command line
    start_page = 0
    if len(sys.argv) > 1:
        try:
            start_page = int(sys.argv[1])
            print(f"Resuming from page: {start_page}\n")
        except ValueError:
            print("Usage: python import_player_stats.py [start_page]")
            sys.exit(1)
    
    # Run BULK import (1,000 games per request!)
    importer.run_bulk_import(start_page=start_page)


if __name__ == '__main__':
    main()
