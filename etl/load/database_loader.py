"""
Database Loader - Loads data into PostgreSQL
"""

from typing import List
from datetime import datetime
from sqlalchemy.dialects.postgresql import insert
from database.connection import get_session
from database.models import MarketPrice, MarketStatistic, PipelineLog, MarketSource
from etl.models import CleanListing, MarketStatistics
from etl.utils.logger import setup_logger

logger = setup_logger(__name__)


class DatabaseLoader:
    """Load data into PostgreSQL"""
    
    @staticmethod
    def load_listings(listings: List[CleanListing]) -> int:
        """
        Load listings into market_prices table
        Uses UPSERT (insert or update on conflict)
        Returns: number of records inserted
        """
        if not listings:
            return 0
        
        inserted = 0
        
        with get_session() as session:
            try:
                for listing in listings:
                    # Convert Pydantic model to dict
                    data = {
                        'source': listing.source,
                        'brand': listing.brand,
                        'model': listing.model,
                        'variant': listing.variant,
                        'year': listing.year,
                        'fuel': listing.fuel,
                        'transmission': listing.transmission,
                        'body_type': listing.body_type,
                        'owner_type': listing.owner_type,
                        'price': listing.price,
                        'kilometers': listing.kilometers,
                        'city': listing.city,
                        'state': listing.state,
                        'listing_url': listing.listing_url,
                        'listing_id': listing.listing_id,
                        'listing_hash': listing.listing_hash,
                        'scraped_at': listing.scraped_at,
                        'is_active': listing.is_active
                    }
                    
                    # UPSERT: update if listing_hash exists
                    stmt = insert(MarketPrice).values(**data)
                    stmt = stmt.on_conflict_do_update(
                        index_elements=['listing_hash'],
                        set_={
                            'price': data['price'], 
                            'scraped_at': data['scraped_at'],
                            'last_seen_at': datetime.utcnow()  # Update freshness timestamp
                        }
                    )
                    
                    session.execute(stmt)
                    inserted += 1
                
                session.commit()
                logger.info(f"Loaded {inserted} listings into market_prices")
                return inserted
                    
            except Exception as e:
                logger.error(f"Error loading listings: {e}")
                raise
    
    @staticmethod
    def load_statistics(stats_list: List[MarketStatistics]) -> int:
        """
        Load statistics into market_statistics table
        Uses UPSERT (insert or update on conflict)
        Returns: number of records inserted
        """
        if not stats_list:
            return 0
        
        inserted = 0
        
        with get_session() as session:
            try:
                for stats in stats_list:
                    # Convert Pydantic model to dict
                    data = {
                        'brand': stats.brand,
                        'model': stats.model,
                        'year': stats.year,
                        'city': stats.city,
                        'fuel': stats.fuel,
                        'transmission': stats.transmission,
                        'avg_price': stats.avg_price,
                        'median_price': stats.median_price,
                        'min_price': stats.min_price,
                        'max_price': stats.max_price,
                        'std_dev': stats.std_dev,
                        'listing_count': stats.listing_count,
                        'calculated_at': stats.calculated_at,
                        'data_start_date': stats.data_start_date,
                        'data_end_date': stats.data_end_date
                    }
                    
                    # UPSERT: update if unique constraint matches
                    stmt = insert(MarketStatistic).values(**data)
                    stmt = stmt.on_conflict_do_update(
                        constraint='uq_market_stats',
                        set_={
                            'avg_price': data['avg_price'],
                            'median_price': data['median_price'],
                            'min_price': data['min_price'],
                            'max_price': data['max_price'],
                            'std_dev': data['std_dev'],
                            'listing_count': data['listing_count'],
                            'calculated_at': data['calculated_at'],
                            'data_start_date': data['data_start_date'],
                            'data_end_date': data['data_end_date']
                        }
                    )
                    
                    session.execute(stmt)
                    inserted += 1
                
                session.commit()
                logger.info(f"Loaded {inserted} statistics into market_statistics")
                return inserted
                    
            except Exception as e:
                logger.error(f"Error loading statistics: {e}")
                raise
    
    @staticmethod
    def log_pipeline_run(run_id: str, status: str, metrics: dict, error: str = None):
        """Log pipeline execution to pipeline_logs"""
        with get_session() as session:
            try:
                log = PipelineLog(
                    pipeline_run_id=run_id,
                    started_at=metrics.get('started_at'),
                    completed_at=metrics.get('completed_at'),
                    duration_seconds=metrics.get('duration_seconds'),
                    status=status,
                    listings_extracted=metrics.get('listings_extracted', 0),
                    listings_transformed=metrics.get('listings_transformed', 0),
                    listings_loaded=metrics.get('listings_loaded', 0),
                    duplicates_found=metrics.get('duplicates_found', 0),
                    validation_failures=metrics.get('validation_failures', 0),
                    error_message=error
                )
                
                session.add(log)
                session.commit()
                logger.info(f"Logged pipeline run: {run_id}")
                    
            except Exception as e:
                logger.error(f"Error logging pipeline run: {e}")
    
    @staticmethod
    def update_source_metadata(source_name: str, listings_count: int, success: bool):
        """Update market_sources metadata"""
        with get_session() as session:
            try:
                source = session.query(MarketSource).filter_by(source_name=source_name).first()
                
                if source:
                    source.last_scraped_at = datetime.utcnow()
                    source.total_listings_scraped += listings_count
                    source.updated_at = datetime.utcnow()
                else:
                    source = MarketSource(
                        source_name=source_name,
                        last_scraped_at=datetime.utcnow(),
                        total_listings_scraped=listings_count,
                        is_active=True
                    )
                    session.add(source)
                
                session.commit()
                logger.info(f"Updated source metadata: {source_name}")
                    
            except Exception as e:
                logger.error(f"Error updating source metadata: {e}")
