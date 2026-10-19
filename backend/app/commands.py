"""
Ukazi za Flask CLI:

    flask create-admin   ustvari uporabnika z administratorskimi pravicami
    flask seed           naloži vzorčne avtomobile
"""
from decimal import Decimal

import click

from .extensions import db
from .models import Car, User

MIN_PASSWORD_LENGTH = 4

# (znamka, model, letnik, cena, gorivo, vrata, opis)
SAMPLE_CARS = [
    ("Audi", "A4", 2019, "21900.00", "diesel", 4, "Servisna knjiga, prvi lastnik, kovinska barva."),
    ("Audi", "Q3", 2021, "33500.00", "petrol", 5, "Quattro pogon, navigacija, LED žarometi."),
    ("BMW", "320d", 2018, "19800.00", "diesel", 4, "Avtomatski menjalnik, športni paket."),
    ("BMW", "i3", 2020, "22900.00", "electric", 5, "Doseg do 300 km, polnjenje CCS."),
    ("BMW", "Z4", 2010, "17500.00", "petrol", 2, "Kabriolet, odlično ohranjen."),
    ("Volkswagen", "Golf", 2017, "12900.00", "diesel", 5, "Ekonomičen, redno servisiran."),
    ("Volkswagen", "Polo", 2015, "7500.00", "petrol", 5, "Idealen mestni avto."),
    ("Škoda", "Octavia", 2020, "18400.00", "diesel", 5, "Karavan z velikim prtljažnikom."),
    ("Škoda", "Fabia", 2013, "4900.00", "petrol", 5, "Zanesljiv in poceni za vzdrževanje."),
    ("Renault", "Clio", 2016, "6900.00", "petrol", 5, "Mestni avto s klimo."),
    ("Renault", "Zoe", 2019, "11900.00", "electric", 5, "Baterija v lasti, doseg do 300 km."),
    ("Toyota", "Yaris", 2021, "17500.00", "hybrid", 5, "Hibridni pogon, nizka poraba."),
    ("Toyota", "Corolla", 2022, "25900.00", "hybrid", 4, "Hibrid z avtomatskim menjalnikom."),
    ("Tesla", "Model 3", 2021, "35900.00", "electric", 4, "Long Range, autopilot."),
    ("Mercedes-Benz", "C 220 d", 2018, "24900.00", "diesel", 4, "AMG paket, usnjena notranjost."),
    ("Ford", "Focus", 2014, "5900.00", "diesel", 5, "Servisirano pri pooblaščenem serviserju."),
    ("Ford", "Fiesta", 2018, "9800.00", "petrol", 3, "Športna izvedba ST-Line."),
    ("Peugeot", "208", 2020, "13900.00", "petrol", 5, "Digitalna armaturna plošča."),
    ("Opel", "Astra", 2012, "3900.00", "diesel", 5, "Ugodna cena, potreben je manjši servis."),
    ("Fiat", "500", 2017, "8900.00", "petrol", 3, "Retro videz, panoramska streha."),
    ("Hyundai", "Ioniq", 2019, "16900.00", "hybrid", 5, "Hibrid z odlično porabo."),
    ("Kia", "Sportage", 2020, "23900.00", "diesel", 5, "Pogon 4x4, vlečna kljuka."),
    ("Dacia", "Duster", 2019, "11500.00", "lpg", 5, "Dvojni sistem: bencin in plin."),
    ("Dacia", "Sandero", 2015, "4500.00", "petrol", 5, None),
    ("Citroën", "C3", 2016, "6400.00", "petrol", 5, "Kamera za vzvratno vožnjo."),
]


def register_commands(app):
    @app.cli.command("create-admin")
    @click.option("--username", prompt="Uporabniško ime", help="Uporabniško ime administratorja.")
    @click.password_option("--password", prompt="Geslo", help="Geslo (pri vnosu v ukazni vrstici skrito).")
    def create_admin(username, password):
        """Ustvari uporabnika z administratorskimi pravicami."""
        username = username.strip()
        if not username or len(username) > 80:
            raise click.ClickException("Uporabniško ime mora imeti od 1 do 80 znakov.")
        if len(password) < MIN_PASSWORD_LENGTH:
            raise click.ClickException(f"Geslo mora imeti vsaj {MIN_PASSWORD_LENGTH} znakov.")
        if db.session.scalar(db.select(User).where(User.username == username)):
            raise click.ClickException(f"Uporabnik '{username}' že obstaja.")

        user = User(username=username, is_admin=True)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        click.echo(f"Administrator '{username}' je ustvarjen.")

    @app.cli.command("seed")
    def seed():
        """Naloži vzorčne avtomobile (samo če je tabela cars prazna)."""
        if db.session.scalar(db.select(db.func.count()).select_from(Car)):
            click.echo("Tabela cars ni prazna, nič ni dodano.")
            return

        db.session.add_all(
            Car(
                brand=brand,
                model=model,
                year=year,
                price=Decimal(price),
                fuel_type=fuel_type,
                doors=doors,
                description=description,
            )
            for brand, model, year, price, fuel_type, doors, description in SAMPLE_CARS
        )
        db.session.commit()
        click.echo(f"Dodanih avtomobilov: {len(SAMPLE_CARS)}.")
