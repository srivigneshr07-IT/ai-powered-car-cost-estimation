"""
ETL Pipeline Orchestrator
Coordinates Extract, Transform, Load, Aggregate phases
"""

import sys
from pathlib import Path

# Add parent directory to Python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import sys
from pathlib import Path

# Add parent directory to Python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import hashlib
from datetime import datetime
from typing import List
import uuid

from etl.extract.cars24_adapter import Cars24Adapter
from etl.extract.cardekho_adapter import CarDekhoAdapter
from etl.extract.spinny_adapter import SpinnyAdapter
from etl.extract.olx_adapter import OLXAdapter
from etl.transform.cleaner import DataCleaner
from etl.transform.normalizer import DataNormalizer
from etl.transform.validator import DataValidator
from etl.aggregate.aggregator import MarketAggregator
from etl.load.database_loader import DatabaseLoader
from etl.models import RawListing, CleanListing
from etl.config import SOURCES, SUPPORTED_CITIES, SCRAPING_CONFIG
from etl.utils.logger import setup_logger

logger = setup_logger(__name__)


class ETLPipeline:
    """Main ETL Pipeline Orchestrator"""
    
    def __init__(self):
        self.run_id = str(uuid.uuid4())
        self.adapters = {
            'cars24': Cars24Adapter(),
            'cardekho': CarDekhoAdapter(),
            'spinny': SpinnyAdapter(),
            'olx': OLXAdapter()
        }
        self.metrics = {
            'started_at': None,
            'completed_at': None,
            'duration_seconds': 0,
            'listings_extracted': 0,
            'listings_transformed': 0,
            'listings_loaded': 0,
            'duplicates_found': 0,
            'validation_failures': 0
        }
    
    def run(self, cities: List[str] = None, sources: List[str] = None):
        """
        Run the complete ETL pipeline
        
        Args:
            cities: List of cities to scrape (default: all supported cities)
            sources: List of sources to use (default: all enabled sources)
        """
        self.metrics['started_at'] = datetime.utcnow()
        logger.info(f"Starting ETL Pipeline - Run ID: {self.run_id}")
        
        try:
            # 1. EXTRACT
            raw_listings = self.extract(cities, sources)
            self.metrics['listings_extracted'] = len(raw_listings)
            logger.info(f"Extracted {len(raw_listings)} raw listings")
            
            # 2. TRANSFORM
            clean_listings = self.transform(raw_listings)
            self.metrics['listings_transformed'] = len(clean_listings)
            logger.info(f"Transformed {len(clean_listings)} clean listings")
            
            # 3. AGGREGATE
            statistics = self.aggregate(clean_listings)
            logger.info(f"Aggregated {len(statistics)} market statistics")
            
            # 4. LOAD
            self.load(clean_listings, statistics)
            
            # 5. LOG SUCCESS
            self.metrics['completed_at'] = datetime.utcnow()
            self.metrics['duration_seconds'] = int(
                (self.metrics['completed_at'] - self.metrics['started_at']).total_seconds()
            )
            
            DatabaseLoader.log_pipeline_run(self.run_id, 'success', self.metrics)
            
            logger.info(f"ETL Pipeline completed successfully - Run ID: {self.run_id}")
            self.print_summary()
            
        except Exception as e:
            logger.error(f"ETL Pipeline failed: {e}")
            self.metrics['completed_at'] = datetime.utcnow()
            DatabaseLoader.log_pipeline_run(self.run_id, 'failed', self.metrics, str(e))
            raise
    
    def extract(self, cities: List[str] = None, sources: List[str] = None) -> List[RawListing]:
        """Extract phase - scrape from all sources"""
        cities = cities or SUPPORTED_CITIES  # Use ALLUse ALL cities
        sources = sources or [s for s, cfg in SOURCES.items() if cfg['enabled']]
        
        all_listings = []
        max_pages = SCRAPING_CONFIG['max_pages_per_city']
        
        for source_name in sources:
            if source_name not in self.adapters:
                logger.warning(f"Adapter not found for source: {source_name}")
                continue
            
            adapter = self.adapters[source_name]
            source_listings = []
            
            for city in cities:
                try:
                    listings = adapter.scrape(city, max_pages)
                    source_listings.extend(listings)
                    
                    # Add city to listings if missing
                    for listing in listings:
                        if not listing.city:
                            listing.city = city
                    
                except Exception as e:
                    logger.error(f"Error scraping {source_name} for {city}: {e}")
                    continue
            
            all_listings.extend(source_listings)
            DatabaseLoader.update_source_metadata(source_name, len(source_listings), True)
            logger.info(f"{source_name}: Extracted {len(source_listings)} listings")
        
        return all_listings
    
    def transform(self, raw_listings: List[RawListing]) -> List[CleanListing]:
        """Transform phase - clean, normalize, validate"""
        clean_listings = []
        seen_hashes = set()
        
        for raw in raw_listings:
            try:
                # 1. Clean
                cleaned = DataCleaner.clean_listing(raw)
                
                # 2. Normalize
                cleaned.brand = DataNormalizer.normalize_brand(cleaned.brand)
                cleaned.fuel = DataNormalizer.normalize_fuel(cleaned.fuel)
                cleaned.transmission = DataNormalizer.normalize_transmission(cleaned.transmission)
                cleaned.owner_type = DataNormalizer.normalize_owner(cleaned.owner_type)
                cleaned.city = DataNormalizer.normalize_city(cleaned.city)
                
                # 3. Validate
                valid, error = DataValidator.validate_listing(cleaned)
                if not valid:
                    self.metrics['validation_failures'] += 1
                    logger.debug(f"Validation failed: {error}")
                    continue
                
                # 4. Generate hash for deduplication
                hash_input = f"{cleaned.brand}_{cleaned.model}_{cleaned.year}_{cleaned.price}_{cleaned.kilometers}"
                listing_hash = hashlib.sha256(hash_input.encode()).hexdigest()
                
                # 5. Check for duplicates
                if listing_hash in seen_hashes:
                    self.metrics['duplicates_found'] += 1
                    continue
                
                seen_hashes.add(listing_hash)
                
                # 6. Create CleanListing
                clean = CleanListing(
                    source=cleaned.source,
                    brand=cleaned.brand,
                    model=cleaned.model,
                    variant=cleaned.variant,
                    year=cleaned.year,
                    fuel=cleaned.fuel,
                    transmission=cleaned.transmission,
                    body_type=cleaned.body_type,
                    owner_type=cleaned.owner_type,
                    price=cleaned.price,
                    kilometers=cleaned.kilometers or 0,
                    city=cleaned.city,
                    state=cleaned.state,
                    listing_url=cleaned.listing_url,
                    listing_id=cleaned.listing_id,
                    listing_hash=listing_hash
                )
                
                clean_listings.append(clean)
                
            except Exception as e:
                logger.error(f"Error transforming listing: {e}")
                self.metrics['validation_failures'] += 1
                continue
        
        return clean_listings
    
    def aggregate(self, clean_listings: List[CleanListing]) -> List:
        """Aggregate phase - calculate market statistics"""
        return MarketAggregator.aggregate(clean_listings)
    
    def load(self, clean_listings: List[CleanListing], statistics: List):
        """Load phase - insert into database"""
        # Load listings
        loaded_listings = DatabaseLoader.load_listings(clean_listings)
        self.metrics['listings_loaded'] = loaded_listings
        
        # Load statistics
        loaded_stats = DatabaseLoader.load_statistics(statistics)
        logger.info(f"Loaded {loaded_stats} statistics")
    
    def print_summary(self):
        """Print pipeline execution summary"""
        print("\n" + "="*60)
        print("ETL PIPELINE EXECUTION SUMMARY")
        print("="*60)
        print(f"Run ID: {self.run_id}")
        print(f"Duration: {self.metrics['duration_seconds']} seconds")
        print(f"Listings Extracted: {self.metrics['listings_extracted']}")
        print(f"Listings Transformed: {self.metrics['listings_transformed']}")
        print(f"Listings Loaded: {self.metrics['listings_loaded']}")
        print(f"Duplicates Found: {self.metrics['duplicates_found']}")
        print(f"Validation Failures: {self.metrics['validation_failures']}")
        print("="*60 + "\n")


if __name__ == "__main__":
    pipeline = ETLPipeline()
    pipeline.run()
