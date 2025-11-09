from sqlalchemy.orm import Session
from app.models.database import CountryResource
from typing import List, Optional
from uuid import UUID

class CountryResourceRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, cr_data: dict) -> CountryResource:
        cr = CountryResource(**cr_data)
        self.db.add(cr)
        self.db.commit()
        self.db.refresh(cr)
        return cr
    
    def get(self, country_id: UUID, resource_id: UUID) -> Optional[CountryResource]:
        return self.db.query(CountryResource).filter(
            CountryResource.country_id == country_id,
            CountryResource.resource_id == resource_id,
            CountryResource.is_deleted == False
        ).first()
    
    def get_by_country(self, country_id: UUID) -> List[CountryResource]:
        return self.db.query(CountryResource).filter(
            CountryResource.country_id == country_id,
            CountryResource.is_deleted == False
        ).all()
    
    def update_quantity(self, country_id: UUID, resource_id: UUID, quantity_delta: float):
        cr = self.get(country_id, resource_id)
        if cr:
            cr.quantity = (cr.quantity or 0) + quantity_delta
            self.db.commit()