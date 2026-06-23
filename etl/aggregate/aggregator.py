"""
Market Statistics Aggregator
Calculates avg, median, min, max from cleaned listings
"""

from typing import List
from datetime import datetime
import statistics
from collections import defaultdict
from etl.models import CleanListing, MarketStatistics


class MarketAggregator:
    """Aggregate listings into market statistics"""
    
    @staticmethod
    def aggregate(listings: List[CleanListing]) -> List[MarketStatistics]:
        """
        Aggregate listings by (brand, model, year, city, fuel, transmission)
        Calculate avg, median, min, max, std_dev, count
        """
        # Group listings
        groups = defaultdict(list)
        
        for listing in listings:
            key = (
                listing.brand,
                listing.model,
                listing.year,
                listing.city or "Unknown",
                listing.fuel or "Unknown",
                listing.transmission or "Unknown"
            )
            groups[key].append(listing.price)
        
        # Calculate statistics for each group
        stats_list = []
        
        for key, prices in groups.items():
            if len(prices) == 0:
                continue
            
            brand, model, year, city, fuel, transmission = key
            
            # Get date range
            listing_dates = [l.scraped_at for l in listings if 
                           l.brand == brand and l.model == model and l.year == year]
            data_start = min(listing_dates) if listing_dates else datetime.utcnow()
            data_end = max(listing_dates) if listing_dates else datetime.utcnow()
            
            stats = MarketStatistics(
                brand=brand,
                model=model,
                year=year,
                city=city if city != "Unknown" else None,
                fuel=fuel if fuel != "Unknown" else None,
                transmission=transmission if transmission != "Unknown" else None,
                avg_price=int(statistics.mean(prices)),
                median_price=int(statistics.median(prices)),
                min_price=min(prices),
                max_price=max(prices),
                std_dev=statistics.stdev(prices) if len(prices) > 1 else 0.0,
                listing_count=len(prices),
                calculated_at=datetime.utcnow(),
                data_start_date=data_start,
                data_end_date=data_end
            )
            
            stats_list.append(stats)
        
        return stats_list
