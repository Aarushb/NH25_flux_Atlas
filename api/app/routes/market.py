from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.models.schemas import TradeResponse, MarketPriceResponse, ResourceCreate, ResourceResponse
from app.repositories.trade_repo import TradeRepository
from app.models.database import Resource
from typing import List

router = APIRouter(prefix="/market", tags=["market"])

def get_db():
    from app.main import SessionLocal
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/resources", response_model=ResourceResponse)
def create_resource(resource: ResourceCreate, db: Session = Depends(get_db)):
    db_resource = Resource(**resource.dict())
    db.add(db_resource)
    db.commit()
    db.refresh(db_resource)
    return db_resource

@router.get("/resources", response_model=List[ResourceResponse])
def list_resources(db: Session = Depends(get_db)):
    return db.query(Resource).all()

@router.get("/trades", response_model=List[TradeResponse])
def get_trades(db: Session = Depends(get_db)):
    repo = TradeRepository(db)
    return repo.get_all()

@router.get("/trades/{resource_id}", response_model=List[TradeResponse])
def get_resource_trades(resource_id: str, db: Session = Depends(get_db)):
    repo = TradeRepository(db)
    return repo.get_by_resource(resource_id)

@router.get("/price/{resource_id}", response_model=MarketPriceResponse)
def get_market_price(resource_id: str, db: Session = Depends(get_db)):
    repo = TradeRepository(db)
    latest_price = repo.get_latest_market_price(resource_id)
    if not latest_price:
        return {"resource_id": resource_id, "price": 0.0, "timestamp": None}
    return latest_price