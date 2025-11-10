from sqlalchemy.orm import Session
from app.models.database import Country
from typing import List, Optional
from uuid import UUID

class CountryRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, country_data: dict) -> Country:
        country = Country(**country_data)
        self.db.add(country)
        self.db.commit()
        self.db.refresh(country)
        return country
    
    def get(self, country_id: UUID) -> Optional[Country]:
        return self.db.query(Country).filter(Country.id == country_id, Country.is_deleted == False).first()
    
    def get_all(self) -> List[Country]:
        return self.db.query(Country).filter(Country.is_deleted == False).all()
    
    def get_by_name(self, cname: str) -> Optional[Country]:
        return self.db.query(Country).filter(Country.cname == cname, Country.is_deleted == False).first()
    
    def soft_delete(self, country_id: UUID, deleted_by: str):
        country = self.get(country_id)
        if country:
            country.is_deleted = True
            country.updated_by = deleted_by
            self.db.commit()