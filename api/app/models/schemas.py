from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

class OrderTypeSchema(str, Enum):
    LIMIT = "LIMIT"
    MARKET = "MARKET"

class OrderSideSchema(str, Enum):
    BUY = "BUY"
    SELL = "SELL"

class OrderStatusSchema(str, Enum):
    PENDING = "PENDING"
    PARTIAL = "PARTIAL"
    FILLED = "FILLED"
    CANCELLED = "CANCELLED"

class CountryCreate(BaseModel):
    id: str
    name: str
    gdp_ppp: float
    carbon_budget: Optional[float] = None

class CountryResponse(BaseModel):
    id: str
    name: str
    gdp_ppp: float
    carbon_budget: Optional[float]
    created_at: datetime
    
    class Config:
        from_attributes = True

class ResourceCreate(BaseModel):
    id: str
    name: str
    base_price: float
    essentiality_factor: float = Field(ge=1.0, le=3.0)
    global_supply: float

class ResourceResponse(BaseModel):
    id: str
    name: str
    base_price: float
    essentiality_factor: float
    global_supply: float
    
    class Config:
        from_attributes = True

class OrderCreate(BaseModel):
    country_id: str
    resource_id: str
    order_type: OrderTypeSchema
    side: OrderSideSchema
    price: Optional[float] = None
    quantity: float

class OrderResponse(BaseModel):
    id: str
    country_id: str
    resource_id: str
    order_type: OrderTypeSchema
    side: OrderSideSchema
    price: Optional[float]
    quantity: float
    filled_quantity: float
    status: OrderStatusSchema
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class TradeResponse(BaseModel):
    id: str
    buyer_id: str
    seller_id: str
    resource_id: str
    quantity: float
    price: float
    carbon_impact: Optional[float]
    executed_at: datetime
    
    class Config:
        from_attributes = True

class MarketPriceResponse(BaseModel):
    resource_id: str
    price: float
    timestamp: datetime
    
    class Config:
        from_attributes = True

class HoldingResponse(BaseModel):
    country_id: str
    resource_id: str
    quantity: float
    
    class Config:
        from_attributes = True