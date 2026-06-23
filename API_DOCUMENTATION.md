# API Documentation

**AI-Powered Dynamic Used Car Valuation System**  
**Version:** 2.0  
**Base URL:** `http://localhost:8000`

---

## Overview

This API provides car price predictions using a combination of:
- XGBoost ML model (60-85% weight)
- Real-time market intelligence (15-40% weight)
- Confidence-based dynamic weighting

---

## Authentication

Currently no authentication required (add for production).

---

## Endpoints

### 1. POST /predict

**Description:** Get car price prediction with market intelligence

**Request:**
```json
{
  "brand": "Maruti",
  "model": "Swift",
  "variant": "VXI",
  "car_age": 6,
  "fuel_type": "Petrol",
  "transmission": "Manual",
  "owner_type": "first",
  "city": "Chennai",
  "kilometers": 50000,
  "damage_description": null,
  "transaction_type": "selling"
}
```

**Response:**
```json
{
  "predicted_price": 465775,
  "damage_cost": 0,
  "confidence_score": 85,
  "suggested_price": 465775,
  "currency": "INR",
  "model_version": "v1",
  "status": "success",
  "transaction_type": "selling",
  "transaction_price": 465775,
  "profit_margin": 0,
  "price_range_min": 0,
  "price_range_max": 0,
  "market_data_available": true,
  "ml_prediction": 500000,
  "market_average": 412375,
  "market_median": 333000,
  "market_confidence": "medium",
  "market_sample_size": 8
}
```

**Response Fields:**
- `predicted_price`: Final dynamic price (ML + Market combined)
- `ml_prediction`: Pure ML model prediction
- `market_average`: Average price from market data
- `market_median`: Median price from market data
- `market_confidence`: Confidence level (high/medium/low/none)
- `market_sample_size`: Number of similar cars found
- `market_data_available`: Whether market data was used

---

### 2. GET /market/insights

**Description:** Get market insights for a specific car

**Query Parameters:**
- `brand` (required): Car brand
- `model` (required): Car model
- `year` (required): Manufacturing year
- `city` (required): City name
- `fuel` (optional): Fuel type
- `transmission` (optional): Transmission type

**Example:**
```
GET /market/insights?brand=Maruti&model=Swift&year=2018&city=Chennai
```

**Response:**
```json
{
  "status": "success",
  "market_data_available": true,
  "sample_size": 8,
  "confidence": "medium",
  "statistics": {
    "average_price": 412375,
    "median_price": 333000,
    "min_price": 238000,
    "max_price": 666000,
    "price_range": 428000
  },
  "year_specific": {
    "sample_size": 1,
    "average_price": 333000,
    "median_price": 333000
  },
  "filters_applied": {
    "brand": "Maruti",
    "model": "Swift",
    "year": 2018,
    "city": "Chennai",
    "fuel": null,
    "transmission": null,
    "freshness_days": 30
  },
  "sample_listings": [
    {
      "price": 332000,
      "year": 2013,
      "kilometers": 93503,
      "source": "cars24",
      "last_seen": "2026-06-23 05:59:16.515852"
    }
  ]
}
```

---

### 3. GET /market/city/{city}

**Description:** Get overall market overview for a city

**Path Parameters:**
- `city` (required): City name

**Example:**
```
GET /market/city/Chennai
```

**Response:**
```json
{
  "status": "success",
  "city": "Chennai",
  "total_listings": 72,
  "average_price": 718167,
  "median_price": 450000,
  "price_range": {
    "min": 144000,
    "max": 5400000
  },
  "top_brands": [
    ["Maruti", 24],
    ["Honda", 12],
    ["Kia", 8]
  ]
}
```

---

### 4. GET /market/brand/{brand}

**Description:** Get market insights for a specific brand

**Path Parameters:**
- `brand` (required): Brand name

**Query Parameters:**
- `city` (optional): Filter by city

**Example:**
```
GET /market/brand/Hyundai?city=Mumbai
```

**Response:**
```json
{
  "status": "success",
  "brand": "Hyundai",
  "city": "Mumbai",
  "total_listings": 6,
  "average_price": 958333,
  "median_price": 1075000,
  "top_models": [
    ["Venue", 3],
    ["Creta", 2],
    ["Verna", 1]
  ]
}
```

---

### 5. POST /market/compare-cities

**Description:** Compare prices across multiple cities

**Request:**
```json
{
  "ml_prediction": 1000000,
  "brand": "Hyundai",
  "model": "Creta",
  "year": 2020,
  "cities": ["Chennai", "Mumbai", "Delhi", "Bangalore"]
}
```

**Response:**
```json
{
  "status": "success",
  "comparisons": {
    "Chennai": {
      "final_price": 986250,
      "confidence": "very_low",
      "sample_size": 1
    },
    "Mumbai": {
      "final_price": 1001100,
      "confidence": "low",
      "sample_size": 2
    },
    "Delhi": {
      "final_price": 1050833,
      "confidence": "low",
      "sample_size": 3
    },
    "Bangalore": {
      "final_price": 991400,
      "confidence": "very_low",
      "sample_size": 1
    }
  },
  "insights": {
    "best_deal": {
      "city": "Chennai",
      "price": 986250
    },
    "highest_price": {
      "city": "Delhi",
      "price": 1050833
    },
    "price_difference": 64583
  }
}
```

---

## Confidence Levels

| Confidence | Sample Size | ML Weight | Market Weight |
|------------|-------------|-----------|---------------|
| High       | 10+         | 60%       | 40%           |
| Medium     | 5-9         | 70%       | 30%           |
| Low        | 2-4         | 85%       | 15%           |
| Very Low   | 1           | 95%       | 5%            |
| None       | 0           | 100%      | 0%            |

---

## Error Responses

**400 Bad Request:**
```json
{
  "detail": "Invalid input parameters"
}
```

**404 Not Found:**
```json
{
  "detail": "Resource not found"
}
```

**500 Internal Server Error:**
```json
{
  "detail": "Internal server error: <error message>"
}
```

---

## Rate Limiting

Currently no rate limiting (add for production).

---

## Data Freshness

- Market data is filtered to last 30 days
- Listings older than 30 days are excluded from calculations
- Database is updated via scheduled scraping

---

## Example Usage (Python)

```python
import requests

# Predict car price
response = requests.post('http://localhost:8000/predict', json={
    "brand": "Maruti",
    "model": "Swift",
    "car_age": 6,
    "fuel_type": "Petrol",
    "transmission": "Manual",
    "city": "Chennai",
    "kilometers": 50000
})

result = response.json()
print(f"Final Price: ₹{result['predicted_price']:,}")
print(f"ML Prediction: ₹{result['ml_prediction']:,}")
print(f"Market Average: ₹{result['market_average']:,}")
print(f"Confidence: {result['market_confidence']}")
```

---

## Example Usage (JavaScript)

```javascript
// Predict car price
fetch('http://localhost:8000/predict', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        brand: "Maruti",
        model: "Swift",
        car_age: 6,
        fuel_type: "Petrol",
        transmission: "Manual",
        city: "Chennai",
        kilometers: 50000
    })
})
.then(response => response.json())
.then(data => {
    console.log(`Final Price: ₹${data.predicted_price.toLocaleString()}`);
    console.log(`Confidence: ${data.market_confidence}`);
});
```

---

## Support

For issues or questions, contact: [your-email@example.com]

**Last Updated:** June 23, 2026
