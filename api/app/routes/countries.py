from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models.schemas import CountryCreate, CountryResponse, HoldingResponse
from app.repositories.country_repo import CountryRepository
from typing import List

router = APIRouter(prefix="/countries", tags=["countries"])

def get_db():
    from app.main import SessionLocal
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=CountryResponse)
def create_country(country: CountryCreate, db: Session = Depends(get_db)):
    repo = CountryRepository(db)
    existing = repo.get(country.id)
    if existing:
        raise HTTPException(status_code=400, detail="Country already exists")
    return repo.create(country.dict())

@router.get("/", response_model=List[CountryResponse])
def list_countries(db: Session = Depends(get_db)):
    repo = CountryRepository(db)
    return repo.get_all()

@router.get("/{country_id}", response_model=CountryResponse)
def get_country(country_id: str, db: Session = Depends(get_db)):
    repo = CountryRepository(db)
    country = repo.get(country_id)
    if not country:
        raise HTTPException(status_code=404, detail="Country not found")
    return country

@router.get("/{country_id}/holdings", response_model=List[HoldingResponse])
def get_country_holdings(country_id: str, db: Session = Depends(get_db)):
    repo = CountryRepository(db)
    holdings = repo.get_holdings(country_id)
    return holdings