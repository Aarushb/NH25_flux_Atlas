from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models.schemas import OrderCreate, OrderResponse
from app.repositories.order_repo import OrderRepository
from app.services.matching_engine import MatchingEngine
from typing import List
import uuid

router = APIRouter(prefix="/orders", tags=["orders"])

def get_db():
    from app.main import SessionLocal
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=OrderResponse)
def place_order(order: OrderCreate, db: Session = Depends(get_db)):
    repo = OrderRepository(db)
    
    order_data = order.dict()
    order_data["id"] = str(uuid.uuid4())
    
    created_order = repo.create(order_data)
    
    matching_engine = MatchingEngine(db)
    matching_engine.match_orders(order.resource_id)
    
    return created_order

@router.get("/country/{country_id}", response_model=List[OrderResponse])
def get_country_orders(country_id: str, db: Session = Depends(get_db)):
    repo = OrderRepository(db)
    return repo.get_country_orders(country_id)

@router.get("/{order_id}", response_model=OrderResponse)
def get_order(order_id: str, db: Session = Depends(get_db)):
    repo = OrderRepository(db)
    order = repo.get(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

@router.delete("/{order_id}")
def cancel_order(order_id: str, db: Session = Depends(get_db)):
    repo = OrderRepository(db)
    order = repo.get(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    repo.cancel_order(order_id)
    return {"status": "cancelled"}