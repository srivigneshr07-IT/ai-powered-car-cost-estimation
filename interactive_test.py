#!/usr/bin/env python3
"""
Interactive Testing Menu for AI-Powered Car Valuation System
"""

import sys
from database.connection import get_session
from database.models import MarketPrice, MarketStatistic
from market_intelligence import MarketIntelligence
from pricing import DynamicPricingEngine
from sqlalchemy import func
from datetime import datetime, timedelta

def print_header(title):
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)

def test_database():
    print_header("DATABASE STATUS")
    try:
        with get_session() as session:
            total = session.query(MarketPrice).count()
            stats = session.query(MarketStatistic).count()
            cities = session.query(func.count(func.distinct(MarketPrice.city))).scalar()
            brands = session.query(func.count(func.distinct(MarketPrice.brand))).scalar()
            
            thirty_days_ago = datetime.now() - timedelta(days=30)
            fresh = session.query(MarketPrice).filter(
                MarketPrice.last_seen_at >= thirty_days_ago
            ).count()
            
            print(f"\n✅ Total Listings: {total}")
            print(f"✅ Market Statistics: {stats}")
            print(f"✅ Fresh Data: {fresh} ({fresh/total*100:.1f}%)")
            print(f"✅ Cities: {cities} | Brands: {brands}")
            
            # Top 5 brands
            top_brands = session.query(
                MarketPrice.brand,
                func.count(MarketPrice.id).label('count')
            ).group_by(MarketPrice.brand).order_by(func.count(MarketPrice.id).desc()).limit(5).all()
            
            print(f"\n📊 Top 5 Brands:")
            for brand, count in top_brands:
                print(f"   {brand}: {count} listings")
                
    except Exception as e:
        print(f"❌ Error: {e}")

def test_market_intelligence():
    print_header("MARKET INTELLIGENCE TEST")
    
    print("\nEnter car details (or press Enter for default test):")
    brand = input("Brand [Maruti]: ").strip() or "Maruti"
    model = input("Model [Swift]: ").strip() or "Swift"
    year = input("Year [2018]: ").strip() or "2018"
    city = input("City [Chennai]: ").strip() or "Chennai"
    
    try:
        mi = MarketIntelligence()
        result = mi.get_market_insights(brand, model, int(year), city)
        
        print(f"\n📊 Market Insights for {brand} {model} {year} in {city}:")
        print(f"   Sample Size: {result['sample_size']} cars")
        print(f"   Confidence: {result['confidence'].upper()}")
        
        if result['sample_size'] > 0:
            stats = result['statistics']
            print(f"   Average Price: ₹{stats['average_price']:,.0f}")
            print(f"   Median Price: ₹{stats['median_price']:,.0f}")
            print(f"   Price Range: ₹{stats['min_price']:,.0f} - ₹{stats['max_price']:,.0f}")
        else:
            print("   No market data available")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def test_dynamic_pricing():
    print_header("DYNAMIC PRICING TEST")
    
    print("\nEnter details (or press Enter for default test):")
    ml_pred = input("ML Prediction [500000]: ").strip() or "500000"
    brand = input("Brand [Maruti]: ").strip() or "Maruti"
    model = input("Model [Swift]: ").strip() or "Swift"
    year = input("Year [2018]: ").strip() or "2018"
    city = input("City [Chennai]: ").strip() or "Chennai"
    
    try:
        engine = DynamicPricingEngine()
        result = engine.get_dynamic_price(int(ml_pred), brand, model, int(year), city)
        
        print(f"\n💰 Dynamic Pricing Result:")
        print(f"   ML Prediction: ₹{result['pricing_breakdown']['ml_prediction']:,.0f}")
        print(f"   Final Price: ₹{result['final_price']:,.0f}")
        print(f"   Market Confidence: {result['market_intelligence']['confidence'].upper()}")
        
        weights = result['pricing_breakdown']['weights']
        print(f"\n⚖️  Weights Applied:")
        print(f"   ML: {weights['ml_weight']*100:.0f}%")
        print(f"   Market Avg: {weights['market_avg_weight']*100:.0f}%")
        print(f"   Market Median: {weights['market_median_weight']*100:.0f}%")
        
        adj = result['adjustment']
        print(f"\n📈 Adjustment:")
        print(f"   Direction: {adj['direction']}")
        print(f"   Amount: ₹{abs(adj['amount']):,.0f}")
        print(f"   Percentage: {adj['percentage']:.2f}%")
        
        print(f"\n💡 Recommendation: {result['recommendation']}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

def view_sample_data():
    print_header("SAMPLE MARKET DATA")
    
    try:
        with get_session() as session:
            # Get 10 random listings
            listings = session.query(MarketPrice).limit(10).all()
            
            print(f"\n📋 Sample Listings (showing 10 of {session.query(MarketPrice).count()}):\n")
            print(f"{'Brand':<12} {'Model':<15} {'Year':<6} {'City':<12} {'Price':<12} {'Source':<10}")
            print("-" * 70)
            
            for listing in listings:
                print(f"{listing.brand:<12} {listing.model:<15} {listing.year:<6} "
                      f"{listing.city:<12} ₹{listing.price:<11,.0f} {listing.source:<10}")
                
    except Exception as e:
        print(f"❌ Error: {e}")

def view_documentation():
    print_header("DOCUMENTATION FILES")
    
    docs = {
        '1': ('API_DOCUMENTATION.md', 'Complete API reference with examples'),
        '2': ('USER_GUIDE.md', 'End-user guide with FAQs'),
        '3': ('TECHNICAL_DOCUMENTATION.md', 'Developer documentation'),
        '4': ('README_V2.md', 'Project overview'),
        '5': ('PHASE7.2_TEST_REPORT.md', 'Test results (17/17 passed)')
    }
    
    print("\nAvailable Documentation:\n")
    for key, (filename, desc) in docs.items():
        print(f"  {key}. {filename}")
        print(f"     {desc}\n")
    
    choice = input("Enter number to view (or Enter to skip): ").strip()
    
    if choice in docs:
        filename = docs[choice][0]
        try:
            with open(f"/home/sagemaker-user/ai-powered-car-final/{filename}", 'r') as f:
                content = f.read()
                print(f"\n{'=' * 70}")
                print(f"  {filename}")
                print(f"{'=' * 70}\n")
                print(content[:2000])  # Show first 2000 chars
                if len(content) > 2000:
                    print(f"\n... (showing first 2000 of {len(content)} characters)")
                    print(f"\nView full file: cat /home/sagemaker-user/ai-powered-car-final/{filename}")
        except Exception as e:
            print(f"❌ Error reading file: {e}")

def main_menu():
    while True:
        print_header("🚗 AI-POWERED CAR VALUATION - TESTING MENU")
        print("\n1. Database Status")
        print("2. Test Market Intelligence")
        print("3. Test Dynamic Pricing")
        print("4. View Sample Data")
        print("5. View Documentation")
        print("6. Run All Tests")
        print("0. Exit")
        
        choice = input("\nSelect option (0-6): ").strip()
        
        if choice == '1':
            test_database()
        elif choice == '2':
            test_market_intelligence()
        elif choice == '3':
            test_dynamic_pricing()
        elif choice == '4':
            view_sample_data()
        elif choice == '5':
            view_documentation()
        elif choice == '6':
            test_database()
            test_market_intelligence()
            test_dynamic_pricing()
        elif choice == '0':
            print("\n👋 Goodbye!")
            break
        else:
            print("\n❌ Invalid option. Please try again.")
        
        input("\nPress Enter to continue...")

if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
        sys.exit(0)
