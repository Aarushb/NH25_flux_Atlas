from sqlalchemy.orm import Session
from app.models.database import Country, CountryHolding
from typing import List, Optional

class CountryRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, country_data: dict) -> Country:
        country = Country(**country_data)
        self.db.add(country)
        self.db.commit()
        self.db.refresh(country)
        return country
    
    def get(self, country_id: str) -> Optional[Country]:
        return self.db.query(Country).filter(Country.id == country_id).first()
    
    def get_all(self) -> List[Country]:
        return self.db.query(Country).all()
    
    def get_holdings(self, country_id: str) -> List[CountryHolding]:
        return self.db.query(CountryHolding).filter(CountryHolding.country_id == country_id).all()
    
    def update_holding(self, country_id: str, resource_id: str, quantity_delta: float):
        holding = self.db.query(CountryHolding).filter(
            CountryHolding.country_id == country_id,
            CountryHolding.resource_id == resource_id
        ).first()
        
        if holding:
            holding.quantity += quantity_delta
        else:
            holding = CountryHolding(
                country_id=country_id,
                resource_id=resource_id,
                quantity=quantity_delta
            )
            self.db.add(holding)
        
        self.db.commit()