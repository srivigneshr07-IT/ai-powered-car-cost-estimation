# ETL Pipeline Architecture - Visual Overview

## Complete System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         AI-POWERED CAR VALUATION SYSTEM                      │
│                              (Enterprise Architecture)                       │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                              PHASE 1: ML LAYER                               │
│                              ✅ COMPLETED                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  User Input → FastAPI → XGBoost Model (R² 0.94) → Base Price → Frontend    │
│                                                                              │
│  • Vanilla JavaScript Frontend                                              │
│  • FastAPI Backend (main.py, predictor.py)                                  │
│  • XGBoost Regression Model                                                 │
│  • AWS Bedrock Vision (damage detection)                                    │
│  • SQLite (vehicle catalog)                                                 │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                         PHASE 2: ETL PIPELINE                                │
│                              ✅ COMPLETED                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  1. EXTRACT (Source Adapters)                                       │   │
│  │     ├── Cars24Adapter    → RawListing[]                             │   │
│  │     ├── CarDekhoAdapter  → RawListing[]                             │   │
│  │     ├── SpinnyAdapter    → RawListing[]                             │   │
│  │     └── OLXAdapter       → RawListing[]                             │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    ↓                                         │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  2. TRANSFORM                                                        │   │
│  │     ├── DataCleaner      → Remove ₹, commas, convert types          │   │
│  │     ├── DataNormalizer   → "Maruti Suzuki" → "Maruti"              │   │
│  │     └── DataValidator    → Validate price/km/year ranges            │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    ↓                                         │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  3. AGGREGATE                                                        │   │
│  │     └── MarketAggregator → Group by (brand, model, year, city)      │   │
│  │                            Calculate: avg, median, min, max, count   │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    ↓                                         │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  4. LOAD (PostgreSQL)                                                │   │
│  │     ├── market_prices (individual listings)                          │   │
│  │     ├── market_statistics (aggregated stats)                         │   │
│  │     ├── pipeline_logs (execution history)                            │   │
│  │     └── market_sources (source health)                               │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│  Execution: python etl/run_pipeline.py                                      │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                         PHASE 3: DATABASE LAYER                              │
│                              ✅ COMPLETED                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  AWS RDS PostgreSQL (database-1.cgp62acck1rv.us-east-1.rds.amazonaws.com)  │
│                                                                              │
│  Tables:                                                                     │
│  ├── market_prices       (raw scraped listings)                             │
│  ├── market_statistics   (aggregated market data)                           │
│  ├── prediction_logs     (audit trail)                                      │
│  ├── market_sources      (scraper health)                                   │
│  └── pipeline_logs       (ETL execution history)                            │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                    PHASE 4: MARKET INTELLIGENCE ENGINE                       │
│                              ⏳ PENDING                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  Query market_statistics table                                              │
│  Calculate market insights                                                   │
│  Provide API for dynamic pricing                                            │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                      PHASE 5: DYNAMIC PRICING ENGINE                         │
│                              ⏳ PENDING                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  User Input → XGBoost → Base Price                                          │
│                             ↓                                                │
│                  Query market_statistics                                     │
│                             ↓                                                │
│              Apply Business Rules:                                           │
│              60% ML + 25% Market Avg + 15% Market Median                    │
│                             ↓                                                │
│                      Final AI Valuation                                      │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                        PHASE 6: API INTEGRATION                              │
│                              ⏳ PENDING                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  Extend /predict endpoint                                                    │
│  Add market intelligence to response                                         │
│  Update frontend to display market data                                      │
│                                                                              │
│  Response:                                                                   │
│  {                                                                           │
│    "ml_base_price": 850000,                                                 │
│    "market_avg_price": 820000,                                              │
│    "market_median_price": 810000,                                           │
│    "final_price": 830000,                                                   │
│    "confidence": 85,                                                         │
│    "market_listings_count": 45                                              │
│  }                                                                           │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

## ETL Pipeline Details

