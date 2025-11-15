"""
Tests for web scraper.
"""

from unittest.mock import Mock, patch
from src.scrapers.steam_scraper import SteamStoreScraper


def test_scraper_initialization():
    """Test scraper initialization."""
    scraper = SteamStoreScraper(rate_limit_delay=2.0)
    assert scraper.rate_limit_delay == 2.0
    assert scraper.session is not None


@patch('src.scrapers.steam_scraper.requests.Session.get')
def test_scrape_game_page_success(mock_get):
    """Test successful game page scraping."""
    # Mock HTML response
    mock_response = Mock()
    mock_response.text = '''
    <html>
        <div class="apphub_AppName">Test Game</div>
        <div class="game_description_snippet">Test description</div>
        <div class="release_date">
            <div class="date">Jan 1, 2020</div>
        </div>
        <div id="developers_list">
            <a>Test Developer</a>
        </div>
    </html>
    '''
    mock_response.raise_for_status = Mock()
    mock_get.return_value = mock_response
    
    scraper = SteamStoreScraper(rate_limit_delay=0.1)
    data = scraper.scrape_game_page(12345)
    
    assert data is not None
    assert data['app_id'] == 12345
    assert data['name'] == 'Test Game'
    assert data['short_description'] == 'Test description'


@patch('src.scrapers.steam_scraper.time.sleep')
@patch('src.scrapers.steam_scraper.requests.Session.get')
def test_scrape_game_page_network_error(mock_get, mock_sleep):
    """Test scraping with network error."""
    from requests import RequestException
    mock_get.side_effect = RequestException("Network error")
    
    scraper = SteamStoreScraper(rate_limit_delay=0.1)
    data = scraper.scrape_game_page(12345)
    
    assert data is None


def test_extract_price_free_game():
    """Test price extraction for free games."""
    from bs4 import BeautifulSoup
    
    html = '<div class="game_purchase_price">Free To Play</div>'
    soup = BeautifulSoup(html, 'html.parser')
    
    scraper = SteamStoreScraper()
    price_data = scraper._extract_price(soup)
    
    assert price_data.get('is_free') is True
    assert price_data.get('price') == 0.0


def test_extract_price_with_discount():
    """Test price extraction with discount."""
    from bs4 import BeautifulSoup
    
    html = '''
    <div class="discount_final_price">$9.99</div>
    <div class="discount_original_price">$19.99</div>
    <div class="discount_pct">-50%</div>
    '''
    soup = BeautifulSoup(html, 'html.parser')
    
    scraper = SteamStoreScraper()
    price_data = scraper._extract_price(soup)
    
    assert price_data.get('is_free') is False
    assert price_data.get('discount_price') == '$9.99'
    assert price_data.get('original_price') == '$19.99'
    assert price_data.get('discount_percent') == '-50%'
