"""
CarDekho Adapter - Scrapes listings from CarDekho
"""

from typing import List
from etl.extract.base_adapter import BaseAdapter
from etl.models import RawListing
from etl.utils.logger import setup_logger

logger = setup_logger(__name__)


class CarDekhoAdapter(BaseAdapter):
    """CarDekho source adapter"""
    
    def __init__(self):
        super().__init__("cardekho", "https://www.cardekho.com")
    
    def scrape(self, city: str, max_pages: int = 3) -> List[RawListing]:
        """Scrape CarDekho listings"""
        listings = []
        city_slug = city.lower().replace(" ", "-")
        
        for page in range(1, max_pages + 1):
            try:
                url = f"{self.base_url}/used-cars+in+{city_slug}?page={page}"
                logger.info(f"Scraping CarDekho: {url}")
                
                html = self.fetch_html(url)
                if not html:
                    continue
                
                soup = self.parse_html(html)
                cards = soup.find_all('div', class_='NewUcExCard')
                
                for card in cards:
                    listing = self.extract_listing(card)
                    if listing:
                        listings.append(listing)
                
                self.sleep()
                
            except Exception as e:
                logger.error(f"Error scraping CarDekho page {page}: {e}")
                continue
        
        logger.info(f"CarDekho: Scraped {len(listings)} listings from {city}")
        return listings
    
    def extract_listing(self, card) -> RawListing:
        """Extract data from CarDekho listing card"""
        try:
            # Title: "Hyundai i10 2012"
            title_elem = card.find('h3', class_='title')
            if not title_elem:
                return None
            title_link = title_elem.find('a')
            title = title_link.text.strip() if title_link else ""
            
            # Year from span inside title
            year_elem = title_link.find('span') if title_link else None
            year = year_elem.text.strip() if year_elem else None
            
            # Price: "₹2.97L"
            price_elem = card.find('div', class_='Price')
            if price_elem:
                price_p = price_elem.find('p')
                price_text = price_p.text.strip() if price_p else "0"
            else:
                price_text = "0"
            
            # Details: km, transmission, fuel
            details_div = card.find('div', class_='dotsDetails')
            detail_items = details_div.find_all('div') if details_div else []
            
            km = detail_items[0].text.strip() if len(detail_items) > 0 else None
            transmission = detail_items[1].text.strip() if len(detail_items) > 1 else None
            fuel = detail_items[2].text.strip() if len(detail_items) > 2 else None
            
            # URL
            url = title_link['href'] if title_link and title_link.get('href') else None
            if url and not url.startswith('http'):
                url = self.base_url + url
            
            # Parse title (remove year from title)
            title_clean = title.replace(year, '').strip() if year else title
            parts = title_clean.split()
            brand = parts[0] if len(parts) > 0 else None
            model = parts[1] if len(parts) > 1 else None
            variant = " ".join(parts[2:]) if len(parts) > 2 else None
            
            return RawListing(
                source="cardekho",
                brand=brand,
                model=model,
                variant=variant,
                year=int(year) if year and year.isdigit() else None,
                fuel=fuel,
                transmission=transmission,
                price=self._parse_price(price_text),
                kilometers=self._parse_km(km),
                listing_url=url
            )
        except Exception as e:
            logger.error(f"Error extracting CarDekho listing: {e}")
            return None
    
    def _parse_price(self, price_text: str) -> int:
        """Parse price from text"""
        try:
            price_text = price_text.replace('₹', '').replace(',', '').strip()
            if 'L' in price_text:
                num = float(price_text.replace('L', '').strip())
                return int(num * 100000)
            if 'Lakh' in price_text or 'lakh' in price_text:
                num = float(price_text.split()[0])
                return int(num * 100000)
            return int(price_text)
        except:
            return None
    
    def _parse_km(self, km_text: str) -> int:
        """Parse kilometers from text"""
        try:
            km_text = km_text.replace('kms', '').replace('km', '').replace(',', '').strip()
            return int(km_text)
        except:
            return None
