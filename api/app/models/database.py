from sqlalchemy import create_engine, Column, String, Float, Integer, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import uuid

Base = declarative_base()

class Group(Base):
    __tablename__ = "groups"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(20), unique=True, nullable=False)
    low_ppp = Column(Integer)
    high_ppp = Column(Integer)
    description = Column(String(50))
    
    countries = relationship("Country", back_populates="group")
    auction_groups = relationship("AuctionGroup", back_populates="group")

class Country(Base):
    __tablename__ = "countries"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cname = Column(String(50), unique=True, nullable=False)
    group_id = Column(UUID(as_uuid=True), ForeignKey("groups.id"))
    carbon_budget = Column(Float)
    ppp = Column(Integer)
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(String(20))
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    updated_by = Column(String(20))
    
    group = relationship("Group", back_populates="countries")
    country_resources = relationship("CountryResource", back_populates="country")
    initiated_auctions = relationship("AuctionInfo", back_populates="initiator")
    auction_rounds_won = relationship("AuctionRound", back_populates="winner")
    bids = relationship("AuctionBid", back_populates="country")

class Resource(Base):
    __tablename__ = "resources"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    rname = Column(String(20), unique=True, nullable=False)
    price = Column(Float)
    description = Column(String(50))
    
    country_resources = relationship("CountryResource", back_populates="resource")
    auctions = relationship("AuctionInfo", back_populates="resource")

class CountryResource(Base):
    __tablename__ = "country_resources"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    country_id = Column(UUID(as_uuid=True), ForeignKey("countries.id"), nullable=False)
    resource_id = Column(UUID(as_uuid=True), ForeignKey("resources.id"), nullable=False)
    supply = Column(Integer)
    demand = Column(Integer)
    quantity = Column(Float)
    unit = Column(String(50))
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(String(50))
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    updated_by = Column(String(50))
    
    country = relationship("Country", back_populates="country_resources")
    resource = relationship("Resource", back_populates="country_resources")

class AuctionInfo(Base):
    __tablename__ = "auction_info"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    initiator_id = Column(UUID(as_uuid=True), ForeignKey("countries.id"), nullable=False)
    resource_id = Column(UUID(as_uuid=True), ForeignKey("resources.id"), nullable=False)
    quantity = Column(Integer)
    base_price = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    initiator = relationship("Country", back_populates="initiated_auctions")
    resource = relationship("Resource", back_populates="auctions")
    auction_groups = relationship("AuctionGroup", back_populates="auction")

class AuctionGroup(Base):
    __tablename__ = "auction_groups"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    auction_id = Column(UUID(as_uuid=True), ForeignKey("auction_info.id"), nullable=False)
    group_id = Column(UUID(as_uuid=True), ForeignKey("groups.id"), nullable=False)
    
    auction = relationship("AuctionInfo", back_populates="auction_groups")
    group = relationship("Group", back_populates="auction_groups")
    rounds = relationship("AuctionRound", back_populates="auction_group")

class AuctionRound(Base):
    __tablename__ = "auction_rounds"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    auction_group_id = Column(UUID(as_uuid=True), ForeignKey("auction_groups.id"), nullable=False)
    round_num = Column(Integer, nullable=False)
    winner_id = Column(UUID(as_uuid=True), ForeignKey("countries.id"))
    status = Column(String(20))
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    auction_group = relationship("AuctionGroup", back_populates="rounds")
    winner = relationship("Country", back_populates="auction_rounds_won")
    bids = relationship("AuctionBid", back_populates="round")

class AuctionBid(Base):
    __tablename__ = "auction_bids"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    round_id = Column(UUID(as_uuid=True), ForeignKey("auction_rounds.id"), nullable=False)
    country_id = Column(UUID(as_uuid=True), ForeignKey("countries.id"), nullable=False)
    price = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    round = relationship("AuctionRound", back_populates="bids")
    country = relationship("Country", back_populates="bids")

class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    table_name = Column(String(20))
    record_id = Column(UUID(as_uuid=True))
    action = Column(String(20))
    changed_by = Column(String(20))
    change_data = Column(JSONB)
    timestamp = Column(DateTime, default=datetime.utcnow)