### Supported Sources (4)
```
┌──────────────┬─────────────────────────────────────┐
│ Source       │ URL                                 │
├──────────────┼─────────────────────────────────────┤
│ Cars24       │ https://www.cars24.com              │
│ CarDekho     │ https://www.cardekho.com            │
│ Spinny       │ https://www.spinny.com              │
│ OLX          │ https://www.olx.in                  │
└──────────────┴─────────────────────────────────────┘
```

### Supported Brands (27)
```
Mass Market:     Maruti, Hyundai, Honda, Toyota, Tata, Mahindra, Kia
Mid-Range:       MG, Volkswagen, Skoda, Renault, Nissan, Ford, Jeep
Luxury:          BMW, Mercedes, Audi, Volvo, Jaguar, Land Rover
Premium:         Mini, Porsche, Lexus
Others:          Isuzu, Citroen, BYD, Force
```

### Supported Cities (10)
```
South:   Chennai, Bangalore, Hyderabad
West:    Mumbai, Pune, Ahmedabad
North:   Delhi, Jaipur, Lucknow
East:    Kolkata
```

### Data Transformation Examples
```
┌─────────────────────┬──────────────────────────────────┐
│ Input               │ Output                           │
├─────────────────────┼──────────────────────────────────┤
│ "₹ 8,50,000"        │ 850000 (int)                     │
│ "45,000 km"         │ 45000 (int)                      │
│ "Maruti Suzuki"     │ "Maruti" (normalized)            │
│ "petrol"            │ "Petrol" (normalized)            │
│ "manual"            │ "Manual" (normalized)            │
│ "1st owner"         │ "First" (normalized)             │
└─────────────────────┴──────────────────────────────────┘
```

### Validation Rules
```
┌─────────────┬──────────────┬──────────────┐
│ Field       │ Min          │ Max          │
├─────────────┼──────────────┼──────────────┤
│ Price       │ ₹50,000      │ ₹5,00,00,000 │
│ Kilometers  │ 0 km         │ 5,00,000 km  │
│ Year        │ 1990         │ 2026         │
└─────────────┴──────────────┴──────────────┘
```

### Market Statistics Grouping
```
Group By:
  ├── Brand (e.g., "Maruti")
  ├── Model (e.g., "Swift")
  ├── Year (e.g., 2020)
  ├── City (e.g., "Chennai")
  ├── Fuel (e.g., "Petrol")
  └── Transmission (e.g., "Manual")

Calculate:
  ├── Average Price
  ├── Median Price
  ├── Minimum Price
  ├── Maximum Price
  ├── Standard Deviation
  └── Listing Count
```

## Execution Flow

```
┌─────────────────────────────────────────────────────────────┐
│  $ python etl/run_pipeline.py                               │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│  1. Initialize adapters (Cars24, CarDekho, Spinny, OLX)     │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│  2. Extract: Scrape 4 sources × 5 cities × 3 pages          │
│     → ~1,200 raw listings                                    │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│  3. Transform: Clean, normalize, validate                    │
│     → ~1,100 clean listings (100 failed validation)         │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│  4. Aggregate: Group and calculate statistics                │
│     → ~450 market statistics records                         │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│  5. Load: UPSERT into PostgreSQL                             │
│     ├── market_prices: 1,100 records                         │
│     ├── market_statistics: 450 records                       │
│     ├── pipeline_logs: 1 record                              │
│     └── market_sources: 4 records updated                    │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│  ✅ Pipeline completed successfully                          │
│  Duration: 150 seconds                                       │
└─────────────────────────────────────────────────────────────┘
```

## Project Status

```
✅ Phase 1: ML Model & Backend (COMPLETE)
✅ Phase 2: ETL Pipeline (COMPLETE)
✅ Phase 3: PostgreSQL Database (COMPLETE)
⏳ Phase 4: Market Intelligence Engine (PENDING)
⏳ Phase 5: Dynamic Pricing Engine (PENDING)
⏳ Phase 6: API Integration (PENDING)
```

## Quick Commands

```bash
# Test ETL setup
python test_etl_setup.py

# Run full pipeline
python etl/run_pipeline.py

# Test database connection
python test_connection_quick.py

# Run backend server
cd backend && uvicorn app.main:app --reload

# Open frontend
cd frontend && python -m http.server 8000
```
