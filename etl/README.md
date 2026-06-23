# ETL Pipeline - Market Intelligence Layer

## Overview

This ETL pipeline scrapes real-time used car listings from 4 major sources, transforms the data, calculates market statistics, and loads them into PostgreSQL.

## Architecture

```
ETL Pipeline
├── Extract (Source Adapters)
│   ├── Cars24Adapter
│   ├── CarDekhoAdapter
│   ├── SpinnyAdapter
│   └── OLXAdapter
│
├── Transform
│   ├── DataCleaner (remove symbols, convert types)
│   ├── DataNormalizer (standardize brands/fuel/transmission)
│   └── DataValidator (validate ranges, required fields)
│
├── Aggregate
│   └── MarketAggregator (calculate avg, median, min, max, std_dev)
│
└── Load
    └── DatabaseLoader (UPSERT into PostgreSQL)
```

## Supported Sources

1. **Cars24** - https://www.cars24.com
2. **CarDekho** - https://www.cardekho.com
3. **Spinny** - https://www.spinny.com
4. **OLX** - https://www.olx.in

## Supported Brands (27)

Maruti, Hyundai, Honda, Toyota, Mahindra, Tata, Kia, MG, Volkswagen, Skoda, Renault, Nissan, Ford, Jeep, BMW, Mercedes, Audi, Volvo, Jaguar, Land Rover, Mini, Porsche, Lexus, Isuzu, Citroen, BYD, Force

## Supported Cities (10)

Chennai, Bangalore, Hyderabad, Mumbai, Delhi, Pune, Kolkata, Ahmedabad, Jaipur, Lucknow

## Execution

### Run Full Pipeline

```bash
cd /home/sagemaker-user/ai-powered-car-final
python etl/run_pipeline.py
```

### Run for Specific Cities

```python
from etl.run_pipeline import ETLPipeline

pipeline = ETLPipeline()
pipeline.run(cities=['Chennai', 'Bangalore'])
```

### Run for Specific Sources

```python
pipeline.run(sources=['cars24', 'olx'])
```

## Data Flow

### 1. Extract
- Scrapes listings from 4 sources
- Returns `RawListing` objects (unprocessed)

### 2. Transform
- **Clean**: Remove ₹, commas, convert "4.5 Lakh" → 450000
- **Normalize**: "Maruti Suzuki" → "Maruti", "petrol" → "Petrol"
- **Validate**: Price (50k-50M), KM (0-500k), Year (1990-2026)
- **Deduplicate**: Generate listing_hash, skip duplicates

### 3. Aggregate
- Group by: (brand, model, year, city, fuel, transmission)
- Calculate: avg_price, median_price, min_price, max_price, std_dev, count

### 4. Load
- **market_prices**: Individual listings (UPSERT on listing_hash)
- **market_statistics**: Aggregated stats (UPSERT on unique constraint)
- **pipeline_logs**: Execution metadata
- **market_sources**: Source health tracking

## Configuration

Edit `etl/config.py` to:
- Add/remove brands
- Add/remove cities
- Enable/disable sources
- Adjust validation rules
- Modify normalization mappings

## Output

### Console
```
2026-06-19 12:00:00 - etl_pipeline - INFO - Starting ETL Pipeline - Run ID: abc-123
2026-06-19 12:01:30 - etl_pipeline - INFO - Extracted 1,234 raw listings
2026-06-19 12:02:00 - etl_pipeline - INFO - Transformed 1,100 clean listings
2026-06-19 12:02:15 - etl_pipeline - INFO - Aggregated 450 market statistics
2026-06-19 12:02:30 - etl_pipeline - INFO - Loaded 1,100 listings
2026-06-19 12:02:30 - etl_pipeline - INFO - ETL Pipeline completed successfully

============================================================
ETL PIPELINE EXECUTION SUMMARY
============================================================
Run ID: abc-123
Duration: 150 seconds
Listings Extracted: 1,234
Listings Transformed: 1,100
Listings Loaded: 1,100
Duplicates Found: 78
Validation Failures: 56
============================================================
```

### Database
- `market_prices`: 1,100 new/updated listings
- `market_statistics`: 450 aggregated records
- `pipeline_logs`: 1 execution log
- `market_sources`: Updated metadata for 4 sources

## Error Handling

- Network errors: Logged, skipped, continue with next page
- Parsing errors: Logged, skipped, continue with next listing
- Validation failures: Counted, logged, excluded from load
- Database errors: Rolled back, logged, pipeline fails

## Best Practices

1. **Run manually** (not on every prediction)
2. **Schedule daily/weekly** (cron job or manual)
3. **Monitor logs** for scraping failures
4. **Check validation_failures** metric
5. **Verify market_statistics** table has recent data

## Extending the Pipeline

### Add New Source

1. Create `etl/extract/newsource_adapter.py`
2. Inherit from `BaseAdapter`
3. Implement `scrape()` and `extract_listing()`
4. Add to `etl/config.py` SOURCES
5. Add to `etl/run_pipeline.py` adapters dict

### Add New Brand

1. Add to `etl/config.py` SUPPORTED_BRANDS
2. Add to `etl/config.py` BRAND_MAPPING

### Add New City

1. Add to `etl/config.py` SUPPORTED_CITIES

## Troubleshooting

### No listings extracted
- Check internet connection
- Verify website URLs are accessible
- Check if website structure changed (update selectors)

### High validation failures
- Check VALIDATION_RULES in config.py
- Review logs for specific errors
- Adjust price/km/year ranges if needed

### Duplicates not detected
- Verify listing_hash generation logic
- Check if price/km changed (will create new hash)

## Next Steps (Phase 4 & 5)

After ETL pipeline is working:
1. **Phase 4**: Market Intelligence Engine (query statistics)
2. **Phase 5**: Dynamic Pricing Engine (60% ML + 25% Avg + 15% Median)
3. **Phase 6**: Extend FastAPI `/predict` endpoint
