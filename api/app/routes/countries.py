from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models.schemas import CountryCreate, CountryResponse, CountryResourceResponse
from app.repositories.country_repo import CountryRepository
from app.repositories.country_resource_repo import CountryResourceRepository
from typing import List
from uuid import UUID

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
    existing = repo.get_by_name(country.cname)
    if existing:
        raise HTTPException(status_code=400, detail="Country already exists")
    return repo.create(country.dict())

@router.get("/", response_model=List[CountryResponse])
def list_countries(db: Session = Depends(get_db)):
s   repo = CountryRepository(db)
    return repo.get_all()

@router.get("/{country_id}", response_model=CountryResponse)
def get_country(country_id: UUID, db: Session = Depends(get_db)):
    repo = CountryRepository(db)
    country = repo.get(country_id)
    if not country:
        raise HTTPException(status_code=404, detail="Country not found")
    return country

@router.get("/{country_id}/resources", response_model=List[CountryResourceResponse])
def get_country_resources(country_id: UUID, db: Session = Depends(get_db)):
    repo = CountryResourceRepository(db)
    return repo.get_by_country(country_id)

@router.delete("/{country_id}")
def delete_country(country_id: UUID, deleted_by: str = "system", db: Session = Depends(get_db)):
    repo = CountryRepository(db)
    country = repo.get(country_id)
    if not country:
        raise HTTPException(status_code=404, detail="Country not found")
    repo.soft_delete(country_id, deleted_by)
    return {"status": "deleted"}