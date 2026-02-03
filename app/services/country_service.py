"""
Service dla Country i City - logika biznesowa
"""
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import Dict, Optional, List
from app.models import Country, City
from app.repositories.country_repository import CountryRepository
from app.repositories.city_repository import CityRepository


class CountryServiceError(Exception):
    pass


class CountryAlreadyExistsError(CountryServiceError):
    pass


class CountryNotFoundError(CountryServiceError):
    pass


class CityServiceError(Exception):
    pass


class CityNotFoundError(CityServiceError):
    pass


class CountryService:
    
    def __init__(self, db: Session):
        self.db = db
        self.repository = CountryRepository(db)
    
    def create_country(self, country_data: Dict) -> Dict:

        if not country_data or "name" not in country_data:
            raise ValueError("Field 'name' is required")
        
        # Sprawdzenie czy kraj już istnieje
        existing = self.repository.find_by_name(country_data["name"])
        if existing:
            raise CountryAlreadyExistsError("Kraj z tą nazwą już istnieje")
        
        # Utworzenie nowego kraju
        new_country = Country(name=country_data["name"])
        
        try:
            self.repository.create(new_country)
            self.db.commit()
            return {
                "id": new_country.id,
                "name": new_country.name
            }
        except IntegrityError:
            self.db.rollback()
            raise CountryAlreadyExistsError("Kraj z tą nazwą już istnieje")
        except Exception as e:
            self.db.rollback()
            raise CountryServiceError(f"Błąd podczas tworzenia kraju: {str(e)}")
    
    def get_country_by_id(self, country_id: int) -> Optional[Dict]:
        country = self.repository.find_by_id(country_id)
        if not country:
            return None
        
        return {
            "id": country.id,
            "name": country.name,
            "cities": [{"id": c.id, "name": c.name} for c in country.cities]
        }
    
    def get_all_countries(self) -> List[Dict]:
        countries = self.repository.get_all()
        return [
            {
                "id": country.id,
                "name": country.name,
                "cities": [{"id": c.id, "name": c.name} for c in country.cities]
            }
            for country in countries
        ]


class CityService:
    
    def __init__(self, db: Session):
        self.db = db
        self.city_repository = CityRepository(db)
        self.country_repository = CountryRepository(db)
    
    def create_city(self, city_data: Dict) -> Dict:

        if not city_data or "name" not in city_data or "country_id" not in city_data:
            raise ValueError("Fields 'name' and 'country_id' are required")
        
        # Sprawdzenie czy kraj istnieje
        country = self.country_repository.find_by_id(city_data["country_id"])
        if not country:
            raise CountryNotFoundError("Kraj nie został znaleziony")
        
        # Utworzenie nowego miasta
        new_city = City(name=city_data["name"], country=country)
        
        try:
            self.city_repository.create(new_city)
            self.db.commit()
            return {
                "id": new_city.id,
                "name": new_city.name,
                "country_id": new_city.country_id
            }
        except Exception as e:
            self.db.rollback()
            raise CityServiceError(f"Błąd podczas tworzenia miasta: {str(e)}")
    
    def get_all_cities(self) -> List[Dict]:
        cities = self.city_repository.get_all()
        return [
            {
                "id": city.id,
                "name": city.name,
                "country_id": city.country_id
            }
            for city in cities
        ]
    
    def get_cities_by_country(self, country_id):
        try:
            # Najpierw sprawdzamy, czy kraj w ogóle istnieje
            country = self.db.query(Country).get(country_id)
            if not country:
                raise CountryNotFoundError(f"Country with id {country_id} not found")
            
            # Pobieramy miasta (zakładając, że masz relację w modelu)
            # i zamieniamy je na słowniki za pomocą Twojej metody to_dict()
            return [city.to_dict() for city in country.cities]
        except Exception as e:
            if not isinstance(e, CountryNotFoundError):
                raise CityServiceError(f"Error fetching cities: {str(e)}")
            raise e
