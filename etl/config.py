"""
ETL Pipeline Configuration
Defines supported brands, cities, sources, and scraping parameters
"""

# Supported Brands (ALL brands from existing XGBoost model)
SUPPORTED_BRANDS = [
    "Maruti", "Hyundai", "Honda", "Toyota", "Mahindra", "Tata", "Kia",
    "MG", "Volkswagen", "Skoda", "Renault", "Nissan", "Ford", "Jeep",
    "BMW", "Mercedes", "Audi", "Volvo", "Jaguar", "Land Rover",
    "Mini", "Porsche", "Lexus", "Isuzu", "Citroen", "BYD", "Force"
]

# Supported Cities (configurable)
SUPPORTED_CITIES = [
    "Chennai", "Bangalore", "Hyderabad", "Mumbai", "Delhi",
    "Pune", "Kolkata", "Ahmedabad", "Jaipur", "Lucknow",
    "Surat", "Indore", "Chandigarh", "Coimbatore", "Kochi"
]

# Source Adapters Configuration (4 sources)
SOURCES = {
    "cars24": {
        "enabled": True,
        "base_url": "https://www.cars24.com",
        "timeout": 10,
        "max_retries": 3
    },
    "cardekho": {
        "enabled": True,
        "base_url": "https://www.cardekho.com",
        "timeout": 10,
        "max_retries": 3
    },
    "spinny": {
        "enabled": False,  # Disabled - requires Selenium
        "base_url": "https://www.spinny.com",
        "timeout": 10,
        "max_retries": 3
    },
    "olx": {
        "enabled": False,  # Disabled - requires Selenium
        "base_url": "https://www.olx.in",
        "timeout": 10,
        "max_retries": 3
    }
}

# Scraping Parameters
SCRAPING_CONFIG = {
    "max_pages_per_city": 220,  # Increased to get 500+ unique listingsto get 500+ unique listings
    "delay_between_requests": 2,  # seconds
    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# Validation Rules
VALIDATION_RULES = {
    "price": {"min": 50000, "max": 50000000},
    "kilometers": {"min": 0, "max": 500000},
    "year": {"min": 1990, "max": 2026}
}

# Normalization Mappings
BRAND_MAPPING = {
    "maruti suzuki": "Maruti", "maruti": "Maruti",
    "hyundai": "Hyundai",
    "honda": "Honda",
    "toyota": "Toyota",
    "mahindra": "Mahindra",
    "tata": "Tata", "tata motors": "Tata",
    "kia": "Kia",
    "mg": "MG", "mg motor": "MG",
    "volkswagen": "Volkswagen", "vw": "Volkswagen",
    "skoda": "Skoda",
    "renault": "Renault",
    "nissan": "Nissan",
    "ford": "Ford",
    "jeep": "Jeep",
    "bmw": "BMW",
    "mercedes benz": "Mercedes", "mercedes-benz": "Mercedes", "mercedes": "Mercedes",
    "audi": "Audi",
    "volvo": "Volvo",
    "jaguar": "Jaguar",
    "land rover": "Land Rover", "landrover": "Land Rover",
    "mini": "Mini",
    "porsche": "Porsche",
    "lexus": "Lexus",
    "isuzu": "Isuzu",
    "citroen": "Citroen",
    "byd": "BYD",
    "force": "Force"
}

FUEL_MAPPING = {
    "petrol": "Petrol",
    "diesel": "Diesel",
    "cng": "CNG",
    "lpg": "LPG",
    "electric": "Electric",
    "hybrid": "Hybrid"
}

TRANSMISSION_MAPPING = {
    "manual": "Manual",
    "automatic": "Automatic",
    "amt": "AMT",
    "cvt": "CVT",
    "dct": "DCT"
}

OWNER_MAPPING = {
    "1st": "First", "first": "First",
    "2nd": "Second", "second": "Second",
    "3rd": "Third", "third": "Third",
    "4th": "Fourth", "fourth": "Fourth"
}
