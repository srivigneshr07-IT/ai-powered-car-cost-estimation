# 🧪 Testing & Review Guide

**Last Updated:** June 23, 2026 9:32 AM  
**System Status:** ✅ OPERATIONAL (95% Complete)

---

## Quick System Health Check

Run this command for instant status:
```bash
cd /home/sagemaker-user/ai-powered-car-final
python3 interactive_test.py
```

This launches an interactive menu with 6 options:
1. Database Status
2. Test Market Intelligence
3. Test Dynamic Pricing
4. View Sample Data
5. View Documentation
6. Run All Tests

---

## Manual Testing Commands

### 1. Check Database Status
```bash
cd /home/sagemaker-user/ai-powered-car-final
python3 -c "
from database.connection import get_session
from database.models import MarketPrice
with get_session() as session:
    print(f'Total listings: {session.query(MarketPrice).count()}')
"
```

### 2. Test Market Intelligence
```bash
python3 -c "
from market_intelligence import MarketIntelligence
mi = MarketIntelligence()
result = mi.get_market_insights('Maruti', 'Swift', 2018, 'Chennai')
print(f'Sample: {result[\"sample_size\"]} cars')
print(f'Confidence: {result[\"confidence\"]}')
print(f'Avg: ₹{result[\"statistics\"][\"average_price\"]:,}')
"
```

### 3. Test Dynamic Pricing
```bash
python3 -c "
from pricing import DynamicPricingEngine
engine = DynamicPricingEngine()
result = engine.get_dynamic_price(500000, 'Maruti', 'Swift', 2018, 'Chennai')
print(f'ML: ₹{result[\"pricing_breakdown\"][\"ml_prediction\"]:,}')
print(f'Final: ₹{result[\"final_price\"]:,}')
print(f'Confidence: {result[\"market_intelligence\"][\"confidence\"]}')
"
```

### 4. View Database (Interactive)
```bash
python3 view_database.py
```

### 5. View Database (Web Browser)
```bash
# Open this file in browser:
/home/sagemaker-user/ai-powered-car-final/rds_viewer.html
```

---

## Start Backend Server

```bash
cd /home/sagemaker-user/ai-powered-car-final/backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Then test endpoints:
```bash
# Test /predict endpoint
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "brand": "Maruti",
    "model": "Swift",
    "year": 2018,
    "city": "Chennai",
    "fuel_type": "Petrol",
    "transmission": "Manual",
    "owner_type": "First",
    "mileage": 50000,
    "engine": 1197,
    "power": 82,
    "seats": 5,
    "transaction_type": "selling"
  }'

# Test /market/insights endpoint
curl http://localhost:8000/market/insights?brand=Maruti&model=Swift&year=2018&city=Chennai

# Test /market/city endpoint
curl http://localhost:8000/market/city/Chennai

# Test /market/brand endpoint
curl http://localhost:8000/market/brand/Maruti?city=Chennai
```

---

## Test Frontend

1. Start backend server (see above)
2. Open frontend:
   ```bash
   # Open in browser:
   /home/sagemaker-user/ai-powered-car-final/frontend/index.html
   ```
3. Fill in car details and click "Get Valuation"
4. Check that Market Intelligence section displays correctly

---

## Run ETL Pipeline (Get More Data)

```bash
cd /home/sagemaker-user/ai-powered-car-final
python3 etl/run_pipeline.py
```

This will:
- Scrape Cars24 and CarDekho
- Process 15 cities × 20 pages = 300 pages
- Takes ~10-15 minutes
- Adds fresh listings to database

---

## View Documentation

### API Documentation
```bash
cat /home/sagemaker-user/ai-powered-car-final/API_DOCUMENTATION.md
```

### User Guide
```bash
cat /home/sagemaker-user/ai-powered-car-final/USER_GUIDE.md
```

### Technical Documentation
```bash
cat /home/sagemaker-user/ai-powered-car-final/TECHNICAL_DOCUMENTATION.md
```

### Test Report
```bash
cat /home/sagemaker-user/ai-powered-car-final/PHASE7.2_TEST_REPORT.md
```

---

## Current System Metrics

**Database:**
- Total Listings: 429
- Fresh Data: 100% (< 30 days)
- Cities: 10
- Brands: 20
- Sources: Cars24 (7.5%), CarDekho (92.5%)

**API Endpoints:**
- POST /predict (with dynamic pricing) ✅
- GET /market/insights ✅
- GET /market/city/{city} ✅
- GET /market/brand/{brand} ✅
- POST /market/compare-cities ✅

**Test Results:**
- Total Tests: 17
- Passed: 17 (100%)
- Failed: 0

**Documentation:**
- API_DOCUMENTATION.md (7 KB) ✅
- USER_GUIDE.md (7 KB) ✅
- TECHNICAL_DOCUMENTATION.md (13 KB) ✅
- README_V2.md (4 KB) ✅
- PHASE7.2_TEST_REPORT.md (6 KB) ✅

---

## Common Test Scenarios

### Scenario 1: Popular Car with Good Market Data
```python
from pricing import DynamicPricingEngine
engine = DynamicPricingEngine()

# Maruti Swift - should have high confidence
result = engine.get_dynamic_price(500000, 'Maruti', 'Swift', 2018, 'Chennai')
# Expected: Medium/High confidence, price adjustment based on market
```

### Scenario 2: Rare Car with No Market Data
```python
# BMW X5 - should fall back to ML-only
result = engine.get_dynamic_price(7500000, 'BMW', 'X5', 2023, 'Lucknow')
# Expected: None confidence, no price adjustment
```

### Scenario 3: Different Cities
```python
# Compare same car in different cities
cities = ['Chennai', 'Mumbai', 'Delhi', 'Bangalore']
for city in cities:
    result = engine.get_dynamic_price(500000, 'Maruti', 'Swift', 2018, city)
    print(f"{city}: ₹{result['final_price']:,}")
```

---

## Troubleshooting

### Database Connection Issues
```bash
# Check .env file
cat /home/sagemaker-user/ai-powered-car-final/.env

# Test connection
python3 -c "from database.connection import get_session; print('✅ Connected')"
```

### Backend Not Starting
```bash
# Check if port 8000 is in use
lsof -i :8000

# Install dependencies
cd /home/sagemaker-user/ai-powered-car-final/backend
pip install -r requirements.txt
```

### Frontend Not Showing Market Intelligence
```bash
# Check if backend is running
curl http://localhost:8000/health

# Check browser console for errors (F12)
```

---

## Next Steps

**Option 1: Deploy to Production**
- Phase 7.7: Deploy backend + frontend to AWS

**Option 2: Add Monitoring**
- Phase 7.4: Add logging, metrics, alerting

**Option 3: Schedule Scraping**
- Phase 7.5: Automate ETL pipeline with cron/EventBridge

**Option 4: Optimize Performance**
- Phase 7.6: Add Redis caching, optimize queries

**Option 5: Get More Data**
- Run ETL pipeline to scrape more listings

---

## Quick Reference

| Task | Command |
|------|---------|
| Interactive Test Menu | `python3 interactive_test.py` |
| Start Backend | `cd backend && uvicorn app.main:app --reload` |
| Run ETL Pipeline | `python3 etl/run_pipeline.py` |
| View Database | `python3 view_database.py` |
| Check Health | See commands above |

---

**System Status:** ✅ PRODUCTION READY  
**Completion:** 95%  
**All Tests:** 17/17 PASSED ✅
