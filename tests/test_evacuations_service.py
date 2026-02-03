import pytest
from datetime import datetime
from app.services.evacuation_service import EvacuationService
from app.models import Country, City, EvacuationStatus

@pytest.fixture
def evacuation_service(db_session):
    """Inicjalizuje serwis z użyciem testowej sesji bazy danych."""
    return EvacuationService(db_session)

@pytest.fixture
def setup_data(db_session):
    """Opcjonalny fixture do przygotowania podstawowych danych (kraj, miasto)."""
    poland = Country(id=1, name="Poland")
    wroclaw = City(id=1, name="Wroclaw", country_id=1)
    db_session.add(poland)
    db_session.add(wroclaw)
    db_session.commit()
    return {"country_id": 1, "city_id": 1}

# --- TESTY ---

def test_create_evacuation_db(evacuation_service, setup_data):
    # Arrange
    data = {
        "action_name": "Operacja Ratunkowa",
        "event_description": "Powódź",
        "start_date": "2026-03-01T12:00:00",
        "country_id": setup_data["country_id"],
        "city_id": setup_data["city_id"]
    }

    # Act
    result = evacuation_service.create_evacuation(data)

    # Assert
    assert result["id"] is not None
    assert result["action_name"] == "Operacja Ratunkowa"
    assert result["status"] == "planned"

def test_get_all_evacuations_db(evacuation_service, setup_data):
    # Arrange
    data1 = {
        "action_name": "Ewak 1",
        "event_description": "Opis 1",
        "start_date": "2026-01-01T10:00:00",
        "country_id": setup_data["country_id"]
    }
    data2 = {
        "action_name": "Ewak 2",
        "event_description": "Opis 2",
        "start_date": "2026-02-01T10:00:00",
        "country_id": setup_data["country_id"]
    }
    evacuation_service.create_evacuation(data1)
    evacuation_service.create_evacuation(data2)

    # Act
    evacuations = evacuation_service.get_all_evacuations()

    # Assert
    assert len(evacuations) == 2
    assert evacuations[0]["action_name"] == "Ewak 1"

def test_update_evacuation_db(evacuation_service, setup_data):
    # Arrange - najpierw tworzymy rekord
    created = evacuation_service.create_evacuation({
        "action_name": "Stara Nazwa",
        "event_description": "Stary Opis",
        "start_date": "2026-01-01T10:00:00",
        "country_id": setup_data["country_id"]
    })
    
    update_data = {
        "action_name": "Nowa Nazwa",
        "status": "in_progress"
    }

    # Act
    updated = evacuation_service.update_evacuation(created["id"], update_data)

    # Assert
    assert updated["action_name"] == "Nowa Nazwa"
    assert updated["status"] == "in_progress"

def test_delete_evacuation_db(evacuation_service, setup_data):
    # Arrange
    created = evacuation_service.create_evacuation({
        "action_name": "Do usuniecia",
        "event_description": "Opis",
        "start_date": "2026-01-01T10:00:00",
        "country_id": setup_data["country_id"]
    })

    # Act
    delete_result = evacuation_service.delete_evacuation(created["id"])
    get_result = evacuation_service.get_evacuation_by_id(created["id"])

    # Assert
    assert delete_result is True
    assert get_result is None

def test_create_evacuation_invalid_date(evacuation_service, setup_data):
    # Arrange
    bad_data = {
        "action_name": "Test",
        "event_description": "Test",
        "start_date": "nie-data" # To powinno rzucić błędem datetime.fromisoformat
    }

    # Act & Assert
    with pytest.raises(ValueError):
        evacuation_service.create_evacuation(bad_data)