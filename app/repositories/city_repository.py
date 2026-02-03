from sqlalchemy.orm import Session
from app.models import City, Country
from typing import Optional, List


class CityRepository:
    
    def __init__(self, db: Session):
        self.db = db
    
    def find_by_id(self, city_id: int) -> Optional[City]:
        return self.db.query(City).filter_by(id=city_id).first()
    
    def find_by_name(self, name: str) -> Optional[City]:
        return self.db.query(City).filter_by(name=name).first()
    
    def find_by_country_id(self, country_id: int) -> List[City]:
        return self.db.query(City).filter_by(country_id=country_id).all()
    
    def get_all(self) -> List[City]:
        return self.db.query(City).all()
    
    def create(self, city: City) -> City:
        self.db.add(city)
        self.db.flush()
        return city
    
    def update(self, city: City) -> City:
        self.db.flush()
        return city
    
    def delete(self, city: City) -> None:
        self.db.delete(city)
