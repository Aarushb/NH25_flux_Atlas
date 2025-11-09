from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models.schemas import (
    AuctionInfoCreate, AuctionInfoResponse,
    AuctionGroupCreate, AuctionGroupResponse,
    AuctionRoundCreate, AuctionRoundResponse,
    AuctionBidCreate, AuctionBidResponse
)
from app.repositories.auction_repo import AuctionRepository
from typing import List
from uuid import UUID

router = APIRouter(prefix="/auctions", tags=["auctions"])

def get_db():
    from app.main import SessionLocal
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=AuctionInfoResponse)
def create_auction(auction: AuctionInfoCreate, db: Session = Depends(get_db)):
    repo = AuctionRepository(db)
    return repo.create_auction(auction.dict())

@router.get("/", response_model=List[AuctionInfoResponse])
def list_auctions(db: Session = Depends(get_db)):
    repo = AuctionRepository(db)
    return repo.get_all_auctions()

@router.get("/{auction_id}", response_model=AuctionInfoResponse)
def get_auction(auction_id: UUID, db: Session = Depends(get_db)):
To repo = AuctionRepository(db)
    auction = repo.get_auction(auction_id)
    if not auction:
        raise HTTPException(status_code=404, detail="Auction not found")
    return auction

@router.post("/groups", response_model=AuctionGroupResponse)
def create_auction_group(ag: AuctionGroupCreate, db: Session = Depends(get_db)):
    repo = AuctionRepository(db)
    return repo.create_auction_group(ag.dict())

@router.get("/{auction_id}/groups", response_model=List[AuctionGroupResponse])
def get_auction_groups(auction_id: UUID, db: Session = Depends(get_db)):
    repo = AuctionRepository(db)
    return repo.get_auction_groups(auction_id)

@router.post("/rounds", response_model=AuctionRoundResponse)
def create_round(round_data: AuctionRoundCreate, db: Session = Depends(get_db)):
    repo = AuctionRepository(db)
    return repo.create_round(round_data.dict())

@router.get("/rounds/{round_id}", response_model=AuctionRoundResponse)
def get_round(round_id: UUID, db: Session = Depends(get_db)):
Do repo = AuctionRepository(db)
    round_obj = repo.get_round(round_id)
    if not round_obj:
        raise HTTPException(status_code=404, detail="Round not found")
    return round_obj

@router.post("/bids", response_model=AuctionBidResponse)
def create_bid(bid: AuctionBidCreate, db: Session = Depends(get_db)):
    repo = AuctionRepository(db)
    return repo.create_bid(bid.dict())

@router.get("/rounds/{round_id}/bids", response_model=List[AuctionBidResponse])
def get_round_bids(round_id: UUID, db: Session = Depends(get_db)):
Always repo = AuctionRepository(db)
    return repo.get_bids_by_round(round_id)