# Database Module

PostgreSQL database layer for AI-Powered Dynamic Used Car Valuation System.

## Overview

This module provides database connectivity, ORM models, and schema management for the market intelligence layer.

## Tables

### 1. market_prices
**Purpose:** Store raw scraped car listings from various sources

**Key Columns:**
- `source` - Data source (cardekho, olx, cars24)
- `brand`, `model`, `variant` - Vehicle identification
- `year`, `fuel`, `transmission`, `body_type` - Specifications
- `price`, `kilometers` - Pricing and condition
- `city`, `state` - Location
- `listing_hash` - MD5 hash for duplicate detection
- `is_active` - Listing validity status

**Indexes:** Optimized for queries by brand, model, year, city, price

### 2. market_statistics
**Purpose:** Pre-calculated aggregated statistics for fast queries

**Key Columns:**
- `brand`, `model`, `year`, `city`, `fuel`, `transmission` - Grouping keys
- `avg_price`, `median_price`, `min_price`, `max_price` - Statistics
- `listing_count` - Sample size
- `calculated_at` - Freshness timestamp

**Unique Constraint:** One record per unique combination of grouping keys

### 3. prediction_logs
**Purpose:** Audit trail of all price predictions

**Key Columns:**
- All input features (brand, model, year, km, etc.)
- `ml_base_price` - XGBoost prediction
- `market_average`, `market_median` - Market data
- `final_price` - Dynamic pricing result
- `confidence_score` - Prediction confidence
- `predicted_at` - Timestamp

### 4. market_sources
**Purpose:** Track scraping sources and their health

**Key Columns:**
- `source_name` - Unique source identifier
- `is_active` - Currently scraping or disabled
- `last_scraped_at` - Last successful scrape
- `total_listings_scraped` - Lifetime count
- `success_rate` - Scraping reliability metric

### 5. pipeline_logs
**Purpose:** ETL execution history and monitoring

**Key Columns:**
- `pipeline_run_id` - UUID for each run
- `started_at`, `completed_at`, `duration_seconds` - Timing
- `status` - success, failed, partial
- `listings_extracted`, `listings_transformed`, `listings_loaded` - Metrics
- `error_message`, `error_stacktrace` - Debugging info

## Setup

### 1. Install Dependencies
```bash
pip install psycopg2-binary sqlalchemy python-dotenv
```

### 2. Configure Environment
Create `.env` file:
```env
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=car_valuation
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password
```

### 3. Create Database
```bash
# Using psql
psql -U postgres -c "CREATE DATABASE car_valuation;"

# Or using Python
python -c "from database.connection import create_all_tables; create_all_tables()"
```

### 4. Run Migration (Optional)
```bash
psql -U postgres -d car_valuation -f database/migrations/001_initial_schema.sql
```

## Usage

### Test Connection
```python
from database.connection import test_connection

if test_connection():
    print("Database ready!")
```

### Create Tables
```python
from database.connection import create_all_tables

create_all_tables()
```

### Query Data
```python
from database.connection import get_session
from database.models import MarketPrice

with get_session() as session:
    listings = session.query(MarketPrice)\
        .filter(MarketPrice.brand == "Maruti")\
        .filter(MarketPrice.model == "Swift")\
        .filter(MarketPrice.city == "Mumbai")\
        .all()
    
    for listing in listings:
        print(f"{listing.year} {listing.brand} {listing.model} - ₹{listing.price}")
```

### Insert Data
```python
from database.connection import get_session
from database.models import MarketPrice
import hashlib

with get_session() as session:
    listing = MarketPrice(
        source="cardekho",
        brand="Maruti",
        model="Swift",
        year=2019,
        price=650000,
        kilometers=45000,
        city="Mumbai",
        fuel="Petrol",
        transmission="Manual",
        listing_hash=hashlib.md5(b"unique_key").hexdigest()
    )
    session.add(listing)
    # Commit happens automatically on context exit
```

### Batch Insert
```python
from database.connection import get_session
from database.models import MarketPrice

listings = [
    {"source": "olx", "brand": "Honda", "model": "City", ...},
    {"source": "cars24", "brand": "Hyundai", "model": "i20", ...},
]

with get_session() as session:
    session.bulk_insert_mappings(MarketPrice, listings)
```

## Schema Diagram

```
market_prices (raw data)
    ↓ (aggregated)
market_statistics (pre-calculated)
    ↓ (queried during prediction)
prediction_logs (audit trail)

market_sources (tracks scrapers)
    ↓ (referenced in market_prices.source)
market_prices

pipeline_logs (tracks ETL runs)
```

## Maintenance

### Check Data Freshness
```sql
SELECT 
    source,
    COUNT(*) as total,
    MAX(scraped_at) as last_scrape
FROM market_prices
WHERE is_active = TRUE
GROUP BY source;
```

### Recalculate Statistics
```sql
-- This will be automated in Phase 4
SELECT 
    brand, model, year, city,
    AVG(price)::INTEGER as avg_price,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY price)::INTEGER as median_price,
    MIN(price) as min_price,
    MAX(price) as max_price,
    COUNT(*) as listing_count
FROM market_prices
WHERE is_active = TRUE
GROUP BY brand, model, year, city;
```

### Archive Old Data
```sql
-- Mark listings older than 90 days as inactive
UPDATE market_prices
SET is_active = FALSE
WHERE scraped_at < NOW() - INTERVAL '90 days';
```

## Performance Tips

1. **Indexes are crucial** - All common query patterns are indexed
2. **Use connection pooling** - Already configured in `connection.py`
3. **Batch operations** - Use `bulk_insert_mappings` for large inserts
4. **Regular VACUUM** - Run `VACUUM ANALYZE` periodically
5. **Monitor query performance** - Set `echo=True` in engine for debugging

## Next Steps

After Phase 3 completion:
- **Phase 2:** Build ETL pipeline to populate `market_prices`
- **Phase 4:** Implement market intelligence engine to calculate `market_statistics`
- **Phase 5:** Build dynamic pricing engine to query statistics
- **Phase 6:** Expose data via FastAPI endpoints
