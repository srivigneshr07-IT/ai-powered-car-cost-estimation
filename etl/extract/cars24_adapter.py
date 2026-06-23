"""
Cars24 Adapter - Scrapes listings from Cars24
"""

from typing import List
from etl.extract.base_adapter import BaseAdapter
from etl.models import RawListing
from etl.utils.logger import setup_logger

logger = setup_logger(__name__)


class Cars24Adapter(BaseAdapter):
    """Cars24 source adapter"""
    
    def __init__(self):
        super().__init__("cars24", "https://www.cars24.com")
    
    def scrape(self, city: str, max_pages: int = 3) -> List[RawListing]:
        """Scrape Cars24 listings"""
        listings = []
        city_slug = city.lower().replace(" ", "-")
        
        for page in range(1, max_pages + 1):
            try:
                url = f"{self.base_url}/buy-used-car?f=make%3A%3A&sort=bestmatch&serveWarrantyCount=true&gaId=482098804.1734598525&listingSource=C2b&city={city_slug}&page={page}"
                logger.info(f"Scraping Cars24: {url}")
                
                html = self.fetch_html(url)
                if not html:
                    continue
                
                soup = self.parse_html(html)
                cards = soup.find_all('div', class_='styles_normalCardWrapper__qDZjq')
                
                for card in cards:
                    listing = self.extract_listing(card)
                    if listing:
                        listings.append(listing)
                
                self.sleep()
                
            except Exception as e:
                logger.error(f"Error scraping Cars24 page {page}: {e}")
                continue
        
        logger.info(f"Cars24: Scraped {len(listings)} listings from {city}")
        return listings
    
    def extract_listing(self, card) -> RawListing:
        """Extract data from Cars24 listing card"""
        try:
            # Extract title (e.g., "2015 Maruti Swift")
            title_elem = card.find('span', class_='bAcffq')
            title = title_elem.text.strip() if title_elem else ""
            
            # Extract price (e.g., "₹3.13 lakh")
            price_elem = card.find('p', class_='hvRpEM')
            price_text = price_elem.text.strip() if price_elem else "0"
            
            # Extract details (km, fuel, transmission)
            details = card.find_all('p', class_='kNDBvu')
            km = details[0].text.strip() if len(details) > 0 else None
            fuel = details[1].text.strip() if len(details) > 1 else None
            transmission = details[2].text.strip() if len(details) > 2 else None
            
            # Extract URL
            link_elem = card.find('a')
            url = self.base_url + link_elem['href'] if link_elem and link_elem.get('href') else None
            
            # Parse title for brand/model/year
            # Title format: "2015 Maruti Swift"
            parts = title.split()
            year = parts[0] if len(parts) > 0 and parts[0].isdigit() else None
            brand = parts[1] if len(parts) > 1 else None
            model = parts[2] if len(parts) > 2 else None
            variant = " ".join(parts[3:]) if len(parts) > 3 else None
            
            return RawListing(
                source="cars24",
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
            logger.error(f"Error extracting Cars24 listing: {e}")
            return None
    
    def _parse_price(self, price_text: str) -> int:
        """Parse price from text"""
        try:
            price_text = price_text.replace('₹', '').replace(',', '').strip()
            if 'Lakh' in price_text or 'lakh' in price_text:
                num = float(price_text.split()[0])
                return int(num * 100000)
            return int(price_text)
        except:
            return None
    
    def _parse_km(self, km_text: str) -> int:
        """Parse kilometers from text"""
        try:
            km_text = km_text.replace('km', '').replace(',', '').strip()
            return int(km_text)
        except:
            return None
