"""
Skupni pripomočki za teste.

Testi tečejo proti pravi MariaDB iz docker-compose.test.yml. Shemo ustvarimo z
istimi migracijami kot v produkciji, pred vsakim testom pa tabele izpraznimo.
Na voljo so odjemalec, žetoni za navadnega uporabnika in administratorja ter
vzorčni avtomobili.
"""
from decimal import Decimal

import pytest
from flask_jwt_extended import create_access_token
from flask_migrate import upgrade

from app import create_app
from app.config import Config
from app.extensions import db
from app.models import Car, User

PASSWORD = "geslo1234"

# Vzorčni avtomobili z znanimi vrednostmi, da lahko testi natančno preverijo
# filtre, sortiranje in paginacijo: (znamka, model, letnik, cena, gorivo, vrata)
SAMPLE_CARS = [
    ("Audi", "A4", 2019, "21900.00", "diesel", 4),
    ("Audi", "Q3", 2021, "33500.00", "petrol", 5),
    ("BMW", "320d", 2018, "19800.00", "diesel", 4),
    ("BMW", "i3", 2020, "22900.00", "electric", 5),
    ("Škoda", "Octavia", 2020, "18400.00", "diesel", 5),
    ("Škoda", "Fabia", 2013, "4900.00", "petrol", 5),
    ("Tesla", "Model 3", 2021, "35900.00", "electric", 4),
    ("Dacia", "Duster", 2019, "11500.00", "lpg", 5),
    ("Fiat", "500", 2017, "8900.00", "petrol", 3),
    ("Opel", "Astra", 2012, "3900.00", "diesel", 5),
]


class TestingConfig(Config):
    """Produkcijska nastavitev (baza in JWT iz okolja), le predpomnilnik je v pomnilniku."""
    TESTING = True
    CACHE_TYPE = "SimpleCache"


@pytest.fixture(scope="session")
def schema():
    """Ustvari tabele z migracijami (flask db upgrade), enako kot ob zagonu v produkciji."""
    app = create_app(TestingConfig)
    with app.app_context():
        upgrade()
        db.engine.dispose()


@pytest.fixture
def app(schema):
    """Nova aplikacija s praznimi tabelami za vsak test."""
    app = create_app(TestingConfig)
    with app.app_context():
        db.session.execute(db.text("TRUNCATE TABLE cars"))
        db.session.execute(db.text("TRUNCATE TABLE users"))
        db.session.commit()
    yield app
    with app.app_context():
        db.session.remove()
        db.engine.dispose()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def password():
    """Geslo, ki ga imajo vsi uporabniki iz make_user."""
    return PASSWORD


@pytest.fixture
def make_user(app):
    """Tovarna uporabnikov: make_user("ime", is_admin=True) vrne id uporabnika."""

    def _make_user(username, is_admin=False):
        with app.app_context():
            user = User(username=username, is_admin=is_admin)
            user.set_password(PASSWORD)
            db.session.add(user)
            db.session.commit()
            return user.id

    return _make_user


@pytest.fixture
def auth_headers(app):
    """Tovarna glav: auth_headers(user_id, is_admin) vrne {"Authorization": "Bearer ..."}."""

    def _auth_headers(user_id, is_admin=False):
        with app.app_context():
            token = create_access_token(identity=str(user_id), additional_claims={"is_admin": is_admin})
        return {"Authorization": f"Bearer {token}"}

    return _auth_headers


@pytest.fixture
def admin_headers(make_user, auth_headers):
    return auth_headers(make_user("admin", is_admin=True), is_admin=True)


@pytest.fixture
def user_headers(make_user, auth_headers):
    return auth_headers(make_user("janez"), is_admin=False)


@pytest.fixture
def cars(app):
    """Vstavi vzorčne avtomobile in vrne njihove id-je v vrstnem redu vstavljanja."""
    with app.app_context():
        objects = [
            Car(brand=brand, model=model, year=year, price=Decimal(price), fuel_type=fuel, doors=doors)
            for brand, model, year, price, fuel, doors in SAMPLE_CARS
        ]
        db.session.add_all(objects)
        db.session.commit()
        return [car.id for car in objects]


@pytest.fixture
def valid_car():
    """Veljavno telo zahtevka za POST in PUT."""
    return {
        "brand": "Seat",
        "model": "Leon",
        "year": 2023,
        "price": 21900.5,
        "fuel_type": "petrol",
        "doors": 5,
        "description": "Nov avto",
    }
