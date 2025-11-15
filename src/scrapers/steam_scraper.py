"""
Web scraper for Steam store pages.
"""

import logging
import time
from typing import Dict, Optional, List, Any
import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class SteamStoreScraper:
    """Scraper for Steam store pages."""
    
    BASE_URL = "https://store.steampowered.com"
    
    def __init__(self, rate_limit_delay: float = 1.0):
        """
        Initialize Steam store scraper.
        
        Args:
            rate_limit_delay: Delay in seconds between requests
        """
        self.rate_limit_delay = rate_limit_delay
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def scrape_game_page(self, app_id: int) -> Optional[Dict[str, Any]]:
        """
        Scrape a game's store page.
        
        Args:
            app_id: Steam application ID
            
        Returns:
            Dictionary containing scraped data, or None if scraping fails
        """
        url = f"{self.BASE_URL}/app/{app_id}"
        
        try:
            time.sleep(self.rate_limit_delay)
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract game information
            data = {
                'app_id': app_id,
                'name': self._extract_game_name(soup),
                'short_description': self._extract_short_description(soup),
                'reviews': self._extract_reviews(soup),
                'release_date': self._extract_release_date(soup),
                'developer': self._extract_developer(soup),
                'publisher': self._extract_publisher(soup),
                'tags': self._extract_tags(soup),
                'price': self._extract_price(soup)
            }
            
            return data
            
        except requests.RequestException as e:
            logger.error(f"Error scraping game page for {app_id}: {e}")
            return None
    
    def _extract_game_name(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract game name from page."""
        name_elem = soup.find('div', class_='apphub_AppName')
        if name_elem:
            return name_elem.text.strip()
        return None
    
    def _extract_short_description(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract short description from page."""
        desc_elem = soup.find('div', class_='game_description_snippet')
        if desc_elem:
            return desc_elem.text.strip()
        return None
    
    def _extract_reviews(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract review summary from page."""
        reviews = {}
        review_elem = soup.find('div', class_='user_reviews_summary_row')
        if review_elem:
            summary = review_elem.find('span', class_='game_review_summary')
            if summary:
                reviews['summary'] = summary.text.strip()
        return reviews
    
    def _extract_release_date(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract release date from page."""
        date_elem = soup.find('div', class_='release_date')
        if date_elem:
            date_text = date_elem.find('div', class_='date')
            if date_text:
                return date_text.text.strip()
        return None
    
    def _extract_developer(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract developer from page."""
        dev_elem = soup.find('div', id='developers_list')
        if dev_elem:
            link = dev_elem.find('a')
            if link:
                return link.text.strip()
        return None
    
    def _extract_publisher(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract publisher from page."""
        pub_elem = soup.find('div', class_='dev_row')
        if pub_elem and 'Publisher:' in pub_elem.text:
            link = pub_elem.find('a')
            if link:
                return link.text.strip()
        return None
    
    def _extract_tags(self, soup: BeautifulSoup) -> List[str]:
        """Extract popular tags from page."""
        tags = []
        tag_container = soup.find('div', class_='glance_tags popular_tags')
        if tag_container:
            tag_elems = tag_container.find_all('a', class_='app_tag')
            tags = [tag.text.strip() for tag in tag_elems]
        return tags
    
    def _extract_price(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract pricing information from page."""
        price_data = {}
        
        # Check for free game
        free_elem = soup.find('div', class_='game_purchase_price')
        if free_elem and 'free' in free_elem.text.lower():
            price_data['is_free'] = True
            price_data['price'] = 0.0
            return price_data
        
        # Check for regular/discounted price
        price_elem = soup.find('div', class_='game_purchase_price')
        discount_elem = soup.find('div', class_='discount_final_price')
        
        if discount_elem:
            price_data['is_free'] = False
            price_data['discount_price'] = discount_elem.text.strip()
            
            original = soup.find('div', class_='discount_original_price')
            if original:
                price_data['original_price'] = original.text.strip()
            
            discount_pct = soup.find('div', class_='discount_pct')
            if discount_pct:
                price_data['discount_percent'] = discount_pct.text.strip()
        elif price_elem:
            price_data['is_free'] = False
            price_data['price'] = price_elem.text.strip()
        
        return price_data
