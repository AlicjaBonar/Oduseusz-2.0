from datetime import date, datetime
from app.models import Traveler, Trip, Stage, Location, City, Country, Notification, TripStatus


class TestNotifications:
    """
    Zbiór testów dotyczących logiki wysyłania powiadomień PUSH.
    """

    def test_create_notification_for_push_user(self, db_session):
        t1 = Traveler(
            first_name="Anna", last_name="Nowak", pesel="99999999999", pref_push=True,
            login="anna.nowak", password_hash="x", email="anna@example.com"
        )
        t2 = Traveler(
            first_name="Tomasz", last_name="Lis", pesel="88888888888", pref_push=False,
            login="tomasz.lis", password_hash="x", email="tomek@example.com"
        )

        db_session.add_all([t1, t2])
        db_session.commit()

        recipients = db_session.query(Traveler).filter(Traveler.pref_push == True).all()

        count = 0
        for traveler in recipients:
            notif = Notification(
                traveler_pesel=traveler.pesel,
                message="Test Message",
                is_read=False,
                created_at=datetime.now()
            )
            db_session.add(notif)
            count += 1
        db_session.commit()

        assert count == 1
        saved_notif = db_session.query(Notification).first()
        assert saved_notif.traveler_pesel == "99999999999"

    def test_country_filtering_logic(self, db_session):
        target_country = Country(name="Włochy")
        other_country = Country(name="Polska")

        city_it = City(name="Rzym", country=target_country)
        city_pl = City(name="Warszawa", country=other_country)

        loc_it = Location(city=city_it, address="Colosseum")
        loc_pl = Location(city=city_pl, address="Pałac Kultury")

        traveler_a = Traveler(
            first_name="Mario", last_name="Rossi",
            pesel="11111111111", pref_push=True, login="traveler.a",
            password_hash="x", email="a@test.com"
        )
        trip_a = Trip(traveler=traveler_a, status=TripStatus.IN_PROGRESS)
        stage_a = Stage(trip=trip_a, location=loc_it, start_date=date.today(), end_date=date.today())

        traveler_b = Traveler(
            first_name="Jan", last_name="Kowalski",
            pesel="22222222222", pref_push=True, login="traveler.b",
            password_hash="x", email="b@test.com"
        )
        trip_b = Trip(traveler=traveler_b, status=TripStatus.IN_PROGRESS)
        stage_b = Stage(trip=trip_b, location=loc_pl, start_date=date.today(), end_date=date.today())

        db_session.add_all([target_country, other_country, city_it, city_pl, loc_it, loc_pl,
                            traveler_a, trip_a, stage_a, traveler_b, trip_b, stage_b])
        db_session.commit()

        query = db_session.query(Traveler).filter(Traveler.pref_push == True)
        query = query.join(Trip).join(Stage).join(Location).join(City).join(Country)

        query = query.filter(Country.name == "Włochy")

        results = query.all()

        assert len(results) == 1
        assert results[0].pesel == "11111111111"