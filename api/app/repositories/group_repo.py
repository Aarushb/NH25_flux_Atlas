from sqlalchemy.orm import Session
from app.models.database import Group
from typing import List, Optional
from uuid import UUID

class GroupRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, group_data: dict) -> Group:
        group = Group(**group_data)
        self.db.add(group)
        self.db.commit()
        self.db.refresh(group)
        return group
    
    def get(self, group_id: UUID) -> Optional[Group]:
        return self.db.query(Group).filter(Group.id == group_id).first()
    
    def get_all(self) -> List[Group]:
        return self.db.query(Group).all()
    
    def get_by_name(self, name: str) -> Optional[Group]:
        return self.db.query(Group).filter(Group.name == name).first()