"""
Podatkovni modeli: avtomobil (Car) in uporabnik (User).
"""
from decimal import Decimal

from sqlalchemy import Numeric, SmallInteger, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from werkzeug.security import check_password_hash, generate_password_hash

from .extensions import db

# Dovoljene vrste goriva. V bazi so shranjene angleške kode, prevod v
# slovenščino ali drug jezik pa opravi frontend.
FUEL_TYPES = ("petrol", "diesel", "electric", "hybrid", "lpg")


class Car(db.Model):
    __tablename__ = "cars"

    id: Mapped[int] = mapped_column(primary_key=True)
    # Indeksi so na poljih, po katerih filtriramo in sortiramo.
    brand: Mapped[str] = mapped_column(String(50), index=True)
    model: Mapped[str] = mapped_column(String(50))
    year: Mapped[int] = mapped_column(SmallInteger, index=True)
    # Numeric namesto float, da pri denarju ne pride do napak zaokroževanja.
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), index=True)
    fuel_type: Mapped[str] = mapped_column(String(20))
    doors: Mapped[int] = mapped_column(SmallInteger)
    description: Mapped[str | None] = mapped_column(Text)

    def to_dict(self):
        return {
            "id": self.id,
            "brand": self.brand,
            "model": self.model,
            "year": self.year,
            "price": float(self.price),
            "fuel_type": self.fuel_type,
            "doors": self.doors,
            "description": self.description,
        }


class User(db.Model):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    # unique=True ustvari tudi indeks, ki pospeši iskanje ob prijavi.
    username: Mapped[str] = mapped_column(String(80), unique=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    is_admin: Mapped[bool] = mapped_column(default=False)

    def set_password(self, password):
        """Geslo shrani kot zgoščeno vrednost, nikoli v čistopisu."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {"id": self.id, "username": self.username, "is_admin": self.is_admin}
