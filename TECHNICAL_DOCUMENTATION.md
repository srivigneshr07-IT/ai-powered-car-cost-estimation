# Technical Documentation

**AI-Powered Dynamic Used Car Valuation System**

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        USER INTERFACE                        │
│                    (React Frontend - HTML/JS)                │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTP/JSON
                         ↓
┌─────────────────────────────────────────────────────────────┐
│                      FASTAPI BACKEND                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │  Prediction  │  │   Market     │  │   Dynamic    │     │
│  │   Service    │  │ Intelligence │  │   Pricing    │     │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘     │
│         │                  │                  │              │
│         ↓                  ↓                  ↓              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   XGBoost    │  │   Query      │  │  Weighting   │     │
│  │   ML Model   │  │   Engine     │  │   Engine     │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└────────────────────────┬────────────────────────────────────┘
                         │ SQL
                         ↓
┌─────────────────────────────────────────────────────────────┐
│              POSTGRESQL DATABASE (AWS RDS)                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │market_prices │  │market_stats  │  │pipeline_logs │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└────────────────────────┬────────────────────────────────────┘
                         ↑
                         │ UPSERT
                         │
┌─────────────────────────────────────────────────────────────┐
│                      ETL PIPELINE                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Extract    │→ │  Transform   │→ │     Load     │     │
│  │  (Scrapers)  │  │  (Cleaning)  │  │  (Database)  │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│         ↑                                                    │
│         │ HTTP Requests                                     │
│         │                                                    │
│  ┌──────────────┐  ┌──────────────┐                       │
│  │   Cars24     │  │   CarDekho   │                       │
│  │   Website    │  │   Website    │                       │
│  └──────────────┘  └──────────────┘                       │
└─────────────────────────────────────────────────────────────┘
```

---

## Technology Stack

### Frontend
- **HTML5/CSS3:** User interface
- **JavaScript (Vanilla):** Client-side logic
- **Fetch API:** HTTP requests

### Backend
- **Python 3.12:** Programming language
- **FastAPI:** Web framework
- **Uvicorn:** ASGI server
- **Pydantic:** Data validation

### Machine Learning
- **XGBoost:** Gradient boosting model
- **Scikit-learn:** Preprocessing
- **Pandas:** Data manipulation
- **NumPy:** Numerical operations

### Database
- **PostgreSQL 15:** Relational database
- **SQLAlchemy:** ORM
- **AWS RDS:** Managed database service

### Web Scraping
- **Requests:** HTTP library
- **BeautifulSoup4:** HTML parsing
- **lxml:** XML/HTML parser

### AWS Services
- **RDS:** Database hosting
- **Bedrock:** AI image analysis (optional)

---

## Database Schema

### Table: market_prices

```sql
CREATE TABLE market_prices (
    id SERIAL PRIMARY KEY,
    source VARCHAR(50) NOT NULL,
    listing_id VARCHAR(100),
    listing_url TEXT,
    brand VARCHAR(100) NOT NULL,
    model VARCHAR(100) NOT NULL,
    variant VARCHAR(200),
    year INTEGER NOT NULL,
    fuel VARCHAR(50),
    transmission VARCHAR(50),
    body_type VARCHAR(50),
    owner_type VARCHAR(50),
    price INTEGER NOT NULL,
    kilometers INTEGER,
    city VARCHAR(100) NOT NULL,
    state VARCHAR(100),
    scraped_at TIMESTAMP DEFAULT NOW(),
    created_at TIMESTAMP DEFAULT NOW(),
    last_seen_at TIMESTAMP DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE,
    listing_hash VARCHAR(64) UNIQUE,
    
    INDEX idx_brand_model_year_city (brand, model, year, city),
    INDEX idx_last_seen_at (last_seen_at),
    INDEX idx_city (city),
    INDEX idx_brand (brand)
);
```

### Table: market_statistics

```sql
CREATE TABLE market_statistics (
    id SERIAL PRIMARY KEY,
    brand VARCHAR(100) NOT NULL,
    model VARCHAR(100) NOT NULL,
    city VARCHAR(100) NOT NULL,
    year_min INTEGER,
    year_max INTEGER,
    sample_size INTEGER,
    avg_price NUMERIC,
    median_price NUMERIC,
    min_price INTEGER,
    max_price INTEGER,
    avg_kilometers NUMERIC,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    INDEX idx_brand_model_city (brand, model, city)
);
```

### Table: pipeline_logs

```sql
CREATE TABLE pipeline_logs (
    id SERIAL PRIMARY KEY,
    pipeline_run_id VARCHAR(100) UNIQUE NOT NULL,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    duration_seconds INTEGER,
    status VARCHAR(50),
    listings_extracted INTEGER,
    listings_transformed INTEGER,
    listings_loaded INTEGER,
    duplicates_found INTEGER,
    validation_failures INTEGER,
    error_message TEXT
);
```

---

## Dynamic Pricing Algorithm

### Formula

```python
if confidence == "high":
    weights = {
        "ml": 0.60,
        "market_avg": 0.25,
        "market_median": 0.15
    }
elif confidence == "medium":
    weights = {
        "ml": 0.70,
        "market_avg": 0.20,
        "market_median": 0.10
    }
elif confidence == "low":
    weights = {
        "ml": 0.85,
        "market_avg": 0.10,
        "market_median": 0.05
    }
else:  # none
    weights = {
        "ml": 1.0,
        "market_avg": 0.0,
        "market_median": 0.0
    }

final_price = (
    weights["ml"] * ml_prediction +
    weights["market_avg"] * market_average +
    weights["market_median"] * market_median
)
```

### Confidence Calculation

```python
def calculate_confidence(sample_size):
    if sample_size >= 10:
        return "high"
    elif sample_size >= 5:
        return "medium"
    elif sample_size >= 2:
        return "low"
    elif sample_size == 1:
        return "very_low"
    else:
        return "none"
