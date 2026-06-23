"""
Base Adapter - Abstract class for all source adapters
Defines the interface that all scrapers must implement
"""

from abc import ABC, abstractmethod
from typing import List
import requests
from bs4 import BeautifulSoup
import time
from etl.models import RawListing
from etl.config import SCRAPING_CONFIG
from etl.utils.logger import setup_logger

logger = setup_logger(__name__)


class BaseAdapter(ABC):
    """Abstract base class for source adapters"""
    
    def __init__(self, source_name: str, base_url: str, use_selenium: bool = False):
        self.source_name = source_name
        self.base_url = base_url
        self.use_selenium = use_selenium
        self.headers = {'User-Agent': SCRAPING_CONFIG['user_agent']}
        self.timeout = 10
        self.delay = SCRAPING_CONFIG['delay_between_requests']
        self._selenium_helper = None
    
    def fetch_html(self, url: str) -> str:
        """Fetch HTML from URL (uses Selenium if use_selenium=True)"""
        if self.use_selenium:
            return self.fetch_html_selenium(url)
        
        try:
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            logger.error(f"Failed to fetch {url}: {e}")
            return ""
    
    def fetch_html_selenium(self, url: str) -> str:
        """Fetch HTML using better headers to mimic browser (fallback without Selenium)"""
        try:
            # Enhanced headers to bypass basic blocking
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Cache-Control': 'max-age=0',
            }
            
            import requests
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            
            # Wait a bit to mimic human behavior
            time.sleep(2)
            
            return response.text
        except Exception as e:
            logger.error(f"Enhanced fetch failed for {url}: {e}")
            return ""
    
    def parse_html(self, html: str) -> BeautifulSoup:
        """Parse HTML into BeautifulSoup object"""
        return BeautifulSoup(html, 'lxml')
    
    @abstractmethod
    def scrape(self, city: str, max_pages: int = 3) -> List[RawListing]:
        """
        Scrape listings for a city
        Must be implemented by child classes
        """
        pass
    
    @abstractmethod
    def extract_listing(self, card) -> RawListing:
        """
        Extract data from a single listing card
        Must be implemented by child classes
        """
        pass
    
    def sleep(self):
        """Sleep between requests"""
        time.sleep(self.delay)
