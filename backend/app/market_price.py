"""
Real-time market price fetcher using SerpAPI (Google Search)
Safe, legal, and reliable
"""

import os
from serpapi import GoogleSearch
import re
from statistics import median

def extract_price_from_text(text):
    """Extract price in lakhs from text"""
    # Match patterns like "5.5 Lakh", "₹5,50,000", "550000"
    patterns = [
        r'₹?\s*(\d+\.?\d*)\s*[Ll]akh',
        r'₹?\s*(\d{1,2}),(\d{2}),(\d{3})',
        r'₹?\s*(\d{5,7})'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            if 'akh' in pattern.lower():
                return float(match.group(1)) * 100000
            elif ',' in pattern:
                return float(match.group(1) + match.group(2) + match.group(3))
            else:
                return float(match.group(1))
    return None

def get_market_prices_serpapi(brand, model, year, city, api_key=None):
    """
    Fetch real-time market prices using Google Search via SerpAPI
    
    Args:
        brand: Car brand (e.g., "Maruti")
        model: Car model (e.g., "Swift")
        year: Manufacturing year (e.g., 2019)
        city: City name (e.g., "Mumbai")
        api_key: SerpAPI key (or set SERPAPI_KEY env variable)
    
    Returns:
        dict with prices and sources
    """
    if not api_key:
        api_key = os.getenv('SERPAPI_KEY')
    
    if not api_key:
        return {
            "success": False,
            "error": "SerpAPI key not found. Set SERPAPI_KEY environment variable."
        }
    
    # Search query
    query = f"{brand} {model} {year} used car price {city}"
    
    try:
        params = {
            "q": query,
            "location": f"{city}, India",
            "hl": "en",
            "gl": "in",
            "api_key": api_key,
            "num": 10
        }
        
        search = GoogleSearch(params)
        results = search.get_dict()
        
        prices = []
        sources = []
        
        # Extract from organic results
        if "organic_results" in results:
            for result in results["organic_results"][:10]:
                title = result.get("title", "")
                snippet = result.get("snippet", "")
                link = result.get("link", "")
                
                # Extract price from title or snippet
                text = f"{title} {snippet}"
                price = extract_price_from_text(text)
                
                if price and 100000 <= price <= 50000000:  # 1L to 5Cr range
                    prices.append(price)
                    sources.append({
                        "price": price,
                        "source": result.get("displayed_link", ""),
                        "title": title,
                        "link": link
                    })
        
        if not prices:
            return {
                "success": False,
                "error": "No prices found in search results"
            }
        
        return {
            "success": True,
            "prices": prices,
            "average": sum(prices) / len(prices),
            "median": median(prices),
            "min": min(prices),
            "max": max(prices),
            "count": len(prices),
            "sources": sources[:5],  # Top 5 sources
            "query": query
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def get_hybrid_price(ml_price, brand, model, year, city, api_key=None):
    """
    Combine ML prediction with real-time market data
    
    Returns:
        Final adjusted price with confidence
    """
    market_data = get_market_prices_serpapi(brand, model, year, city, api_key)
    
    if not market_data["success"]:
        return {
            "final_price": ml_price,
            "confidence": "low",
            "source": "ml_only",
            "market_data": None,
            "adjustment_factor": 1.0
        }
    
    # Calculate adjustment factor
    market_median = market_data["median"]
    adjustment_factor = market_median / ml_price if ml_price > 0 else 1.0
    
    # Limit adjustment to reasonable range (0.5x to 2x)
    adjustment_factor = max(0.5, min(2.0, adjustment_factor))
    
    final_price = ml_price * adjustment_factor
    
    return {
        "final_price": final_price,
        "ml_price": ml_price,
        "market_median": market_median,
        "market_range": f"₹{market_data['min']:,.0f} - ₹{market_data['max']:,.0f}",
        "confidence": "high" if len(market_data["prices"]) >= 3 else "medium",
        "source": "hybrid",
        "market_data": market_data,
        "adjustment_factor": adjustment_factor,
        "sources_count": market_data["count"]
    }


# Example usage
if __name__ == "__main__":
    # Test with example
    result = get_market_prices_serpapi(
        brand="Maruti",
        model="Swift",
        year=2019,
        city="Mumbai",
        api_key="YOUR_API_KEY_HERE"  # Replace with actual key
    )
    
    print("Market Data:", result)
    
    if result["success"]:
        print(f"\nAverage Price: ₹{result['average']:,.0f}")
        print(f"Median Price: ₹{result['median']:,.0f}")
        print(f"Price Range: ₹{result['min']:,.0f} - ₹{result['max']:,.0f}")
        print(f"\nTop Sources:")
        for source in result["sources"]:
            print(f"  - {source['source']}: ₹{source['price']:,.0f}")
