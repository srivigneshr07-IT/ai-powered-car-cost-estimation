# User Guide

**AI-Powered Dynamic Used Car Valuation System**

---

## Table of Contents

1. [Introduction](#introduction)
2. [Getting Started](#getting-started)
3. [Using the System](#using-the-system)
4. [Understanding Results](#understanding-results)
5. [Market Intelligence](#market-intelligence)
6. [Confidence Levels](#confidence-levels)
7. [FAQ](#faq)

---

## Introduction

This system helps you estimate the fair market price of used cars by combining:
- **AI Machine Learning:** Trained on thousands of car sales
- **Real Market Data:** Current listings from Cars24 and CarDekho
- **Smart Weighting:** Adjusts based on data availability

---

## Getting Started

### Accessing the System

1. Open your web browser
2. Navigate to: `http://localhost:5500/frontend/index.html`
3. You'll see the car valuation form

### What You'll Need

- Car brand and model
- Year of manufacture (or car age)
- Kilometers driven
- Fuel type (Petrol/Diesel/CNG/Electric)
- Transmission type (Manual/Automatic)
- City location
- Owner type (First/Second/Third)

---

## Using the System

### Step 1: Enter Car Details

Fill in the form with your car's information:

```
Brand: Maruti
Model: Swift
Variant: VXI
Year: 2018 (or Age: 6 years)
Fuel: Petrol
Transmission: Manual
Kilometers: 50,000
City: Chennai
Owner: First
```

### Step 2: Optional - Upload Images

- Upload car images for automatic detail extraction
- Upload damage images for damage cost estimation
- This is optional but improves accuracy

### Step 3: Submit

Click "Predict Vehicle Price" button

### Step 4: View Results

Results appear below the form showing:
- Final estimated price
- Market intelligence breakdown
- Confidence level
- Price adjustment details

---

## Understanding Results

### Price Display

```
┌─────────────────────────────────┐
│ Estimated Market Price          │
│                                 │
│ ₹ 4,65,775                      │
│                                 │
│ Market Value:    ₹ 4,65,775    │
│ Damage Cost:     ₹ 0           │
│ Confidence:      85%           │
└─────────────────────────────────┘
```

**What Each Means:**
- **Estimated Market Price:** Final recommended price
- **Market Value:** Price before damage deduction
- **Damage Cost:** Estimated repair cost (if damage detected)
- **Confidence:** How confident the system is (higher = better)

---

## Market Intelligence

### What You'll See

```
┌─────────────────────────────────────────┐
│ 📊 Market Intelligence                  │
│ 🟡 Medium Confidence                    │
│                                         │
│ ML Prediction    Market Avg   Market Med│
│ ₹5,00,000        ₹4,12,375    ₹3,33,000│
│                                         │
│ 📈 Based on 8 similar cars              │
│ ↘ Decreased by ₹34,225 (-6.84%)        │
└─────────────────────────────────────────┘
```

### Understanding the Breakdown

**ML Prediction:**
- What the AI model predicts based on car features
- Trained on historical sales data
- Doesn't know current market conditions

**Market Average:**
- Average price of similar cars currently listed
- From Cars24 and CarDekho
- Updated regularly

**Market Median:**
- Middle value of similar car prices
- Less affected by outliers
- More stable indicator

**Final Price:**
- Smart combination of ML + Market data
- Weighted based on confidence
- Most accurate estimate

---

## Confidence Levels

### 🟢 High Confidence (10+ similar cars)

```
Formula: 60% ML + 40% Market
Example: (60% × ₹5L) + (40% × ₹4.5L) = ₹4.8L
```

**What it means:**
- Lots of similar cars in market
- Very reliable estimate
- Safe to use for negotiations

---

### 🟡 Medium Confidence (5-9 similar cars)

```
Formula: 70% ML + 30% Market
Example: (70% × ₹5L) + (30% × ₹4.5L) = ₹4.85L
```

**What it means:**
- Some similar cars found
- Good estimate
- Compare with other sources

---

### 🟠 Low Confidence (2-4 similar cars)

```
Formula: 85% ML + 15% Market
Example: (85% × ₹5L) + (15% × ₹4.5L) = ₹4.925L
```

**What it means:**
- Few similar cars found
- Estimate less reliable
- Check multiple sources

---

### ⚪ No Market Data (0 similar cars)

```
Formula: 100% ML
Example: ₹5L (ML only)
```

**What it means:**
- No similar cars in database
- Rare or unique car
- Use as rough estimate only

---

## Price Adjustments

### Why Prices Get Adjusted

**Market is Higher:**
```
ML: ₹5,00,000
Market: ₹5,50,000
Final: ₹5,20,000 ↗ (+4%)
```
**Meaning:** Market demand is high, price increased

**Market is Lower:**
```
ML: ₹5,00,000
Market: ₹4,50,000
Final: ₹4,80,000 ↘ (-4%)
```
**Meaning:** Market supply is high, price decreased

---

## FAQ

### Q: Why is my price different from other websites?

**A:** We combine AI predictions with real market data. Other sites may use:
- Only historical data (outdated)
- Only current listings (no AI)
- Different data sources

Our hybrid approach is more accurate.

---

### Q: What if I see "No Market Data"?

**A:** This means:
- Your car is rare or unique
- Not enough similar cars in our database
- Price is based on ML model only

**Recommendation:** Check multiple sources for rare cars.

---

### Q: How often is market data updated?

**A:** 
- Database updated weekly
- Only uses listings from last 30 days
- Old/sold cars automatically excluded

---

### Q: Can I trust the confidence level?

**A:** Yes! Confidence is based on:
- Number of similar cars found
- Data freshness
- Price consistency

Higher confidence = more reliable estimate.

---

### Q: What cities are covered?

**A:** Currently 10 cities:
- Chennai
- Mumbai
- Delhi
- Bangalore
- Hyderabad
- Pune
- Kolkata
- Ahmedabad
- Jaipur
- Lucknow

More cities coming soon!

---

### Q: What if my city is not listed?

**A:** 
- System will still work
- Uses ML prediction only
- Less accurate than city-specific data

---

### Q: How accurate is the damage cost estimate?

**A:** 
- Based on AI image analysis
- Estimates visible damage only
- Get professional inspection for final quote

---

### Q: Can I use this for selling my car?

**A:** Yes! Use it to:
- Set asking price
- Negotiate with buyers
- Compare dealer offers
- Understand market value

---

### Q: Can I use this for buying a car?

**A:** Yes! Use it to:
- Verify seller's price is fair
- Negotiate better deals
- Avoid overpaying
- Compare multiple cars

---

## Tips for Best Results

### ✅ Do:
- Enter accurate information
- Upload clear car images
- Check confidence level
- Compare with other sources
- Use for negotiation guidance

### ❌ Don't:
- Rely solely on low confidence estimates
- Ignore market intelligence
- Use for rare/exotic cars without verification
- Expect exact selling price (market varies)

---

## Support

**Need Help?**
- Check FAQ above
- Review API documentation
- Contact support: [your-email@example.com]

**Found a Bug?**
- Report on GitHub
- Include car details and error message

---

**Last Updated:** June 23, 2026  
**Version:** 2.0
