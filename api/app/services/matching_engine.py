from sqlalchemy.orm import Session
from app.models.database import Order, OrderSide, OrderType, OrderStatus
from app.repositories.order_repo import OrderRepository
from app.repositories.trade_repo import TradeRepository
from app.repositories.country_repo import CountryRepository
from typing import List, Tuple
import uuid

class MatchingEngine:
    """
    Order matching engine - implements price-time priority
    Easily swappable for different matching algorithms
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.order_repo = OrderRepository(db)
        self.trade_repo = TradeRepository(db)
        self.country_repo = CountryRepository(db)
    
    def match_orders(self, resource_id: str) -> List[dict]:
        """
        Match pending orders for a resource
        Returns list of executed trades
        """
        orders = self.order_repo.get_pending_orders(resource_id)
        
        buy_orders = [o for o in orders if o.side == OrderSide.BUY]
        sell_orders = [o for o in orders if o.side == OrderSide.SELL]
        
        buy_orders.sort(key=lambda x: (-x.price if x.price else float('inf'), x.created_at))
        sell_orders.sort(key=lambda x: (x.price if x.price else 0, x.created_at))
        
        trades = []
        
        while buy_orders and sell_orders:
            buy_order = buy_orders[0]
            sell_order = sell_orders[0]
            
            if not self._can_match(buy_order, sell_order):
                break
            
            trade_quantity = min(
                buy_order.quantity - buy_order.filled_quantity,
                sell_order.quantity - sell_order.filled_quantity
            )
            
            trade_price = self._determine_trade_price(buy_order, sell_order)
            
            trade = self._execute_trade(
                buy_order,
                sell_order,
                trade_quantity,
                trade_price
            )
            
            trades.append(trade)
            
            if buy_order.filled_quantity >= buy_order.quantity:
                buy_orders.pop(0)
            if sell_order.filled_quantity >= sell_order.quantity:
                sell_orders.pop(0)
        
        return trades
    
    def _can_match(self, buy_order: Order, sell_order: Order) -> bool:
        """Check if buy and sell orders can be matched"""
        if buy_order.order_type == OrderType.MARKET or sell_order.order_type == OrderType.MARKET:
            return True
        
        return buy_order.price >= sell_order.price
    
    def _determine_trade_price(self, buy_order: Order, sell_order: Order) -> float:
        """Determine execution price - can be modified for different pricing rules"""
        if buy_order.order_type == OrderType.MARKET:
            return sell_order.price if sell_order.price else 0.0
        elif sell_order.order_type == OrderType.MARKET:
            return buy_order.price if buy_order.price else 0.0
        else:
            return (buy_order.price + sell_order.price) / 2.0
    
    def _execute_trade(
        self,
        buy_order: Order,
        sell_order: Order,
        quantity: float,
        price: float
    ) -> dict:
        """Execute a trade and update all relevant records"""
        trade_id = str(uuid.uuid4())
        
        trade_data = {
            "id": trade_id,
            "buyer_id": buy_order.country_id,
            "seller_id": sell_order.country_id,
            "resource_id": buy_order.resource_id,
            "quantity": quantity,
            "price": price,
            "carbon_impact": None
      }
        
        trade = self.trade_repo.create(trade_data)
        
        self.order_repo.update_order_fill(buy_order.id, quantity)
        self.order_repo.update_order_fill(sell_order.id, quantity)
        
        self.country_repo.update_holding(buy_order.country_id, buy_order.resource_id, quantity)
        self.country_repo.update_holding(sell_order.country_id, sell_order.resource_id, -quantity)
        
        self.trade_repo.record_market_price(buy_order.resource_id, price)
        
        return {
            "id": trade.id,
            "buyer_id": trade.buyer_id,
            "seller_id": trade.seller_id,
            "resource_id": trade.resource_id,
            "quantity": trade.quantity,
            "price": trade.price,
            "executed_at": trade.executed_at
        }