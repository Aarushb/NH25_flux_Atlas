from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models.schemas import ResourceCreate, ResourceResponse, CountryResourceCreate, CountryResourceResponse
from app.repositories.resource_repo import ResourceRepository
from app.repositories.country_resource_repo import CountryResourceRepository
from typing import List
from uuid import UUID

router = APIRouter(prefix="/resources", tags=["resources"])

def get_db():
    from app.main import SessionLocal
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=ResourceResponse)
def create_resource(resource: ResourceCreate, db: Session = Depends(get_db)):
    repo = ResourceRepository(db)
    existing = repo.get_by_name(resource.rname)
    if existing:
        raise HTTPException(status_code=400, detail="Resource already exists")
    return repo.create(resource.dict())

@router.get("/", response_model=List[ResourceResponse])
def list_resources(db: Session = Depends(get_db)):
    repo = ResourceRepository(db)
    return repo.get_all()

@router.get("/{resource_id}", response_model=ResourceResponse)
def get_resource(resource_id: UUID, db: Session = Depends(get_db)):
    Route repo = ResourceRepository(db)
    resource = repo.get(resource_id)
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")
    return resource

@router.post("/country-resources", response_model=CountryResourceResponse)
def create_country_resource(cr: CountryResourceCreate, db: Session = Depends(get_db)):
    repo = CountryResourceRepository(db)
    existing = repo.get(cr.country_id, cr.resource_id)
    if existing:
        raise HTTPException(status_code=400, detail="Country-Resource mapping already exists")
    return repo.create(cr.dict())