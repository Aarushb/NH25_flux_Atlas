from sqlalchemy import create_engine, Column, String, Float, Integer, DateTime, Boolean, ForeignKey, Enum as SQLEnum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import enum

Base = declarative_base()

class OrderType(enum.Enum):
    LIMIT = "LIMIT"
    MARKET = "MARKET"

class OrderSide(enum.Enum):
    BUY = "BUY"
    SELL = "SELL"

class OrderStatus(enum.Enum):
    PENDING = "PENDING"
    PARTIAL = "PARTIAL"
    FILLED = "FILLED"
    CANCELLED = "CANCELLED"

class Country(Base):
    __tablename__ = "countries"
    
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    gdp_ppp = Column(Float, nullable=False)
    carbon_budget = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    orders = relationship("Order", back_populates="country")
    trades_as_buyer = relationship("Trade", foreign_keys="Trade.buyer_id", back_populates="buyer")
    trades_as_seller = relationship("Trade", foreign_keys="Trade.seller_id", back_populates="seller")
    holdings = relationship("CountryHolding", back_populates="country")

class Resource(Base):
    __tablename__ = "resources"
    
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    base_price = Column(Float, nullable=False)
    essentiality_factor = Column(Float, nullable=False, default=1.5)
    global_supply = Column(Float, nullable=False)
    
    orders = relationship("Order", back_populates="resource")
    trades = relationship("Trade", back_populates="resource")

class CountryHolding(Base):
    __tablename__ = "country_holdings"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    country_id = Column(String, ForeignKey("countries.id"), nullable=False)
    resource_id = Column(String, ForeignKey("resources.id"), nullable=False)
    quantity = Column(Float, nullable=False, default=0.0)
    
    country = relationship("Country", back_populates="holdings")
    resource = relationship("Resource")

class Order(Base):
    __tablename__ = "orders"
    
    id = Column(String, primary_key=True)
    country_id = Column(String, ForeignKey("countries.id"), nullable=False)
    resource_id = Column(String, ForeignKey("resources.id"), nullable=False)
    order_type = Column(SQLEnum(OrderType), nullable=False)
    side = Column(SQLEnum(OrderSide), nullable=False)
    price = Column(Float)
    quantity = Column(Float, nullable=False)
    filled_quantity = Column(Float, default=0.0)
    status = Column(SQLEnum(OrderStatus), default=OrderStatus.PENDING)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    country = relationship("Country", back_populates="orders")
    resource = relationship("Resource", back_populates="orders")

class Trade(Base):
    __tablename__ = "trades"
    
    id = Column(String, primary_key=True)
    buyer_id = Column(String, ForeignKey("countries.id"), nullable=False)
    seller_id = Column(String, ForeignKey("countries.id"), nullable=False)
    resource_id = Column(String, ForeignKey("resources.id"), nullable=False)
    quantity = Column(Float, nullable=False)
    price = Column(Float, nullable=False)
    carbon_impact = Column(Float)
    executed_at = Column(DateTime, default=datetime.utcnow)
    
    buyer = relationship("Country", foreign_keys=[buyer_id], back_populates="trades_as_buyer")
    seller = relationship("Country", foreign_keys=[seller_id], back_populates="trades_as_seller")
    resource = relationship("Resource", back_populates="trades")

class MarketPrice(Base):
    __tablename__ = "market_prices"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    resource_id = Column(String, ForeignKey("resources.id"), nullable=False)
    price = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)