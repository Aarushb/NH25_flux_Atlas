from sqlalchemy.orm import Session
from app.models.database import Trade, MarketPrice
from typing import List, Optional

class TradeRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, trade_data: dict) -> Trade:
        trade = Trade(**trade_data)
        self.db.add(trade)
        self.db.commit()
        self.db.refresh(trade)
        return trade
    
    def get_all(self) -> List[Trade]:
        return self.db.query(Trade).all()
    
    def get_by_resource(self, resource_id: str) -> List[Trade]:
        return self.db.query(Trade).filter(Trade.resource_id == resource_id).all()
    
    def record_market_price(self, resource_id: str, price: float):
        market_price = MarketPrice(resource_id=resource_id, price=price)
        self.db.add(market_price)
        self.db.commit()
    
    def get_latest_market_price(self, resource_id: str) -> Optional[MarketPrice]:
        return self.db.query(MarketPrice).filter(
            MarketPrice.resource_id == resource_id
        ).order_by(MarketPrice.timestamp.desc()).first()