```

---

## ETL Pipeline

### Extract Phase

```python
# For each source (Cars24, CarDekho):
for city in cities:
    for page in range(1, max_pages + 1):
        url = build_url(source, city, page)
        html = requests.get(url)
        listings = parse_html(html)
        raw_listings.extend(listings)
        time.sleep(2)  # Rate limiting
```

### Transform Phase

```python
for listing in raw_listings:
    # 1. Clean data
    cleaned = clean_listing(listing)
    
    # 2. Normalize
    cleaned.brand = normalize_brand(cleaned.brand)
    cleaned.fuel = normalize_fuel(cleaned.fuel)
    
    # 3. Validate
    if not validate_listing(cleaned):
        continue
    
    # 4. Generate hash for deduplication
    listing_hash = generate_hash(cleaned)
    
    # 5. Check duplicates
    if listing_hash in seen_hashes:
        duplicates += 1
        continue
    
    clean_listings.append(cleaned)
```

### Load Phase

```python
# UPSERT logic
for listing in clean_listings:
    stmt = insert(MarketPrice).values(**listing)
    stmt = stmt.on_conflict_do_update(
        index_elements=['listing_hash'],
        set_={
            'price': listing['price'],
            'last_seen_at': datetime.now()
        }
    )
    session.execute(stmt)
```

---

## API Request Flow

### 1. User Submits Form

```javascript
fetch('/predict', {
    method: 'POST',
    body: JSON.stringify(carData)
})
```

### 2. Backend Receives Request

```python
@app.post("/predict")
def predict(vehicle: VehicleInput):
    # Validate input
    payload = vehicle.model_dump()
```

### 3. ML Prediction

```python
# Load model and predict
ml_price = predict_price(input_df)
```

### 4. Market Intelligence Query

```python
# Query database for similar cars
insights = market_intelligence.get_market_insights(
    brand, model, year, city
)
```

### 5. Dynamic Pricing

```python
# Combine ML + Market
result = pricing_engine.get_dynamic_price(
    ml_prediction=ml_price,
    brand=brand,
    model=model,
    year=year,
    city=city
)
```

### 6. Return Response

```python
return {
    "predicted_price": result["final_price"],
    "ml_prediction": ml_price,
    "market_average": insights["average"],
    "market_confidence": insights["confidence"],
    ...
}
```

---

## Performance Considerations

### Database Indexes

```sql
-- Critical indexes for fast queries
CREATE INDEX idx_brand_model_year_city ON market_prices(brand, model, year, city);
CREATE INDEX idx_last_seen_at ON market_prices(last_seen_at);
CREATE INDEX idx_listing_hash ON market_prices(listing_hash);
```

### Query Optimization

```python
# Use freshness filter
cutoff = datetime.now() - timedelta(days=30)
query = query.filter(MarketPrice.last_seen_at >= cutoff)

# Limit results
query = query.limit(100)
```

### Caching (Future)

```python
# Redis cache for frequent queries
@cache(ttl=3600)  # 1 hour
def get_market_insights(brand, model, city):
    ...
```

---

## Security Considerations

### Current State (Development)
- No authentication
- No rate limiting
- CORS enabled for all origins

### Production Recommendations
- Add API key authentication
- Implement rate limiting (100 req/min)
- Restrict CORS to specific domains
- Use HTTPS only
- Sanitize all inputs
- Add request logging
- Implement API versioning

---

## Deployment Architecture

### Development
```
Local Machine
├── Backend (localhost:8000)
├── Frontend (localhost:5500)
└── Database (AWS RDS)
```

### Production (Recommended)
```
AWS Infrastructure
├── EC2/ECS: Backend (FastAPI)
├── S3 + CloudFront: Frontend (Static)
├── RDS: Database (PostgreSQL)
├── EventBridge: Scheduled scraping
└── CloudWatch: Monitoring
```

---

## Environment Variables

```bash
# Database
POSTGRES_HOST=database-1.cgp62acck1rv.us-east-1.rds.amazonaws.com
POSTGRES_PORT=5432
POSTGRES_DB=car_valuation
POSTGRES_USER=postgres
POSTGRES_PASSWORD=<password>

# API
API_VERSION=v1
DEBUG=False
CORS_ORIGINS=https://yourdomain.com

# Scraping
MAX_PAGES_PER_CITY=20
DELAY_BETWEEN_REQUESTS=2
FRESHNESS_DAYS=30
```

---

## Monitoring & Logging

### Key Metrics to Track
- API response time
- Prediction accuracy
- Market data coverage
- Scraping success rate
- Database query performance
- Error rates

### Logging Levels
```python
DEBUG: Detailed information
INFO: General information
WARNING: Warning messages
ERROR: Error messages
CRITICAL: Critical failures
```

---

## Testing

### Unit Tests
```bash
pytest tests/unit/
```

### Integration Tests
```bash
pytest tests/integration/
```

### API Tests
```bash
pytest tests/api/
```

---

## Maintenance

### Weekly Tasks
- Run ETL pipeline
- Check data quality
- Review error logs
- Monitor API performance

### Monthly Tasks
- Database backup
- Performance optimization
- Security updates
- Dependency updates

---

## Troubleshooting

### Common Issues

**Issue:** Slow API response
**Solution:** Check database indexes, add caching

**Issue:** No market data
**Solution:** Run ETL pipeline, check scraping logs

**Issue:** Database connection error
**Solution:** Check RDS security group, verify credentials

---

**Last Updated:** June 23, 2026  
**Version:** 2.0
