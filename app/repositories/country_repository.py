from sqlalchemy.orm import Session
from app.models import Country
from typing import Optional, List


class CountryRepository:
    
    def __init__(self, db: Session):
        self.db = db
    
    def find_by_id(self, country_id: int) -> Optional[Country]:
        return self.db.query(Country).filter_by(id=country_id).first()
    
    def find_by_name(self, name: str) -> Optional[Country]:
        return self.db.query(Country).filter_by(name=name).first()
    
    def get_all(self) -> List[Country]:
        return self.db.query(Country).all()
    
    def create(self, country: Country) -> Country:
        self.db.add(country)
        self.db.flush()
        return country
    
    def update(self, country: Country) -> Country:
        self.db.flush()
        return country
    
    def delete(self, country: Country) -> None:
        self.db.delete(country)
