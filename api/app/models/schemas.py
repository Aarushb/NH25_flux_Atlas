from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from uuid import UUID

class GroupCreate(BaseModel):
    name: str
    low_ppp: Optional[int] = None
    high_ppp: Optional[int] = None
    description: Optional[str] = None

class GroupResponse(BaseModel):
    id: UUID
    name: str
    low_ppp: Optional[int]
    high_ppp: Optional[int]
    description: Optional[str]
    
    class Config:
        from_attributes = True

class CountryCreate(BaseModel):
    cname: str
    group_id: Optional[UUID] = None
    carbon_budget: Optional[float] = None
    ppp: Optional[int] = None
    created_by: Optional[str] = None

class CountryResponse(BaseModel):
    id: UUID
    cname: str
    group_id: Optional[UUID]
    carbon_budget: Optional[float]
    ppp: Optional[int]
    is_deleted: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class ResourceCreate(BaseModel):
    rname: str
    price: Optional[float] = None
    description: Optional[str] = None

class ResourceResponse(BaseModel):
    id: UUID
    rname: str
    price: Optional[float]
    description: Optional[str]
    class Config:
        from_attributes = True

class CountryResourceCreate(BaseModel):
    country_id: UUID
    resource_id: UUID
    supply: Optional[int] = None
    demand: Optional[int] = None
    quantity: Optional[float] = None
    unit: Optional[str] = None
    created_by: Optional[str] = None

class CountryResourceResponse(BaseModel):
    id: UUID
    country_id: UUID
    resource_id: UUID
    supply: Optional[int]
    demand: Optional[int]
    quantity: Optional[float]
    unit: Optional[str]
    
    class Config:
        from_attributes = True

class AuctionInfoCreate(BaseModel):
    initiator_id: UUID
    resource_id: UUID
    quantity: int
    base_price: float

class AuctionInfoResponse(BaseModel):
    id: UUID
    initiator_id: UUID
    resource_id: UUID
    quantity: int
    base_price: float
    timestamp: datetime
    
    class Config:
        from_attributes = True

class AuctionGroupCreate(BaseModel):
    auction_id: UUID
    group_id: UUID

class AuctionGroupResponse(BaseModel):
    id: UUID
    auction_id: UUID
    group_id: UUID
    
    class Config:
        from_attributes = True

class AuctionRoundCreate(BaseModel):
    auction_group_id: UUID
    round_num: int
    status: str

class AuctionRoundResponse(BaseModel):
    id: UUID
    auction_group_id: UUID
    round_num: int
    winner_id: Optional[UUID]
    status: str
    timestamp: datetime
    
    class Config:
        from_attributes = True

class AuctionBidCreate(BaseModel):
    round_id: UUID
    country_id: UUID
    price: float

class AuctionBidResponse(BaseModel):
    id: UUID
    round_id: UUID
    country_id: UUID
    price: float
    timestamp: datetime
    
    class Config:
        from_attributes = True