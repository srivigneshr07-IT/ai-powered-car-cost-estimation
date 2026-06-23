"""
Dynamic Pricing Engine
Combines ML predictions with real-time market intelligence
"""

from typing import Dict, Optional
from market_intelligence import MarketIntelligence


class DynamicPricingEngine:
    """
    Combines ML model predictions with market intelligence
    to provide accurate, market-aware pricing
    """
    
    def __init__(self, freshness_days: int = 30):
        """
        Initialize Dynamic Pricing Engine
        
        Args:
            freshness_days: Only use market data from last N days
        """
        self.market_intelligence = MarketIntelligence(freshness_days)
        
        # Weights based on confidence level
        self.weight_config = {
            "high": {
                "ml_weight": 0.60,
                "market_avg_weight": 0.25,
                "market_median_weight": 0.15
            },
            "medium": {
                "ml_weight": 0.70,
                "market_avg_weight": 0.20,
                "market_median_weight": 0.10
            },
            "low": {
                "ml_weight": 0.85,
                "market_avg_weight": 0.10,
                "market_median_weight": 0.05
            },
            "very_low": {
                "ml_weight": 0.95,
                "market_avg_weight": 0.03,
                "market_median_weight": 0.02
            },
            "none": {
                "ml_weight": 1.0,
                "market_avg_weight": 0.0,
                "market_median_weight": 0.0
            }
        }
    
    def get_dynamic_price(
        self,
        ml_prediction: float,
        brand: str,
        model: str,
        year: int,
        city: str,
        fuel: Optional[str] = None,
        transmission: Optional[str] = None
    ) -> Dict:
        """
        Calculate dynamic price combining ML and market intelligence
        
        Args:
            ml_prediction: Price predicted by ML model
            brand: Car brand
            model: Car model
            year: Manufacturing year
            city: City name
            fuel: Fuel type (optional)
            transmission: Transmission type (optional)
        
        Returns:
            Dictionary with final price and breakdown
        """
        # Get market insights
        market_insights = self.market_intelligence.get_market_insights(
            brand=brand,
            model=model,
            year=year,
            city=city,
            fuel=fuel,
            transmission=transmission
        )
        
        # Check if market data is available
        if not market_insights.get("market_data_available", False):
            return self._ml_only_response(ml_prediction, market_insights)
        
        # Get confidence and weights
        confidence = market_insights["confidence"]
        weights = self.weight_config[confidence]
        
        # Get market prices
        market_avg = market_insights["statistics"]["average_price"]
        market_median = market_insights["statistics"]["median_price"]
        
        # Calculate weighted final price
        final_price = (
            weights["ml_weight"] * ml_prediction +
            weights["market_avg_weight"] * market_avg +
            weights["market_median_weight"] * market_median
        )
        
        # Calculate price adjustment
        adjustment = final_price - ml_prediction
        adjustment_percent = (adjustment / ml_prediction) * 100
        
        return {
            "status": "success",
            "final_price": round(final_price),
            "pricing_breakdown": {
                "ml_prediction": round(ml_prediction),
                "market_average": market_avg,
                "market_median": market_median,
                "weights_applied": weights,
                "confidence": confidence
            },
            "adjustment": {
                "amount": round(adjustment),
                "percentage": round(adjustment_percent, 2),
                "direction": "increased" if adjustment > 0 else "decreased"
            },
            "market_context": {
                "sample_size": market_insights["sample_size"],
                "price_range": market_insights["statistics"]["price_range"],
                "min_price": market_insights["statistics"]["min_price"],
                "max_price": market_insights["statistics"]["max_price"]
            },
            "recommendation": self._generate_recommendation(
                final_price, 
                market_insights["statistics"]["min_price"],
                market_insights["statistics"]["max_price"],
                confidence
            )
        }
    
    def _ml_only_response(self, ml_prediction: float, market_insights: Dict) -> Dict:
        """Return response when no market data is available"""
        return {
            "status": "ml_only",
            "final_price": round(ml_prediction),
            "pricing_breakdown": {
                "ml_prediction": round(ml_prediction),
                "market_average": None,
                "market_median": None,
                "weights_applied": self.weight_config["none"],
                "confidence": "none"
            },
            "adjustment": {
                "amount": 0,
                "percentage": 0.0,
                "direction": "none"
            },
            "market_context": {
                "sample_size": 0,
                "message": "No market data available. Price based on ML model only."
            },
            "recommendation": "Limited market data. Consider checking multiple sources for price validation."
        }
    
    def _generate_recommendation(
        self, 
        final_price: float, 
        min_price: float, 
        max_price: float,
        confidence: str
    ) -> str:
        """Generate pricing recommendation based on market position"""
        
        # Calculate position in price range
        price_range = max_price - min_price
        position = (final_price - min_price) / price_range if price_range > 0 else 0.5
        
        if confidence == "high":
            if position < 0.3:
                return "Great deal! Price is below market average. Consider buying soon."
            elif position < 0.7:
                return "Fair price. Aligns well with current market conditions."
            else:
                return "Price is above market average. Consider negotiating."
        
        elif confidence == "medium":
            if position < 0.3:
                return "Good price based on available market data. Verify condition carefully."
            elif position < 0.7:
                return "Reasonable price. Limited market data - compare with other sources."
            else:
                return "Higher than typical market price. Negotiate or seek more options."
        
        else:  # low or very_low
            return "Limited market data available. Verify price with multiple sources before deciding."
    
    def get_price_comparison(
        self,
        ml_prediction: float,
        brand: str,
        model: str,
        year: int,
        cities: list
    ) -> Dict:
        """
        Compare prices across multiple cities
        
        Args:
            ml_prediction: ML model prediction
            brand: Car brand
            model: Car model
            year: Manufacturing year
            cities: List of cities to compare
        
        Returns:
            Dictionary with city-wise price comparison
        """
        comparisons = {}
        
        for city in cities:
            result = self.get_dynamic_price(
                ml_prediction=ml_prediction,
                brand=brand,
                model=model,
                year=year,
                city=city
            )
            
            comparisons[city] = {
                "final_price": result["final_price"],
                "confidence": result["pricing_breakdown"]["confidence"],
                "sample_size": result["market_context"]["sample_size"]
            }
        
        # Find best deal
        valid_cities = {k: v for k, v in comparisons.items() if v["sample_size"] > 0}
        
        if valid_cities:
            best_city = min(valid_cities.items(), key=lambda x: x[1]["final_price"])
            worst_city = max(valid_cities.items(), key=lambda x: x[1]["final_price"])
            
            return {
                "status": "success",
                "comparisons": comparisons,
                "insights": {
                    "best_deal": {
                        "city": best_city[0],
                        "price": best_city[1]["final_price"]
                    },
                    "highest_price": {
                        "city": worst_city[0],
                        "price": worst_city[1]["final_price"]
                    },
                    "price_difference": worst_city[1]["final_price"] - best_city[1]["final_price"]
                }
            }
        else:
            return {
                "status": "insufficient_data",
                "comparisons": comparisons,
                "message": "Not enough market data for meaningful comparison"
            }
