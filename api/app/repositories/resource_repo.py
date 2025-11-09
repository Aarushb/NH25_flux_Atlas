from sqlalchemy.orm import Session
from app.models.database import Resource
from typing import List, Optional
from uuid import UUID

class ResourceRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, resource_data: dict) -> Resource:
        resource = Resource(**resource_data)
        self.db.add(resource)
        self.db.commit()
        self.db.refresh(resource)
        return resource
    
    def get(self, resource_id: UUID) -> Optional[Resource]:
        return self.db.query(Resource).filter(Resource.id == resource_id).first()
    
    def get_all(self) -> List[Resource]:
        return self.db.query(Resource).all()
    
    def get_by_name(self, rname: str) -> Optional[Resource]:
        return self.db.query(Resource).filter(Resource.rname == rname).first()