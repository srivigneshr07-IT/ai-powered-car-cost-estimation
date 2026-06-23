"""
Pydantic Models for ETL Pipeline
Standardized data structures for Extract, Transform, Load
"""

from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime


class RawListing(BaseModel):
    """Raw scraped listing (before transformation)"""
    source: str
    brand: Optional[str] = None
    model: Optional[str] = None
    variant: Optional[str] = None
    year: Optional[int] = None
    fuel: Optional[str] = None
    transmission: Optional[str] = None
    body_type: Optional[str] = None
    owner_type: Optional[str] = None
    price: Optional[int] = None
    kilometers: Optional[int] = None
    city: Optional[str] = None
    state: Optional[str] = None
    listing_url: Optional[str] = None
    listing_id: Optional[str] = None


class CleanListing(BaseModel):
    """Cleaned and normalized listing (after transformation)"""
    source: str
    brand: str
    model: str
    variant: Optional[str] = None
    year: int
    fuel: str
    transmission: str
    body_type: Optional[str] = None
    owner_type: Optional[str] = None
    price: int
    kilometers: int
    city: str
    state: Optional[str] = None
    listing_url: Optional[str] = None
    listing_id: Optional[str] = None
    listing_hash: str
    scraped_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = True

    @validator('price')
    def validate_price(cls, v):
        if not (50000 <= v <= 50000000):
            raise ValueError(f"Price {v} out of range")
        return v

    @validator('kilometers')
    def validate_km(cls, v):
        if not (0 <= v <= 500000):
            raise ValueError(f"Kilometers {v} out of range")
        return v

    @validator('year')
    def validate_year(cls, v):
        if not (1990 <= v <= 2026):
            raise ValueError(f"Year {v} out of range")
        return v


class MarketStatistics(BaseModel):
    """Aggregated market statistics"""
    brand: str
    model: str
    year: Optional[int] = None
    city: Optional[str] = None
    fuel: Optional[str] = None
    transmission: Optional[str] = None
    avg_price: int
    median_price: int
    min_price: int
    max_price: int
    std_dev: float
    listing_count: int
    calculated_at: datetime = Field(default_factory=datetime.utcnow)
    data_start_date: datetime
    data_end_date: datetime
