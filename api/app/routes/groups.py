from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models.schemas import GroupCreate, GroupResponse
from app.repositories.group_repo import GroupRepository
from typing import List
from uuid import UUID

router = APIRouter(prefix="/groups", tags=["groups"])

def get_db():
    from app.main import SessionLocal
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=GroupResponse)
def create_group(group: GroupCreate, db: Session = Depends(get_db)):
    repo = GroupRepository(db)
    existing = repo.get_by_name(group.name)
    if existing:
        raise HTTPException(status_code=400, detail="Group already exists")
    return repo.create(group.dict())

@router.get("/", response_model=List[GroupResponse])
def list_groups(db: Session = Depends(get_db)):
    repo = GroupRepository(db)
    return repo.get_all()

@router.get("/{group_id}", response_model=GroupResponse)
def get_group(group_id: UUID, db: Session = Depends(get_db)):
s   repo = GroupRepository(db)
    group = repo.get(group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    return group