# AI-Powered Dynamic Used Car Valuation System

**Version 2.0** | **Status: Production Ready** ✅

An intelligent car price prediction system that combines XGBoost machine learning with real-time market intelligence from web scraping to provide accurate, market-aware valuations.

---

## 🎯 Key Features

### 1. **Hybrid Pricing Model**
- **XGBoost ML Model:** Trained on historical car sales data
- **Real-Time Market Intelligence:** Live data from Cars24 & CarDekho
- **Dynamic Weighting:** Confidence-based combination (60-100% ML, 0-40% Market)

### 2. **Market Intelligence Dashboard**
- View ML prediction vs Market average vs Final price
- Confidence indicators (High/Medium/Low/None)
- Sample size transparency
- Price adjustment breakdown

### 3. **Comprehensive Coverage**
- **429+ Car Listings:** Across 10 major cities
- **20+ Brands:** Maruti, Hyundai, Honda, Kia, and more
- **100% Fresh Data:** All listings < 30 days old
- **Automatic Updates:** Weekly scraping pipeline

### 4. **Smart Features**
- AI-powered damage detection (AWS Bedrock)
- Transaction-specific pricing (Buying/Selling)
- City-wise price comparison
- Confidence-based recommendations

---

## 🏗️ Architecture

```
User Interface (React Frontend)
         ↓
FastAPI Backend
    ├── XGBoost ML Model (60-100%)
    ├── Market Intelligence (0-40%)
    └── Dynamic Pricing Engine
         ↓
PostgreSQL Database (AWS RDS)
         ↑
ETL Pipeline (Web Scraping)
    ├── Cars24
    └── CarDekho
```

---

## 📊 System Performance

| Metric | Value |
|--------|-------|
| Total Listings | 429 |
| Cities Covered | 10 |
| Brands Covered | 20 |
| Data Freshness | 100% (< 30 days) |
| API Response Time | < 500ms |
| Test Coverage | 17/17 passed |

---

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- PostgreSQL 15+
- AWS RDS access

### Installation

```bash
# Clone repository
git clone <repository-url>
cd ai-powered-car-final

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your database credentials

# Run backend
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Open frontend
# Navigate to frontend/index.html in browser
```

---

## 📚 Documentation

- **[API Documentation](API_DOCUMENTATION.md)** - Complete API reference
- **[User Guide](USER_GUIDE.md)** - How to use the system
- **[Technical Documentation](TECHNICAL_DOCUMENTATION.md)** - Architecture & implementation
- **[Phase 7 Checklist](PHASE7_CHECKLIST.md)** - Development progress
- **[Test Report](PHASE7.2_TEST_REPORT.md)** - Testing results

---

## 📈 Project Phases

- [x] **Phase 1:** XGBoost ML Model + Backend + Frontend
- [x] **Phase 2:** ETL Pipeline (Web Scraping)
- [x] **Phase 3:** PostgreSQL Database (AWS RDS)
- [x] **Phase 4:** Market Intelligence Engine
- [x] **Phase 5:** Dynamic Pricing Engine
- [x] **Phase 6:** API Integration
- [x] **Phase 7.1:** Frontend Updates
- [x] **Phase 7.2:** Testing & Validation
- [x] **Phase 7.3:** Documentation
- [ ] **Phase 7.7:** Production Deployment

**Progress:** 95% Complete

---

## 🧪 Testing

**Test Results:** 17/17 passed (100%)

---

## 📊 API Endpoints

### Core Endpoints
- `POST /predict` - Get car price prediction
- `GET /market/insights` - Get market insights
- `GET /market/city/{city}` - City market overview
- `GET /market/brand/{brand}` - Brand insights
- `POST /market/compare-cities` - Compare prices across cities

See [API Documentation](API_DOCUMENTATION.md) for details.

---

## 🔄 ETL Pipeline

### Data Sources
- **Cars24:** 7.5% of listings
- **CarDekho:** 92.5% of listings

### Pipeline Schedule
- **Frequency:** Weekly
- **Duration:** ~30-40 minutes
- **Cities:** 10 major Indian cities
- **Freshness:** 30-day rolling window

### Run Manually
```bash
python etl/run_pipeline.py
```

---

## 🔧 Technology Stack

**Frontend:** HTML5, CSS3, JavaScript  
**Backend:** Python, FastAPI, Uvicorn  
**ML:** XGBoost, Scikit-learn, Pandas  
**Database:** PostgreSQL (AWS RDS)  
**Scraping:** Requests, BeautifulSoup4  
**Cloud:** AWS RDS, AWS Bedrock

---

**Last Updated:** June 23, 2026  
**Version:** 2.0  
**Status:** Production Ready ✅
