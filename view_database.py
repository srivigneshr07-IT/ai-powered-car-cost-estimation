"""
Simple Database Viewer - View RDS tables in terminal
"""

from database.connection import get_session
from database.models import MarketPrice, MarketStatistic, PipelineLog
from sqlalchemy import func, desc
from datetime import datetime, timedelta
import sys


def view_tables():
    """Show all tables and row counts"""
    print("\n" + "="*80)
    print("📊 DATABASE TABLES")
    print("="*80)
    
    with get_session() as session:
        tables = [
            ("market_prices", MarketPrice),
            ("market_statistics", MarketStatistic),
            ("pipeline_logs", PipelineLog)
        ]
        
        for table_name, model in tables:
            count = session.query(model).count()
            print(f"   {table_name}: {count} rows")
    print()


def view_market_prices(limit=20):
    """View market_prices table"""
    print("\n" + "="*80)
    print(f"📋 MARKET_PRICES TABLE (Latest {limit} rows)")
    print("="*80)
    
    with get_session() as session:
        listings = session.query(MarketPrice).order_by(desc(MarketPrice.last_seen_at)).limit(limit).all()
        
        print(f"\n{'ID':<5} {'Brand':<12} {'Model':<15} {'Year':<6} {'Price':<12} {'KM':<10} {'City':<12} {'Last Seen':<20}")
        print("-"*110)
        
        for listing in listings:
            print(f"{listing.id:<5} {listing.brand:<12} {listing.model[:14]:<15} {listing.year:<6} "
                  f"₹{listing.price:>10,} {listing.kilometers:>9,} {listing.city:<12} "
                  f"{str(listing.last_seen_at)[:19]:<20}")
    print()


def view_by_city():
    """View listings grouped by city"""
    print("\n" + "="*80)
    print("📍 LISTINGS BY CITY")
    print("="*80)
    
    with get_session() as session:
        cities = session.query(
            MarketPrice.city,
            func.count(MarketPrice.id).label('count'),
            func.avg(MarketPrice.price).label('avg_price'),
            func.min(MarketPrice.price).label('min_price'),
            func.max(MarketPrice.price).label('max_price')
        ).group_by(MarketPrice.city).order_by(desc('count')).all()
        
        print(f"\n{'City':<15} {'Count':<8} {'Avg Price':<15} {'Min Price':<15} {'Max Price':<15}")
        print("-"*70)
        
        for city, count, avg_price, min_price, max_price in cities:
            print(f"{city:<15} {count:<8} ₹{int(avg_price):>12,}  ₹{int(min_price):>12,}  ₹{int(max_price):>12,}")
    print()


def view_by_brand():
    """View listings grouped by brand"""
    print("\n" + "="*80)
    print("🚗 LISTINGS BY BRAND (Top 15)")
    print("="*80)
    
    with get_session() as session:
        brands = session.query(
            MarketPrice.brand,
            func.count(MarketPrice.id).label('count'),
            func.avg(MarketPrice.price).label('avg_price')
        ).group_by(MarketPrice.brand).order_by(desc('count')).limit(15).all()
        
        print(f"\n{'Brand':<15} {'Count':<8} {'Avg Price':<15}")
        print("-"*40)
        
        for brand, count, avg_price in brands:
            print(f"{brand:<15} {count:<8} ₹{int(avg_price):>12,}")
    print()


def view_fresh_vs_stale():
    """View fresh vs stale listings"""
    print("\n" + "="*80)
    print("🕐 FRESHNESS ANALYSIS")
    print("="*80)
    
    with get_session() as session:
        now = datetime.utcnow()
        
        # Last 24 hours
        day_ago = now - timedelta(days=1)
        fresh_24h = session.query(MarketPrice).filter(MarketPrice.last_seen_at >= day_ago).count()
        
        # Last 7 days
        week_ago = now - timedelta(days=7)
        fresh_7d = session.query(MarketPrice).filter(MarketPrice.last_seen_at >= week_ago).count()
        
        # Last 30 days
        month_ago = now - timedelta(days=30)
        fresh_30d = session.query(MarketPrice).filter(MarketPrice.last_seen_at >= month_ago).count()
        
        # Total
        total = session.query(MarketPrice).count()
        
        print(f"\n   🟢 Last 24 hours: {fresh_24h} listings")
        print(f"   🟡 Last 7 days: {fresh_7d} listings")
        print(f"   🟠 Last 30 days: {fresh_30d} listings")
        print(f"   🔴 Older than 30 days: {total - fresh_30d} listings")
        print(f"   📊 Total: {total} listings")
    print()


def search_listings(brand=None, city=None, min_price=None, max_price=None):
    """Search listings with filters"""
    print("\n" + "="*80)
    print("🔍 SEARCH RESULTS")
    print("="*80)
    
    with get_session() as session:
        query = session.query(MarketPrice)
        
        if brand:
            query = query.filter(MarketPrice.brand.ilike(f"%{brand}%"))
        if city:
            query = query.filter(MarketPrice.city.ilike(f"%{city}%"))
        if min_price:
            query = query.filter(MarketPrice.price >= min_price)
        if max_price:
            query = query.filter(MarketPrice.price <= max_price)
        
        listings = query.order_by(desc(MarketPrice.last_seen_at)).limit(20).all()
        
        print(f"\nFound {len(listings)} listings")
        print(f"\n{'Brand':<12} {'Model':<15} {'Year':<6} {'Price':<12} {'KM':<10} {'City':<12}")
        print("-"*80)
        
        for listing in listings:
            print(f"{listing.brand:<12} {listing.model[:14]:<15} {listing.year:<6} "
                  f"₹{listing.price:>10,} {listing.kilometers:>9,} {listing.city:<12}")
    print()


def main():
    """Main menu"""
    while True:
        print("\n" + "="*80)
        print("🗄️  RDS DATABASE VIEWER")
        print("="*80)
        print("\n1. View all tables")
        print("2. View market_prices (latest 20)")
        print("3. View market_prices (latest 50)")
        print("4. View by city")
        print("5. View by brand")
        print("6. View freshness analysis")
        print("7. Search listings (custom)")
        print("8. Exit")
        
        choice = input("\nEnter choice (1-8): ").strip()
        
        if choice == "1":
            view_tables()
        elif choice == "2":
            view_market_prices(20)
        elif choice == "3":
            view_market_prices(50)
        elif choice == "4":
            view_by_city()
        elif choice == "5":
            view_by_brand()
        elif choice == "6":
            view_fresh_vs_stale()
        elif choice == "7":
            brand = input("Brand (or press Enter to skip): ").strip() or None
            city = input("City (or press Enter to skip): ").strip() or None
            min_price = input("Min price (or press Enter to skip): ").strip()
            max_price = input("Max price (or press Enter to skip): ").strip()
            min_price = int(min_price) if min_price else None
            max_price = int(max_price) if max_price else None
            search_listings(brand, city, min_price, max_price)
        elif choice == "8":
            print("\nGoodbye! 👋")
            break
        else:
            print("\n❌ Invalid choice. Try again.")


if __name__ == "__main__":
    main()
