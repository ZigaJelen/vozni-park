"""
Avtomobili: seznam s filtriranjem, sortiranjem in paginacijo ter dodajanje,
urejanje in brisanje (samo administrator).
"""
from decimal import Decimal, InvalidOperation

from flask import Blueprint, jsonify, request

from ..auth_utils import admin_required
from ..extensions import cache, db
from ..models import Car
from ..validation import MAX_PRICE, validate_car

bp = Blueprint("cars", __name__)

SORT_COLUMNS = {"id": Car.id, "brand": Car.brand, "year": Car.year, "price": Car.price}
DEFAULT_PER_PAGE = 10
MAX_PER_PAGE = 100
MAX_PAGE = 1_000_000


def _invalid(errors):
    """400 odgovor z napakami po poljih (enak zapis za telo zahtevka in parametre poizvedbe)."""
    return jsonify(error="Bad Request", message="Neveljavni podatki.", errors=errors), 400


def _int_param(name, default, minimum, maximum, errors):
    """Prebere celoštevilski parameter poizvedbe; napako zapiše v `errors`."""
    raw = request.args.get(name, "").strip()
    if not raw:
        return default
    try:
        value = int(raw)
    except ValueError:
        errors[name] = "Mora biti celo število."
        return default
    if not minimum <= value <= maximum:
        errors[name] = f"Mora biti med {minimum} in {maximum}."
        return default
    return value


def _price_param(name, errors):
    """Prebere ceno iz parametra poizvedbe (neobvezno); napako zapiše v `errors`."""
    raw = request.args.get(name, "").strip()
    if not raw:
        return None
    try:
        value = Decimal(raw)
    except InvalidOperation:
        errors[name] = "Mora biti število."
        return None
    if not value.is_finite() or not 0 <= value <= MAX_PRICE:
        errors[name] = f"Mora biti med 0 in {MAX_PRICE}."
        return None
    return value


def _is_ok(response):
    """Predpomnimo samo uspešne odgovore; 400 z napakami po poljih ne."""
    return getattr(response, "status_code", None) == 200


@bp.get("/cars")
@cache.cached(query_string=True, response_filter=_is_ok, response_hit_indication=True)
def list_cars():
    """
    GET /api/cars: seznam avtomobilov.

    Parametri (vsi neobvezni): brand, price_min, price_max,
    sort (id, brand, year, price), order (asc, desc), page, per_page.
    """
    errors = {}
    brand = request.args.get("brand", "").strip()
    price_min = _price_param("price_min", errors)
    price_max = _price_param("price_max", errors)
    if price_min is not None and price_max is not None and price_min > price_max:
        errors["price_min"] = "Ne sme biti večja od price_max."

    sort = request.args.get("sort", "id")
    if sort not in SORT_COLUMNS:
        errors["sort"] = f"Dovoljene vrednosti: {', '.join(SORT_COLUMNS)}."
    order = request.args.get("order", "asc")
    if order not in ("asc", "desc"):
        errors["order"] = "Dovoljeni vrednosti: asc, desc."

    page = _int_param("page", 1, 1, MAX_PAGE, errors)
    per_page = _int_param("per_page", DEFAULT_PER_PAGE, 1, MAX_PER_PAGE, errors)
    if errors:
        return _invalid(errors)

    query = db.select(Car)
    if brand:
        query = query.where(Car.brand == brand)
    if price_min is not None:
        query = query.where(Car.price >= price_min)
    if price_max is not None:
        query = query.where(Car.price <= price_max)

    column = SORT_COLUMNS[sort]
    # Car.id na koncu daje stabilen vrstni red pri enakih vrednostih; brez njega
    # bi se avtomobili med stranmi lahko podvajali ali izpuščali.
    query = query.order_by(column.desc() if order == "desc" else column.asc(), Car.id)

    pagination = db.paginate(query, page=page, per_page=per_page, error_out=False)
    return jsonify(
        items=[car.to_dict() for car in pagination.items],
        page=pagination.page,
        per_page=pagination.per_page,
        total=pagination.total,
        pages=pagination.pages,
    )


@bp.get("/cars/<int:car_id>")
def get_car(car_id):
    car = db.get_or_404(Car, car_id, description="Avtomobil ne obstaja.")
    return jsonify(car.to_dict())


@bp.post("/cars")
@admin_required
def create_car():
    """POST /api/cars: doda avtomobil (samo administrator)."""
    data, errors = validate_car(request.get_json(silent=True))
    if errors:
        return _invalid(errors)

    car = Car(**data)
    db.session.add(car)
    db.session.commit()
    cache.clear()  # seznam in znamke takoj pokažejo spremembo
    return jsonify(car.to_dict()), 201


@bp.put("/cars/<int:car_id>")
@admin_required
def update_car(car_id):
    """PUT /api/cars/<id>: zamenja podatke avtomobila (samo administrator)."""
    car = db.get_or_404(Car, car_id, description="Avtomobil ne obstaja.")
    data, errors = validate_car(request.get_json(silent=True))
    if errors:
        return _invalid(errors)

    for field, value in data.items():
        setattr(car, field, value)
    db.session.commit()
    cache.clear()
    return jsonify(car.to_dict())


@bp.delete("/cars/<int:car_id>")
@admin_required
def delete_car(car_id):
    """DELETE /api/cars/<id>: izbriše avtomobil (samo administrator)."""
    car = db.get_or_404(Car, car_id, description="Avtomobil ne obstaja.")
    db.session.delete(car)
    db.session.commit()
    cache.clear()
    return "", 204


@bp.get("/brands")
@cache.cached(response_hit_indication=True)
def list_brands():
    """GET /api/brands: abecedni seznam znamk (za filter v frontendu)."""
    brands = db.session.scalars(db.select(Car.brand).distinct().order_by(Car.brand)).all()
    return jsonify(brands)
