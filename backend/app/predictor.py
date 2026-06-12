"""
=========================================================

Project : AI Powered Vehicle Valuation System

Module  : Model Loader

=========================================================
"""

import joblib
from pathlib import Path

# Load model once when API starts

BASE_DIR = Path(__file__).resolve().parents[2]

MODEL_PATH = BASE_DIR / "models" / "vehicle_price_model_v1.pkl"

model = joblib.load(MODEL_PATH)


def predict_price(input_df):

    """
    Predict vehicle price.

    Parameters
    ----------
    input_df : pandas.DataFrame

    Returns
    -------
    float
    """

    prediction = model.predict(input_df)

    return float(prediction[0])


def estimate_damage_cost(description: str | None = None) -> float:
    if not description:
        return 0.0

    text = description.lower().strip()
    if not text:
        return 0.0

    major_keywords = [
        "major",
        "engine",
        "transmission",
        "frame",
        "accident",
        "flood",
        "airbag",
        "total",
        "fire",
        "rollover",
    ]
    medium_keywords = [
        "crack",
        "broken",
        "collision",
        "door",
        "window",
        "bumper",
        "fender",
        "headlight",
        "taillight",
        "windshield",
        "radiator",
    ]
    minor_keywords = [
        "scratch",
        "scuff",
        "dent",
        "dented",
        "chip",
        "chipped",
        "paint",
    ]

    if any(keyword in text for keyword in major_keywords):
        return 90000.0
    if any(keyword in text for keyword in medium_keywords):
        return 50000.0
    if any(keyword in text for keyword in minor_keywords):
        return 20000.0

    return min(15000.0 + len(text) * 18.0, 40000.0)


def calculate_confidence_score(payload: dict) -> int:
    score = 60
    weights = {
        "oem": 7,
        "model": 7,
        "variant": 6,
        "fuel": 5,
        "transmission": 5,
        "body": 5,
        "owner_type": 3,
        "City": 3,
        "state": 3,
        "km": 4,
        "car_age": 4,
    }
    for key, weight in weights.items():
        if payload.get(key) not in [None, "", 0]:
            score += weight

    if payload.get("damage_description"):
        score += 2

    return min(max(int(score), 45), 95)


def compute_suggested_price(predicted_price: float, damage_cost: float) -> float:
    floor_price = predicted_price * 0.72
    suggested = predicted_price - damage_cost
    return round(max(suggested, floor_price), 2)


def calculate_transaction_price(predicted_price: float, damage_cost: float, transaction_type: str) -> dict:
    """
    Calculate transaction-specific pricing based on transaction type.
    
    Parameters
    ----------
    predicted_price : float
        Base predicted market value
    damage_cost : float
        Estimated damage repair cost
    transaction_type : str
        One of: "selling", "buying_resale", "buying_personal"
    
    Returns
    -------
    dict with transaction_price, profit_margin, price_range_min, price_range_max
    """
    market_value = predicted_price - damage_cost
    floor_price = predicted_price * 0.72
    market_value = max(market_value, floor_price)
    
    if transaction_type == "selling":
        # Selling mode: show suggested selling price
        return {
            "transaction_price": round(market_value, 2),
            "profit_margin": None,
            "price_range_min": None,
            "price_range_max": None
        }
    
    elif transaction_type == "buying_resale":
        # Buying for resale: calculate max buy price for 10% profit margin
        max_buy_price = market_value / 1.10
        profit_amount = market_value - max_buy_price
        return {
            "transaction_price": round(max_buy_price, 2),
            "profit_margin": round(profit_amount, 2),
            "price_range_min": round(max_buy_price * 0.95, 2),  # 5% negotiation room
            "price_range_max": round(max_buy_price, 2)
        }
    
    elif transaction_type == "buying_personal":
        # Buying for personal use: show fair buy price (lower than market)
        fair_buy_price = market_value * 0.95  # 5% below market value
        fair_min = market_value * 0.90  # 10% below market
        fair_max = market_value * 0.98  # 2% below market
        return {
            "transaction_price": round(fair_buy_price, 2),
            "profit_margin": None,
            "price_range_min": round(fair_min, 2),
            "price_range_max": round(fair_max, 2)
        }
    
    else:
        # Default to selling
        return {
            "transaction_price": round(market_value, 2),
            "profit_margin": None,
            "price_range_min": None,
            "price_range_max": None
        }
