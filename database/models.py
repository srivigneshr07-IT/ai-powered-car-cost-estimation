"""
SQLAlchemy ORM Models for Market Intelligence Database
Defines 5 tables: market_prices, market_statistics, prediction_logs, market_sources, pipeline_logs
"""

from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, Text, DateTime, Index, UniqueConstraint
)
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class MarketPrice(Base):
    """Raw scraped car listings from various sources"""
    __tablename__ = "market_prices"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Source Information
    source = Column(String(50), nullable=False, index=True)
    listing_id = Column(String(100))
    listing_url = Column(Text)
    
    # Vehicle Details (Normalized)
    brand = Column(String(100), nullable=False, index=True)
    model = Column(String(100), nullable=False, index=True)
    variant = Column(String(200))
    year = Column(Integer, nullable=False, index=True)
    
    # Specifications
    fuel = Column(String(50))
    transmission = Column(String(50))
    body_type = Column(String(50))
    owner_type = Column(String(50))
    
    # Pricing & Condition
    price = Column(Integer, nullable=False, index=True)
    kilometers = Column(Integer)
    
    # Location
    city = Column(String(100), nullable=False, index=True)
    state = Column(String(100))
    
    # Metadata
    scraped_at = Column(DateTime, default=datetime.utcnow, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_seen_at = Column(DateTime, default=datetime.utcnow, index=True)  # Track freshness
    is_active = Column(Boolean, default=True, index=True)
    
    # Deduplication
    listing_hash = Column(String(64), unique=True, index=True)
    
    # Composite indexes for common queries
    __table_args__ = (
        Index('idx_brand_model_year_city', 'brand', 'model', 'year', 'city'),
        Index('idx_brand_model_city', 'brand', 'model', 'city'),
        Index('idx_price_year', 'price', 'year'),
    )


class MarketStatistic(Base):
    """Aggregated market statistics for fast queries"""
    __tablename__ = "market_statistics"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Grouping Dimensions
    brand = Column(String(100), nullable=False, index=True)
    model = Column(String(100), nullable=False, index=True)
    year = Column(Integer, index=True)
    city = Column(String(100), index=True)
    fuel = Column(String(50))
    transmission = Column(String(50))
    
    # Statistical Metrics
    avg_price = Column(Integer)
    median_price = Column(Integer)
    min_price = Column(Integer)
    max_price = Column(Integer)
    std_dev = Column(Float)
    
    # Sample Information
    listing_count = Column(Integer)
    
    # Temporal Metadata
    calculated_at = Column(DateTime, default=datetime.utcnow, index=True)
    data_start_date = Column(DateTime)
    data_end_date = Column(DateTime)
    
    # Composite unique constraint
    __table_args__ = (
        UniqueConstraint('brand', 'model', 'year', 'city', 'fuel', 'transmission', 
                        name='uq_market_stats'),
        Index('idx_stats_lookup', 'brand', 'model', 'year', 'city'),
    )


class PredictionLog(Base):
    """Audit trail of all price predictions"""
    __tablename__ = "prediction_logs"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Input Features
    brand = Column(String(100))
    model = Column(String(100))
    variant = Column(String(200))
    year = Column(Integer)
    kilometers = Column(Integer)
    fuel = Column(String(50))
    transmission = Column(String(50))
    body_type = Column(String(50))
    owner_type = Column(String(50))
    city = Column(String(100))
    state = Column(String(100))
    car_age = Column(Integer)
    premium_brand = Column(Integer)
    transaction_mode = Column(String(50))
    
    # Predictions
    ml_base_price = Column(Integer)
    market_average = Column(Integer)
    market_median = Column(Integer)
    final_price = Column(Integer)
    
    # Calculation Details
    ml_weight = Column(Float)
    market_avg_weight = Column(Float)
    market_median_weight = Column(Float)
    
    # Metadata
    confidence_score = Column(Integer)
    listings_used = Column(Integer)
    market_data_age_hours = Column(Integer)
    
    # Audit
    predicted_at = Column(DateTime, default=datetime.utcnow, index=True)
    user_id = Column(String(100))
    session_id = Column(String(100))
    
    __table_args__ = (
        Index('idx_prediction_brand_model', 'brand', 'model'),
        Index('idx_prediction_date', 'predicted_at'),
    )


class MarketSource(Base):
    """Metadata about scraping sources"""
    __tablename__ = "market_sources"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    source_name = Column(String(50), unique=True, nullable=False)
    base_url = Column(Text)
    is_active = Column(Boolean, default=True)
    last_scraped_at = Column(DateTime)
    total_listings_scraped = Column(Integer, default=0)
    success_rate = Column(Float)
    avg_response_time_ms = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class PipelineLog(Base):
    """ETL pipeline execution history"""
    __tablename__ = "pipeline_logs"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    pipeline_run_id = Column(String(100), unique=True, nullable=False)
    
    # Execution Details
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    duration_seconds = Column(Integer)
    status = Column(String(50))  # 'success', 'failed', 'partial'
    
    # Metrics
    listings_extracted = Column(Integer)
    listings_transformed = Column(Integer)
    listings_loaded = Column(Integer)
    duplicates_found = Column(Integer)
    validation_failures = Column(Integer)
    
    # Error Tracking
    error_message = Column(Text)
    error_stacktrace = Column(Text)
    
    # Metadata
    executed_by = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
