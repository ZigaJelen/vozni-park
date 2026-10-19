"""
Razširitve Flask, ustvarjene brez aplikacije.

Objekte ustvarimo tukaj, z aplikacijo pa jih povežemo šele v create_app()
(init_app). Tako se izognemo krožnim uvozom: models.py in routes lahko
uvozijo `db`, ne da bi uvozili celotno aplikacijo.
"""
from flask_caching import Cache
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Skupni osnovni razred vseh modelov."""


db = SQLAlchemy(model_class=Base)
migrate = Migrate()
jwt = JWTManager()
cors = CORS()
cache = Cache()
