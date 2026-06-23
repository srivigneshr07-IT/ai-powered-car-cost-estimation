"""
Spinny Adapter - Scrapes listings from Spinny
"""

from typing import List
from etl.extract.base_adapter import BaseAdapter
from etl.models import RawListing
from etl.utils.logger import setup_logger

logger = setup_logger(__name__)


class SpinnyAdapter(BaseAdapter):
    """Spinny source adapter"""
    
    def __init__(self):
        super().__init__("spinny", "https://www.spinny.com", use_selenium=True)
    
    def scrape(self, city: str, max_pages: int = 3) -> List[RawListing]:
        """Scrape Spinny listings"""
        listings = []
        city_slug = city.lower().replace(" ", "-")
        
        for page in range(1, max_pages + 1):
            try:
                # Spinny URL format: /used-cars-in-{city}/s/
                url = f"{self.base_url}/used-cars-in-{city_slug}/s/"
                if page > 1:
                    url += f"?page={page}"
                logger.info(f"Scraping Spinny: {url}")
                
                html = self.fetch_html(url)
                if not html:
                    continue
                
                soup = self.parse_html(html)
                cards = soup.find_all('div', class_='CarListingDesktop__carListingCarWrapper')
                
                for card in cards:
                    listing = self.extract_listing(card)
                    if listing:
                        listings.append(listing)
                
                self.sleep()
                
            except Exception as e:
                logger.error(f"Error scraping Spinny page {page}: {e}")
                continue
        
        logger.info(f"Spinny: Scraped {len(listings)} listings from {city}")
        return listings
    
    def extract_listing(self, card) -> RawListing:
        """Extract data from Spinny listing card"""
        try:
            # Title: "2025 Renault Triber"
            title_elem = card.find('h3', class_='ListingBrandModelDetail__makeModelInfo')
            if not title_elem:
                return None
            
            title_link = title_elem.find('a')
            title_span = title_link.find('span', class_='ListingBrandModelDetail__make') if title_link else None
            title = title_span.text.strip() if title_span else ""
            
            # Price: "7.85 Lakh"
            price_elem = card.find('li', class_='ListingBrandModelDetail__price')
            price_span = price_elem.find('span') if price_elem else None
            price_text = price_span.text.strip() if price_span else "0"
            
            # Variant: "RXZ AMT"
            variant_elem = card.find('span', class_='ListingPricingDetail__variant')
            variant = variant_elem.text.strip() if variant_elem else None
            
            # Details: km, fuel, transmission
            details_ul = card.find('ul', class_='CarListingCardDetail__more')
            detail_items = details_ul.find_all('li') if details_ul else []
            
            km = detail_items[0].text.strip() if len(detail_items) > 0 else None
            fuel = detail_items[1].text.strip() if len(detail_items) > 1 else None
            transmission = detail_items[2].text.strip() if len(detail_items) > 2 else None
            
            # URL
            url = title_link['href'] if title_link and title_link.get('href') else None
            if url and not url.startswith('http'):
                url = self.base_url + url
            
            # Parse title: "2025 Renault Triber"
            parts = title.split()
            year = parts[0] if len(parts) > 0 and parts[0].isdigit() else None
            brand = parts[1] if len(parts) > 1 else None
            model = parts[2] if len(parts) > 2 else None
            
            return RawListing(
                source="spinny",
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
            logger.error(f"Error extracting Spinny listing: {e}")
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
            # Handle formats like "7.5K km" or "75,000 km"
            km_text = km_text.replace('km', '').replace('kms', '').replace(',', '').strip()
            if 'K' in km_text or 'k' in km_text:
                num = float(km_text.replace('K', '').replace('k', '').strip())
                return int(num * 1000)
            return int(km_text)
        except:
            return None
