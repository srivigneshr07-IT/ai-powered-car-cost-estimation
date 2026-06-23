"""
Data Normalizer - Standardizes brands, fuel types, transmission, etc.
"""

from typing import Optional
from etl.config import BRAND_MAPPING, FUEL_MAPPING, TRANSMISSION_MAPPING, OWNER_MAPPING


class DataNormalizer:
    """Normalize data to standard formats"""
    
    @staticmethod
    def normalize_brand(brand: str) -> Optional[str]:
        """Normalize brand name"""
        if not brand:
            return None
        
        brand_lower = brand.lower().strip()
        return BRAND_MAPPING.get(brand_lower, brand.title())
    
    @staticmethod
    def normalize_fuel(fuel: str) -> Optional[str]:
        """Normalize fuel type"""
        if not fuel:
            return None
        
        fuel_lower = fuel.lower().strip()
        return FUEL_MAPPING.get(fuel_lower, fuel.title())
    
    @staticmethod
    def normalize_transmission(transmission: str) -> Optional[str]:
        """Normalize transmission type"""
        if not transmission:
            return None
        
        trans_lower = transmission.lower().strip()
        return TRANSMISSION_MAPPING.get(trans_lower, transmission.title())
    
    @staticmethod
    def normalize_owner(owner: str) -> Optional[str]:
        """Normalize owner type"""
        if not owner:
            return None
        
        owner_lower = owner.lower().strip()
        return OWNER_MAPPING.get(owner_lower, owner.title())
    
    @staticmethod
    def normalize_city(city: str) -> Optional[str]:
        """Normalize city name"""
        if not city:
            return None
        return city.title().strip()
