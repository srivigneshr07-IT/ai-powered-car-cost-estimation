"""
Multi-API Market Price Fetcher with Smart Caching
Rotates between multiple free APIs for higher limits
"""

import os
import json
import time
from datetime import datetime, timedelta
from pathlib import Path
import hashlib

# Cache directory
CACHE_DIR = Path(__file__).parent / "cache"
CACHE_DIR.mkdir(exist_ok=True)
CACHE_DURATION_HOURS = 24

def get_cache_key(brand, model, year, city):
    """Generate cache key"""
    key = f"{brand}_{model}_{year}_{city}".lower()
    return hashlib.md5(key.encode()).hexdigest()

def get_cached_price(brand, model, year, city):
    """Get cached price if available and fresh"""
    cache_key = get_cache_key(brand, model, year, city)
    cache_file = CACHE_DIR / f"{cache_key}.json"
    
    if cache_file.exists():
        with open(cache_file, 'r') as f:
            data = json.load(f)
        
        cached_time = datetime.fromisoformat(data['timestamp'])
        if datetime.now() - cached_time < timedelta(hours=CACHE_DURATION_HOURS):
            data['from_cache'] = True
            return data
    
    return None

def save_to_cache(brand, model, year, city, price_data):
    """Save price data to cache"""
    cache_key = get_cache_key(brand, model, year, city)
    cache_file = CACHE_DIR / f"{cache_key}.json"
    
    price_data['timestamp'] = datetime.now().isoformat()
    price_data['from_cache'] = False
    
    with open(cache_file, 'w') as f:
        json.dump(price_data, f)

def scrape_with_scraperapi(brand, model, year, city, api_key):
    """Use ScraperAPI (1000 free/month)"""
    try:
        import requests
        from bs4 import BeautifulSoup
        
        # Search on CarDekho via ScraperAPI
        search_url = f"https://www.cardekho.com/used-{brand.lower()}-{model.lower()}-cars-in-{city.lower()}"
        
        params = {
            'api_key': api_key,
            'url': search_url
        }
        
        response = requests.get('http://api.scraperapi.com/', params=params, timeout=60)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            prices = []
            
            # Extract prices (adjust selectors based on actual site)
            price_elements = soup.find_all(class_=['price', 'priceTag'])
            for elem in price_elements[:10]:
                text = elem.get_text()
                # Extract numeric price
                import re
                match = re.search(r'(\d+\.?\d*)\s*[Ll]akh', text)
                if match:
                    prices.append(float(match.group(1)) * 100000)
            
            if prices:
                return {
                    'success': True,
                    'prices': prices,
                    'median': sorted(prices)[len(prices)//2],
                    'source': 'scraperapi'
                }
        
        return {'success': False, 'error': 'No data found'}
        
    except Exception as e:
        return {'success': False, 'error': str(e)}

def scrape_with_requests(brand, model, year, city):
    """Direct scraping with requests (unlimited but may get blocked)"""
    try:
        import requests
        from bs4 import BeautifulSoup
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        # Try Cars24 (simpler structure)
        url = f"https://www.cars24.com/buy-used-{brand.lower()}-{model.lower()}-cars-{city.lower()}/"
        
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            prices = []
            
            # Extract prices
            import re
            price_pattern = r'₹\s*(\d+\.?\d*)\s*[Ll]akh'
            matches = re.findall(price_pattern, response.text)
            
            for match in matches[:10]:
                prices.append(float(match) * 100000)
            
            if prices:
                return {
                    'success': True,
                    'prices': prices,
                    'median': sorted(prices)[len(prices)//2],
                    'source': 'direct_scraping'
                }
        
        return {'success': False, 'error': 'No data found'}
        
    except Exception as e:
        return {'success': False, 'error': str(e)}

def get_market_price_multi_source(brand, model, year, city):
    """
    Try multiple sources with caching
    Priority: Cache → ScraperAPI → Direct Scraping → ML Only
    """
    
    # 1. Check cache first
    cached = get_cached_price(brand, model, year, city)
    if cached:
        return cached
    
    # 2. Try ScraperAPI (if key available)
    scraperapi_key = os.getenv('SCRAPERAPI_KEY')
    if scraperapi_key:
        result = scrape_with_scraperapi(brand, model, year, city, scraperapi_key)
        if result['success']:
            save_to_cache(brand, model, year, city, result)
            return result
    
    # 3. Try direct scraping
    result = scrape_with_requests(brand, model, year, city)
    if result['success']:
        save_to_cache(brand, model, year, city, result)
        return result
    
    # 4. No market data available
    return {
        'success': False,
        'error': 'No market data available',
        'use_ml_only': True
    }

def get_final_price(ml_price, brand, model, year, city):
    """Get final price with market adjustment"""
    
    market_data = get_market_price_multi_source(brand, model, year, city)
    
    if not market_data['success']:
        return {
            'final_price': ml_price,
            'source': 'ml_only',
            'confidence': 'medium'
        }
    
    # Adjust ML price with market data
    market_median = market_data['median']
    adjustment = market_median / ml_price if ml_price > 0 else 1.0
    adjustment = max(0.5, min(2.0, adjustment))  # Limit to 0.5x-2x
    
    final_price = ml_price * adjustment
    
    return {
        'final_price': final_price,
        'ml_price': ml_price,
        'market_median': market_median,
        'adjustment_factor': adjustment,
        'source': market_data['source'],
        'from_cache': market_data.get('from_cache', False),
        'confidence': 'high'
    }


# Example usage
if __name__ == "__main__":
    result = get_final_price(
        ml_price=500000,
        brand="Maruti",
        model="Swift",
        year=2019,
        city="Mumbai"
    )
    print(result)
