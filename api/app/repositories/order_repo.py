from sqlalchemy.orm import Session
from app.models.database import Order, OrderStatus, OrderSide, OrderType
from typing import List, Optional

class OrderRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, order_data: dict) -> Order:
        order = Order(**order_data)
        self.db.add(order)
        self.db.commit()
        self.db.refresh(order)
        return order
    
    def get(self, order_id: str) -> Optional[Order]:
        return self.db.query(Order).filter(Order.id == order_id).first()
    
    def get_pending_orders(self, resource_id: str) -> List[Order]:
        return self.db.query(Order).filter(
            Order.resource_id == resource_id,
            Order.status.in_([OrderStatus.PENDING, OrderStatus.PARTIAL])
        ).order_by(Order.created_at).all()
    
    def get_country_orders(self, country_id: str) -> List[Order]:
        return self.db.query(Order).filter(Order.country_id == country_id).all()
    
    def update_order_fill(self, order_id: str, filled_quantity: float):
        order = self.get(order_id)
        if order:
            order.filled_quantity += filled_quantity
            if order.filled_quantity >= order.quantity:
                order.status = OrderStatus.FILLED
            else:
                order.status = OrderStatus.PARTIAL
            self.db.commit()
    
    def cancel_order(self, order_id: str):
        order = self.get(order_id)
        if order:
            order.status = OrderStatus.CANCELLED
            self.db.commit()