"""
Selenium Helper - Browser automation for JavaScript-rendered pages
"""

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time


class SeleniumHelper:
    """Manages Selenium WebDriver for scraping JavaScript-rendered pages"""
    
    def __init__(self):
        self.driver = None
    
    def get_driver(self):
        """Initialize and return Chrome driver (reuse if already created)"""
        if self.driver is None:
            options = Options()
            options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            options.add_argument('--window-size=1920,1080')
            options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
            
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=options)
        
        return self.driver
    
    def fetch_html(self, url: str, wait_seconds: int = 5) -> str:
        """Fetch HTML from URL using Selenium"""
        try:
            driver = self.get_driver()
            driver.get(url)
            
            # Wait for page to load
            time.sleep(wait_seconds)
            
            # Get rendered HTML
            html = driver.page_source
            return html
            
        except Exception as e:
            print(f"Selenium error: {e}")
            return None
    
    def close(self):
        """Close the browser"""
        if self.driver:
            self.driver.quit()
            self.driver = None


# Global instance to reuse browser across scraping sessions
_selenium_helper = None

def get_selenium_helper():
    """Get or create global Selenium helper instance"""
    global _selenium_helper
    if _selenium_helper is None:
        _selenium_helper = SeleniumHelper()
    return _selenium_helper

def close_selenium():
    """Close global Selenium helper"""
    global _selenium_helper
    if _selenium_helper:
        _selenium_helper.close()
        _selenium_helper = None
