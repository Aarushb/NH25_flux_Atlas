import math
from typing import Dict

class PricingService:
    """
    Modular pricing service - swap out formula as needed
    Current implementation based on: v = (base_price) * y * (e^{-(current - target)/supply} - 1/(1+k))
    """
    
    @staticmethod
    def calculate_dynamic_price(
        base_price: float,
        essentiality_factor: float,
        current_supply: float,
        target_supply: float,
        global_supply: float
    ) -> float:
        """
        Calculate dynamic price based on supply/demand pressure
        
        Args:
            base_price: Resource base price
            essentiality_factor: k value (1-3, higher = more essential)
            current_supply: Current market supply level
            target_supply: Target supply level
            global_supply: Total global supply
        """
        y = base_price * essentiality_factor
        
        supply_pressure = (current_supply - target_supply) / global_supply if global_supply > 0 else 0
        
        exponential_term = math.exp(-supply_pressure)
        dampening_term = 1.0 / (1.0 + essentiality_factor)
        
      _price_multiplier = exponential_term - dampening_term
        
        dynamic_price = base_price * y * price_multiplier
        
        return max(dynamic_price, base_price * 0.1)
    
    @staticmethod
    def calculate_clearing_price(buy_orders: list, sell_orders: list) -> float:
        """
        Simple clearing price: midpoint of best bid and ask
        Can be replaced with more sophisticated auction mechanisms
        """
        if not buy_orders or not sell_orders:
            return 0.0
        
        best_bid = max([o.price for o in buy_orders if o.price])
        best_ask = min([o.price for o in sell_orders if o.price])
        
        return (best_bid + best_ask) / 2.0