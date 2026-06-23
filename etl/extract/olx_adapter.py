"""
OLX Adapter - Scrapes listings from OLX
"""

from typing import List
from etl.extract.base_adapter import BaseAdapter
from etl.models import RawListing
from etl.utils.logger import setup_logger

logger = setup_logger(__name__)


class OLXAdapter(BaseAdapter):
    """OLX source adapter"""
    
    def __init__(self):
        super().__init__("olx", "https://www.olx.in", use_selenium=True)
    
    def scrape(self, city: str, max_pages: int = 3) -> List[RawListing]:
        """Scrape OLX listings"""
        listings = []
        
        # City-specific location codes for OLX
        city_codes = {
            "chennai": "chennai_g4059162",
            "bangalore": "bangalore_g4058877",
            "hyderabad": "hyderabad_g4058526",
            "mumbai": "mumbai_g4058877",
            "delhi": "delhi_g4000001",
            "pune": "pune_g4058900",
            "kolkata": "kolkata_g4058742",
            "ahmedabad": "ahmedabad_g4058644",
            "jaipur": "jaipur_g4059012",
            "lucknow": "lucknow_g4059003"
        }
        
        city_slug = city_codes.get(city.lower(), f"{city.lower()}_g4000000")
        
        for page in range(1, max_pages + 1):
            try:
                url = f"{self.base_url}/{city_slug}/cars_c84"
                if page > 1:
                    url += f"?page={page}"
                logger.info(f"Scraping OLX: {url}")
                
                html = self.fetch_html(url)
                if not html:
                    continue
                
                soup = self.parse_html(html)
                cards = soup.find_all('li', attrs={'data-aut-id': 'itemBox'})
                
                for card in cards:
                    listing = self.extract_listing(card)
                    if listing:
                        listings.append(listing)
                
                self.sleep()
                
            except Exception as e:
                logger.error(f"Error scraping OLX page {page}: {e}")
                continue
        
        logger.info(f"OLX: Scraped {len(listings)} listings from {city}")
        return listings
    
    def extract_listing(self, card) -> RawListing:
        """Extract data from OLX listing card"""
        try:
            title_elem = card.find('span', attrs={'data-aut-id': 'itemTitle'})
            title = title_elem.text.strip() if title_elem else ""
            
            price_elem = card.find('span', attrs={'data-aut-id': 'itemPrice'})
            price_text = price_elem.text.strip() if price_elem else "0"
            
            # OLX has details in description
            desc_elem = card.find('span', attrs={'data-aut-id': 'itemDetails'})
            desc = desc_elem.text.strip() if desc_elem else ""
            
            link_elem = card.find('a', attrs={'data-aut-id': 'itemTitle'})
            url = link_elem['href'] if link_elem and link_elem.get('href') else None
            if url and not url.startswith('http'):
                url = self.base_url + url
            
            # Parse title for brand/model
            parts = title.split()
            brand = parts[0] if len(parts) > 0 else None
            model = parts[1] if len(parts) > 1 else None
            variant = " ".join(parts[2:]) if len(parts) > 2 else None
            
            # Extract year and km from description
            year, km = self._parse_description(desc)
            
            return RawListing(
                source="olx",
                brand=brand,
                model=model,
                variant=variant,
                year=year,
                price=self._parse_price(price_text),
                kilometers=km,
                listing_url=url
            )
        except Exception as e:
            logger.error(f"Error extracting OLX listing: {e}")
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
    
    def _parse_description(self, desc: str):
        """Parse year and km from description"""
        year = None
        km = None
        
        try:
            parts = desc.split('-')
            for part in parts:
                part = part.strip()
                if 'km' in part.lower():
                    km_text = part.replace('km', '').replace(',', '').strip()
                    km = int(km_text) if km_text.isdigit() else None
                elif part.isdigit() and len(part) == 4:
                    year = int(part)
        except:
            pass
        
        return year, km
