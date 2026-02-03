import pytest
from datetime import datetime
from app.services.trip_service import TripService, TravelerNotFoundError, TripNotFoundError
from app.models import Traveler, Country, City, TripStatus, Location, Trip, Companion

@pytest.fixture
def trip_service(db_session):
    return TripService(db_session)

@pytest.fixture
def sample_data(db_session):
    """Przygotowanie danych bazowych: podróżny, kraj i miasto."""
    traveler = Traveler(
        pesel="90010112345", 
        first_name="Jan", 
        last_name="Kowalski", 
        login="jkowal", 
        password_hash="hash"
    )
    country = Country(name="Grecja")
    db_session.add(traveler)
    db_session.add(country)
    db_session.flush()

    city = City(name="Ateny", country_id=country.id)
    db_session.add(city)
    db_session.commit()
    
    return {
        "traveler_pesel": traveler.pesel,
        "city_id": city.id
    }

# --- TESTY TWORZENIA ---

def test_create_trip_success(trip_service, sample_data):
    # Arrange
    trip_data = {
        "status": "planned",
        "traveler_pesel": sample_data["traveler_pesel"],
        "stages": [
            {
                "start_date": "2026-05-01T10:00:00",
                "end_date": "2026-05-10T20:00:00",
                "city_id": sample_data["city_id"],
                "address": "Hotel Akropolis 123"
            }
        ]
    }

    # Act
    result = trip_service.create_trip(trip_data)

    # Assert
    assert result["id"] is not None
    assert result["traveler_pesel"] == sample_data["traveler_pesel"]
    assert len(result["stages"]) == 1
    assert result["stages"][0]["location_id"] is not None

def test_create_trip_traveler_not_found(trip_service):
    # Arrange
    trip_data = {"status": "planned", "traveler_pesel": "00000000000"}

    # Act & Assert
    with pytest.raises(TravelerNotFoundError):
        trip_service.create_trip(trip_data)

def test_location_reuse_logic(trip_service, sample_data, db_session):
    """Testuje, czy serwis nie tworzy nowej lokalizacji, jeśli taka sama już istnieje."""
    # 1. Tworzymy lokalizację ręcznie
    existing_loc = Location(address="Dworzec 1", city_id=sample_data["city_id"])
    db_session.add(existing_loc)
    db_session.commit()

    trip_data = {
        "status": "planned",
        "traveler_pesel": sample_data["traveler_pesel"],
        "stages": [
            {
                "start_date": "2026-06-01T10:00:00",
                "end_date": "2026-06-05T10:00:00",
                "city_id": sample_data["city_id"],
                "address": "Dworzec 1" # Ten sam adres
            }
        ]
    }

    # Act
    result = trip_service.create_trip(trip_data)

    # Assert
    # location_id w etapie powinno być takie samo jak nasze existing_loc.id
    assert result["stages"][0]["location_id"] == existing_loc.id

# --- TESTY TOWARZYSZY ---

def test_add_companions_to_trip(trip_service, sample_data, db_session):
    # Arrange - tworzymy najpierw pustą podróż
    trip = Trip(status=TripStatus.PLANNED, traveler_pesel=sample_data["traveler_pesel"])
    db_session.add(trip)
    db_session.commit()

    companions_data = [
        {"pesel": "111111", "first_name": "Anna", "last_name": "Nowak", "age": 25}
    ]

    # Act
    result = trip_service.add_companions_to_trip(trip.id, companions_data, sample_data["traveler_pesel"])

    # Assert
    assert "Dodano 1 companionów" in result["message"]
    # Sprawdzenie czy w bazie faktycznie jest powiązanie
    db_session.refresh(trip)
    assert len(trip.companions) == 1
    assert trip.companions[0].first_name == "Anna"

# --- TESTY AKTUALIZACJI I USUWANIA ---

def test_update_trip_status(trip_service, sample_data, db_session):
    # Arrange
    trip = Trip(status=TripStatus.PLANNED, traveler_pesel=sample_data["traveler_pesel"])
    db_session.add(trip)
    db_session.commit()

    # Act
    updated = trip_service.update_trip(trip.id, {"status": "in_progress"})

    # Assert
    assert updated["status"] == "in_progress"

def test_delete_trip_not_found(trip_service):
    with pytest.raises(TripNotFoundError):
        trip_service.delete_trip(9999)