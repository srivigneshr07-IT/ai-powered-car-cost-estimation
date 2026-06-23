"""
Data Cleaner - Removes symbols, strips whitespace, converts types
"""

import re
from typing import Optional
from etl.models import RawListing


class DataCleaner:
    """Clean raw scraped data"""
    
    @staticmethod
    def clean_price(price_text: str) -> Optional[int]:
        """Clean price text to integer"""
        if not price_text:
            return None
        
        try:
            # Remove currency symbols and commas
            price_text = str(price_text).replace('₹', '').replace(',', '').strip()
            
            # Handle Lakh/Crore
            if 'lakh' in price_text.lower():
                num = float(re.findall(r'[\d.]+', price_text)[0])
                return int(num * 100000)
            elif 'crore' in price_text.lower():
                num = float(re.findall(r'[\d.]+', price_text)[0])
                return int(num * 10000000)
            
            # Direct number
            return int(float(price_text))
        except:
            return None
    
    @staticmethod
    def clean_kilometers(km_text: str) -> Optional[int]:
        """Clean kilometers text to integer"""
        if not km_text:
            return None
        
        try:
            km_text = str(km_text).replace('km', '').replace(',', '').strip()
            return int(float(km_text))
        except:
            return None
    
    @staticmethod
    def clean_year(year_text: str) -> Optional[int]:
        """Clean year text to integer"""
        if not year_text:
            return None
        
        try:
            year = int(str(year_text).strip())
            return year if 1990 <= year <= 2026 else None
        except:
            return None
    
    @staticmethod
    def clean_text(text: str) -> Optional[str]:
        """Clean general text - strip whitespace, lowercase"""
        if not text:
            return None
        return str(text).strip()
    
    @staticmethod
    def clean_listing(listing: RawListing) -> RawListing:
        """Clean all fields in a listing"""
        return RawListing(
            source=listing.source,
            brand=DataCleaner.clean_text(listing.brand),
            model=DataCleaner.clean_text(listing.model),
            variant=DataCleaner.clean_text(listing.variant),
            year=DataCleaner.clean_year(listing.year) if listing.year else None,
            fuel=DataCleaner.clean_text(listing.fuel),
            transmission=DataCleaner.clean_text(listing.transmission),
            body_type=DataCleaner.clean_text(listing.body_type),
            owner_type=DataCleaner.clean_text(listing.owner_type),
            price=DataCleaner.clean_price(listing.price) if listing.price else None,
            kilometers=DataCleaner.clean_kilometers(listing.kilometers) if listing.kilometers else None,
            city=DataCleaner.clean_text(listing.city),
            state=DataCleaner.clean_text(listing.state),
            listing_url=listing.listing_url,
            listing_id=listing.listing_id
        )
