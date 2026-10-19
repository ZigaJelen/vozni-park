"""Enotski testi za validate_car(): brez baze in strežnika."""
from datetime import date
from decimal import Decimal

import pytest

from app.models import FUEL_TYPES
from app.validation import (
    MAX_DESCRIPTION_LENGTH,
    MAX_PRICE,
    MAX_TEXT_LENGTH,
    MIN_YEAR,
    validate_car,
)

MAX_YEAR = date.today().year + 1

VALID = {
    "brand": "Seat",
    "model": "Leon",
    "year": 2023,
    "price": 21900.5,
    "fuel_type": "petrol",
    "doors": 5,
    "description": "Nov avto",
}


def check(**changes):
    """Preveri veljaven avtomobil s spremenjenimi polji; vrne (podatki, napake)."""
    return validate_car({**VALID, **changes})


def test_valid_car_gives_clean_data_and_no_errors():
    data, errors = validate_car(VALID)

    assert errors == {}
    assert data == {**VALID, "price": Decimal("21900.50")}


@pytest.mark.parametrize("body", [None, [], "besedilo", 5])
def test_body_must_be_an_object(body):
    data, errors = validate_car(body)

    assert data == {}
    assert set(errors) == {"_"}


def test_all_missing_fields_are_reported_at_once():
    _, errors = validate_car({})

    assert set(errors) == {"brand", "model", "year", "price", "fuel_type", "doors"}


# --- besedila ---


@pytest.mark.parametrize("field", ["brand", "model"])
def test_text_is_trimmed(field):
    data, errors = check(**{field: "  Seat  "})

    assert errors == {}
    assert data[field] == "Seat"


@pytest.mark.parametrize("field", ["brand", "model"])
@pytest.mark.parametrize("value", ["", "   ", None, 5, ["Seat"]])
def test_text_must_be_non_empty_string(field, value):
    _, errors = check(**{field: value})

    assert field in errors


@pytest.mark.parametrize("field", ["brand", "model"])
def test_text_length_limit(field):
    assert check(**{field: "a" * MAX_TEXT_LENGTH})[1] == {}
    assert field in check(**{field: "a" * (MAX_TEXT_LENGTH + 1)})[1]


# --- letnik ---


@pytest.mark.parametrize("year", [MIN_YEAR, MAX_YEAR])
def test_year_limits_are_accepted(year):
    assert check(year=year)[1] == {}


@pytest.mark.parametrize("year", [MIN_YEAR - 1, MAX_YEAR + 1, "2020", 2020.0, True, None])
def test_year_rejects_invalid_values(year):
    assert "year" in check(year=year)[1]


# --- cena ---


@pytest.mark.parametrize("price, expected", [(1, Decimal("1")), (0.01, Decimal("0.01")), (MAX_PRICE, MAX_PRICE)])
def test_price_limits_are_accepted(price, expected):
    data, errors = check(price=price)

    assert errors == {}
    assert data["price"] == expected


@pytest.mark.parametrize(
    "price",
    [0, -1, MAX_PRICE + Decimal("0.01"), 10.505, True, None, "abc", [], float("nan"), float("inf")],
)
def test_price_rejects_invalid_values(price):
    assert "price" in check(price=price)[1]


# --- gorivo in vrata ---


@pytest.mark.parametrize("fuel_type", FUEL_TYPES)
def test_every_fuel_type_is_accepted(fuel_type):
    assert check(fuel_type=fuel_type)[1] == {}


@pytest.mark.parametrize("fuel_type", ["Diesel", "", "gas", None, 1, []])
def test_fuel_type_rejects_unknown_values(fuel_type):
    assert "fuel_type" in check(fuel_type=fuel_type)[1]


@pytest.mark.parametrize("doors", [2, 3, 4, 5])
def test_doors_accepts_two_to_five(doors):
    assert check(doors=doors)[1] == {}


@pytest.mark.parametrize("doors", [0, 1, 6, 4.0, "4", True, None])
def test_doors_rejects_invalid_values(doors):
    assert "doors" in check(doors=doors)[1]


# --- opis ---


@pytest.mark.parametrize("description", [None, "", "   "])
def test_empty_description_becomes_none(description):
    data, errors = check(description=description)

    assert errors == {}
    assert data["description"] is None


def test_missing_description_is_allowed():
    body = {key: value for key, value in VALID.items() if key != "description"}

    data, errors = validate_car(body)

    assert errors == {}
    assert data["description"] is None


def test_description_length_limit():
    assert check(description="a" * MAX_DESCRIPTION_LENGTH)[1] == {}
    assert "description" in check(description="a" * (MAX_DESCRIPTION_LENGTH + 1))[1]


@pytest.mark.parametrize("description", [5, [], {}, True])
def test_description_must_be_text(description):
    assert "description" in check(description=description)[1]
