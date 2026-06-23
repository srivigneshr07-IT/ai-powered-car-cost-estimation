# Phase 2 ETL Pipeline - Quick Reference

## 🚀 Quick Start

```bash
cd /home/sagemaker-user/ai-powered-car-final
python etl/run_pipeline.py
```

## 📊 What Gets Scraped

### 4 Sources
- **Cars24** (https://www.cars24.com)
- **CarDekho** (https://www.cardekho.com)
- **Spinny** (https://www.spinny.com)
- **OLX** (https://www.olx.in)

### 27 Brands
Maruti, Hyundai, Honda, Toyota, Mahindra, Tata, Kia, MG, Volkswagen, Skoda, Renault, Nissan, Ford, Jeep, BMW, Mercedes, Audi, Volvo, Jaguar, Land Rover, Mini, Porsche, Lexus, Isuzu, Citroen, BYD, Force

### 10 Cities
Chennai, Bangalore, Hyderabad, Mumbai, Delhi, Pune, Kolkata, Ahmedabad, Jaipur, Lucknow

## 📁 File Structure

```
etl/
├── config.py              # Configuration (brands, cities, sources)
├── models.py              # Pydantic models (RawListing, CleanListing)
├── run_pipeline.py        # Main orchestrator (run this!)
├── README.md              # Full documentation
│
├── extract/               # Source adapters
│   ├── base_adapter.py    # Abstract base class
│   ├── cars24_adapter.py
│   ├── cardekho_adapter.py
│   ├── spinny_adapter.py
│   └── olx_adapter.py
│
├── transform/             # Data transformation
│   ├── cleaner.py         # Remove symbols, convert types
│   ├── normalizer.py      # Standardize formats
│   └── validator.py       # Validate ranges
│
├── aggregate/             # Statistics calculation
│   └── aggregator.py      # Calculate avg, median, min, max
│
├── load/                  # Database operations
│   └── database_loader.py # UPSERT into PostgreSQL
│
└── utils/                 # Utilities
    └── logger.py          # Structured logging
```

## 🔄 Data Flow

```
Extract → Transform → Aggregate → Load
  ↓          ↓           ↓         ↓
Raw      Clean      Statistics  PostgreSQL
Listings Listings   (grouped)   (market_statistics)
```

## 🎯 Key Features

1. **Multi-Source**: Scrapes from 4 websites simultaneously
2. **Data Cleaning**: Removes ₹, commas, converts "4.5 Lakh" → 450000
3. **Normalization**: "Maruti Suzuki" → "Maruti", "petrol" → "Petrol"
4. **Validation**: Price (50k-50M), KM (0-500k), Year (1990-2026)
5. **Deduplication**: SHA256 hash-based duplicate detection
6. **Aggregation**: Groups by (brand, model, year, city, fuel, transmission)
7. **UPSERT**: Updates existing records, inserts new ones

## 📈 Output

### Database Tables Updated
- `market_prices`: Individual listings
- `market_statistics`: Aggregated statistics (avg, median, min, max)
- `pipeline_logs`: Execution history
- `market_sources`: Source health tracking

### Console Output
```
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

## ⚙️ Configuration

Edit `etl/config.py` to:
- Add/remove brands: `SUPPORTED_BRANDS`
- Add/remove cities: `SUPPORTED_CITIES`
- Enable/disable sources: `SOURCES`
- Adjust validation rules: `VALIDATION_RULES`
- Modify normalization: `BRAND_MAPPING`, `FUEL_MAPPING`, etc.

## 🧪 Testing

```bash
# Test setup
python test_etl_setup.py

# Test with limited scope
python -c "
from etl.run_pipeline import ETLPipeline
pipeline = ETLPipeline()
pipeline.run(cities=['Chennai'], sources=['cars24'])
"
```

## 🔧 Customization

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

### Run for Specific Cities and Sources
```python
pipeline.run(cities=['Chennai'], sources=['cars24', 'cardekho'])
```

## 🚨 Troubleshooting

### No listings extracted
- Check internet connection
- Verify website URLs are accessible
- Website structure may have changed (update selectors)

### High validation failures
- Review logs for specific errors
- Adjust VALIDATION_RULES in config.py if needed

### Database connection errors
- Verify PostgreSQL credentials in .env
- Check database is running
- Verify tables exist (run test_database_setup.py)

## 📝 Next Steps

After ETL pipeline is working:
1. **Phase 4**: Market Intelligence Engine
2. **Phase 5**: Dynamic Pricing Engine (60% ML + 25% Avg + 15% Median)
3. **Phase 6**: Extend FastAPI `/predict` endpoint

## 📚 Documentation

- Full documentation: `etl/README.md`
- Phase 2 completion: `PHASE2_COMPLETE.md`
- Database setup: `PHASE3_COMPLETE.md`

## ✅ Status

**Phase 2: COMPLETE**
- [x] 4 source adapters implemented
- [x] Transform layer (clean, normalize, validate)
- [x] Aggregator (calculate statistics)
- [x] Database loader (UPSERT logic)
- [x] Main orchestrator
- [x] Configuration management
- [x] Documentation
- [x] All 27 brands supported
- [x] 10 cities supported
