"""
Preverjanje vhodnih podatkov za avtomobil.

validate_car() prejme podatke iz JSON telesa zahtevka in vrne par
(podatki, napake). Če je slovar napak prazen, so podatki veljavni in že
pretvorjeni v prave tipe (npr. cena v Decimal), pripravljeni za model.
"""
from datetime import date
from decimal import Decimal, InvalidOperation

from .models import FUEL_TYPES

MAX_TEXT_LENGTH = 50              # dolžina stolpcev brand in model
MAX_DESCRIPTION_LENGTH = 2000
MIN_YEAR = 1886                   # leto izuma avtomobila
MAX_PRICE = Decimal("99999999.99")  # meja stolpca Numeric(10, 2)
MIN_DOORS, MAX_DOORS = 2, 5


def _is_int(value):
    """True za cela števila; bool (True/False) v Pythonu je tudi int, zato ga izločimo."""
    return isinstance(value, int) and not isinstance(value, bool)


def validate_car(data):
    """Preveri podatke za avtomobil. Vrne (podatki, napake)."""
    if not isinstance(data, dict):
        return {}, {"_": "Telo zahtevka mora biti JSON objekt."}

    clean, errors = {}, {}

    for field in ("brand", "model"):
        value = data.get(field)
        if not isinstance(value, str) or not value.strip():
            errors[field] = "Polje je obvezno."
        elif len(value.strip()) > MAX_TEXT_LENGTH:
            errors[field] = f"Največ {MAX_TEXT_LENGTH} znakov."
        else:
            clean[field] = value.strip()

    # Letnik: celo število od izuma avtomobila do prihodnjega leta
    year = data.get("year")
    max_year = date.today().year + 1
    if not _is_int(year):
        errors["year"] = "Letnik mora biti celo število."
    elif not MIN_YEAR <= year <= max_year:
        errors["year"] = f"Letnik mora biti med {MIN_YEAR} in {max_year}."
    else:
        clean["year"] = year

    price = data.get("price")
    try:
        if isinstance(price, bool) or price is None:
            raise InvalidOperation
        price = Decimal(str(price))
    except InvalidOperation:
        errors["price"] = "Cena mora biti število."
    else:
        if not price.is_finite() or price <= 0 or price > MAX_PRICE:
            errors["price"] = f"Cena mora biti večja od 0 in največ {MAX_PRICE}."
        elif price.as_tuple().exponent < -2:
            errors["price"] = "Cena ima lahko največ dve decimalki."
        else:
            clean["price"] = price

    fuel_type = data.get("fuel_type")
    if fuel_type not in FUEL_TYPES:
        errors["fuel_type"] = f"Dovoljene vrednosti: {', '.join(FUEL_TYPES)}."
    else:
        clean["fuel_type"] = fuel_type

    doors = data.get("doors")
    if not _is_int(doors) or not MIN_DOORS <= doors <= MAX_DOORS:
        errors["doors"] = f"Število vrat mora biti celo število od {MIN_DOORS} do {MAX_DOORS}."
    else:
        clean["doors"] = doors

    # Opis: neobvezen; prazen niz shranimo kot None
    description = data.get("description")
    if description is None:
        clean["description"] = None
    elif not isinstance(description, str):
        errors["description"] = "Opis mora biti besedilo."
    elif len(description.strip()) > MAX_DESCRIPTION_LENGTH:
        errors["description"] = f"Največ {MAX_DESCRIPTION_LENGTH} znakov."
    else:
        clean["description"] = description.strip() or None

    return clean, errors
