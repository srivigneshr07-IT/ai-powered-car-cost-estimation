"""
Data Validator - Validates data against business rules
"""

from typing import Optional, Tuple
from etl.config import VALIDATION_RULES, SUPPORTED_BRANDS, SUPPORTED_CITIES
from etl.models import RawListing


class DataValidator:
    """Validate data against business rules"""
    
    @staticmethod
    def validate_price(price: int) -> Tuple[bool, Optional[str]]:
        """Validate price range"""
        if not price:
            return False, "Price is missing"
        
        min_price = VALIDATION_RULES['price']['min']
        max_price = VALIDATION_RULES['price']['max']
        
        if price < min_price or price > max_price:
            return False, f"Price {price} out of range ({min_price}-{max_price})"
        
        return True, None
    
    @staticmethod
    def validate_kilometers(km: int) -> Tuple[bool, Optional[str]]:
        """Validate kilometers range"""
        if km is None:
            return False, "Kilometers is missing"
        
        min_km = VALIDATION_RULES['kilometers']['min']
        max_km = VALIDATION_RULES['kilometers']['max']
        
        if km < min_km or km > max_km:
            return False, f"Kilometers {km} out of range ({min_km}-{max_km})"
        
        return True, None
    
    @staticmethod
    def validate_year(year: int) -> Tuple[bool, Optional[str]]:
        """Validate year range"""
        if not year:
            return False, "Year is missing"
        
        min_year = VALIDATION_RULES['year']['min']
        max_year = VALIDATION_RULES['year']['max']
        
        if year < min_year or year > max_year:
            return False, f"Year {year} out of range ({min_year}-{max_year})"
        
        return True, None
    
    @staticmethod
    def validate_brand(brand: str) -> Tuple[bool, Optional[str]]:
        """Validate brand is supported"""
        if not brand:
            return False, "Brand is missing"
        
        if brand not in SUPPORTED_BRANDS:
            return False, f"Brand {brand} not supported"
        
        return True, None
    
    @staticmethod
    def validate_required_fields(listing: RawListing) -> Tuple[bool, Optional[str]]:
        """Validate required fields exist"""
        if not listing.brand:
            return False, "Brand is required"
        if not listing.model:
            return False, "Model is required"
        if not listing.price:
            return False, "Price is required"
        if not listing.year:
            return False, "Year is required"
        
        return True, None
    
    @staticmethod
    def validate_listing(listing: RawListing) -> Tuple[bool, Optional[str]]:
        """Validate entire listing"""
        # Check required fields
        valid, error = DataValidator.validate_required_fields(listing)
        if not valid:
            return False, error
        
        # Validate price
        valid, error = DataValidator.validate_price(listing.price)
        if not valid:
            return False, error
        
        # Validate kilometers (optional but if present, must be valid)
        if listing.kilometers is not None:
            valid, error = DataValidator.validate_kilometers(listing.kilometers)
            if not valid:
                return False, error
        
        # Validate year
        valid, error = DataValidator.validate_year(listing.year)
        if not valid:
            return False, error
        
        # Validate brand (after normalization)
        valid, error = DataValidator.validate_brand(listing.brand)
        if not valid:
            return False, error
        
        return True, None
