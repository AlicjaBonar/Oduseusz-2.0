from datetime import date
from app.models import Traveler, Trip, Stage, Location, City, Country, TripStatus
from app.views.app import get_filtered_trips

class TestReports:
    """
    Zbiór testów dotyczących filtrowania wycieczek i generowania raportów.
    """

    def test_filter_trips_by_country_success(self, db_session):
        # 1. Arrange
        country_fr = Country(name="Francja")
        city_par = City(name="Paryż", country=country_fr)
        loc = Location(city=city_par, address="Wieża Eiffla")

        traveler = Traveler(
            first_name="Jan", last_name="Kowalski",
            pesel="12345678901", login="jan.kowalski",
            password_hash="dummy_hash", email="jan@example.com",
            pref_push=True
        )
        trip = Trip(traveler=traveler, status=TripStatus.IN_PROGRESS)
        stage = Stage(trip=trip, location=loc, start_date=date.today(), end_date=date.today())

        db_session.add_all([country_fr, city_par, loc, traveler, trip, stage])
        db_session.commit()

        results = get_filtered_trips(db_session, country="Francja", date_from=None, date_to=None, status=None)

        assert len(results) == 1
        assert results[0].traveler.last_name == "Kowalski"

    def test_filter_trips_no_match(self, db_session):
        country_fr = Country(name="Francja")
        city_par = City(name="Paryż", country=country_fr)
        loc = Location(city=city_par, address="Centrum")

        dummy_traveler = Traveler(
            first_name="Test", last_name="Testowy", pesel="00000000000",
            login="test.dummy", password_hash="x", email="test@test.pl"
        )

        trip = Trip(status=TripStatus.IN_PROGRESS, traveler=dummy_traveler)
        stage = Stage(trip=trip, location=loc, start_date=date.today(), end_date=date.today())

        db_session.add_all([country_fr, city_par, loc, dummy_traveler, trip, stage])
        db_session.commit()

        results = get_filtered_trips(db_session, country="Niemcy", date_from=None, date_to=None, status=None)

        assert len(results) == 0

    def test_status_translation_logic(self):
        status_map = {
            'PLANNED': 'Planowana',
            'IN_PROGRESS': 'W trakcie',
            'COMPLETED': 'Zakończona',
            'CANCELLED': 'Anulowana'
        }
        status_enum_name = "IN_PROGRESS"
        status_missing = "UNKNOWN_STATUS"

        translated_ok = status_map.get(status_enum_name, status_enum_name)
        translated_missing = status_map.get(status_missing, status_missing)

        assert translated_ok == "W trakcie"
        assert translated_missing == "UNKNOWN_STATUS"