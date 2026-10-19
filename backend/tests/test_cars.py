"""Testi poti /api/cars in /api/brands: seznam, filtri, sortiranje, paginacija, CRUD in pravice."""
import unicodedata

import pytest


def items(response):
    return response.get_json()["items"]


def collation_key(text):
    """Ključ za razvrščanje kot v MariaDB (utf8mb4_uca1400_ai_ci): brez naglasov in velikosti črk."""
    decomposed = unicodedata.normalize("NFD", text)
    return "".join(char for char in decomposed if not unicodedata.combining(char)).casefold()


# --- seznam in paginacija ---


def test_list_has_expected_shape(client, cars):
    response = client.get("/api/cars")
    body = response.get_json()

    assert response.status_code == 200
    assert set(body) == {"items", "page", "per_page", "total", "pages"}
    assert (body["total"], body["page"], body["per_page"], body["pages"]) == (10, 1, 10, 1)
    assert len(body["items"]) == 10


def test_pagination_splits_results(client, cars):
    sizes = [len(items(client.get("/api/cars", query_string={"per_page": 3, "page": page}))) for page in (1, 2, 3, 4)]

    assert sizes == [3, 3, 3, 1]


def test_page_beyond_last_is_empty(client, cars):
    body = client.get("/api/cars", query_string={"page": 9}).get_json()

    assert body["items"] == []
    assert body["total"] == 10


def test_pagination_has_no_duplicates_or_gaps(client, cars):
    seen = []
    for page in (1, 2, 3, 4):
        response = client.get("/api/cars", query_string={"sort": "brand", "per_page": 3, "page": page})
        seen += [car["id"] for car in items(response)]

    assert sorted(seen) == sorted(cars)


# --- filtriranje ---


@pytest.mark.parametrize(
    "params, expected_models",
    [
        ({"brand": "Audi"}, {"A4", "Q3"}),
        ({"brand": "Škoda"}, {"Octavia", "Fabia"}),
        ({"brand": "skoda"}, {"Octavia", "Fabia"}),  # MariaDB: filter ne razlikuje šumnikov
        ({"brand": "AUDI"}, {"A4", "Q3"}),  # MariaDB: filter ne razlikuje velikosti črk
        ({"brand": "Neobstaja"}, set()),
        ({"price_min": 20000}, {"A4", "Q3", "i3", "Model 3"}),
        ({"price_max": 5000}, {"Fabia", "Astra"}),
        ({"price_min": 10000, "price_max": 20000}, {"320d", "Octavia", "Duster"}),
        ({"price_min": 8900, "price_max": 8900}, {"500"}),  # meji sta vključeni
        ({"brand": "BMW", "price_max": 20000}, {"320d"}),
    ],
)
def test_filters(client, cars, params, expected_models):
    response = client.get("/api/cars", query_string=params)

    assert response.status_code == 200
    assert {car["model"] for car in items(response)} == expected_models
    assert response.get_json()["total"] == len(expected_models)


def test_empty_brand_filter_is_ignored(client, cars):
    response = client.get("/api/cars", query_string={"brand": ""})

    assert response.get_json()["total"] == 10


# --- sortiranje ---


@pytest.mark.parametrize("field", ["brand", "year", "price"])
@pytest.mark.parametrize("order", ["asc", "desc"])
def test_sorting(client, cars, field, order):
    response = client.get("/api/cars", query_string={"sort": field, "order": order})
    values = [car[field] for car in items(response)]
    key = collation_key if field == "brand" else None  # MariaDB: znamke po collationu

    assert values == sorted(values, key=key, reverse=(order == "desc"))


# --- neveljavni parametri ---


@pytest.mark.parametrize(
    "params",
    [
        {"page": 0},
        {"page": -1},
        {"page": "abc"},
        {"per_page": 0},
        {"per_page": 101},
        {"per_page": "abc"},
        {"sort": "foo"},
        {"order": "up"},
        {"price_min": "abc"},
        {"price_min": -5},
        {"price_max": "NaN"},
        {"price_max": 10**12},
    ],
)
def test_invalid_list_params_return_400(client, cars, params):
    response = client.get("/api/cars", query_string=params)

    assert response.status_code == 400
    assert set(response.get_json()["errors"]) == set(params)


def test_price_min_greater_than_price_max_returns_400(client, cars):
    response = client.get("/api/cars", query_string={"price_min": 5000, "price_max": 1000})

    assert response.status_code == 400
    assert "price_min" in response.get_json()["errors"]


def test_multiple_invalid_params_are_all_reported(client, cars):
    response = client.get("/api/cars", query_string={"sort": "foo", "order": "up", "page": "x"})

    assert set(response.get_json()["errors"]) == {"sort", "order", "page"}


# --- en avtomobil, znamke, napake ---


def test_get_car(client, cars):
    response = client.get(f"/api/cars/{cars[0]}")
    body = response.get_json()

    assert response.status_code == 200
    assert (body["brand"], body["model"], body["price"]) == ("Audi", "A4", 21900.0)


def test_get_missing_car_returns_json_404(client, cars):
    response = client.get("/api/cars/9999")

    assert response.status_code == 404
    assert response.get_json()["message"] == "Avtomobil ne obstaja."


def test_unknown_route_returns_json_404(client):
    response = client.get("/api/ne-obstaja")

    assert response.status_code == 404
    assert response.get_json()["error"] == "Not Found"


def test_brands_are_unique_and_sorted(client, cars):
    brands = client.get("/api/brands").get_json()

    assert len(brands) == 7  # obe Škodi se združita v eno znamko
    assert brands == sorted(brands, key=collation_key)  # MariaDB: Škoda stoji pred Teslo


# --- pravice za pisanje ---

WRITE_ENDPOINTS = [("post", "/api/cars"), ("put", "/api/cars/1"), ("delete", "/api/cars/1")]


@pytest.mark.parametrize("method, path", WRITE_ENDPOINTS)
def test_write_endpoints_require_login(client, cars, method, path):
    response = getattr(client, method)(path, json={})

    assert response.status_code == 401


@pytest.mark.parametrize("method, path", WRITE_ENDPOINTS)
def test_write_endpoints_forbidden_for_regular_user(client, cars, user_headers, method, path):
    response = getattr(client, method)(path, json={}, headers=user_headers)

    assert response.status_code == 403


# --- dodajanje ---


def test_admin_creates_car(client, admin_headers, valid_car):
    response = client.post("/api/cars", json=valid_car, headers=admin_headers)
    body = response.get_json()

    assert response.status_code == 201
    assert (body["brand"], body["price"]) == ("Seat", 21900.5)
    assert client.get(f"/api/cars/{body['id']}").status_code == 200


def test_create_trims_text_and_ignores_id(client, admin_headers, valid_car):
    response = client.post("/api/cars", json={**valid_car, "brand": "  Seat  ", "id": 999}, headers=admin_headers)
    body = response.get_json()

    assert body["brand"] == "Seat"
    assert body["id"] != 999


@pytest.mark.parametrize(
    "changes, field",
    [
        ({"brand": ""}, "brand"),
        ({"model": "   "}, "model"),
        ({"year": "2020"}, "year"),
        ({"year": 1800}, "year"),
        ({"price": 0}, "price"),
        ({"price": 10.505}, "price"),
        ({"fuel_type": "Diesel"}, "fuel_type"),
        ({"doors": 6}, "doors"),
        ({"description": 5}, "description"),
    ],
)
def test_create_rejects_invalid_values(client, admin_headers, valid_car, changes, field):
    response = client.post("/api/cars", json={**valid_car, **changes}, headers=admin_headers)

    assert response.status_code == 400
    assert field in response.get_json()["errors"]


def test_create_reports_all_missing_fields(client, admin_headers):
    response = client.post("/api/cars", json={}, headers=admin_headers)

    assert set(response.get_json()["errors"]) == {"brand", "model", "year", "price", "fuel_type", "doors"}


def test_create_rejects_non_json_body(client, admin_headers):
    response = client.post("/api/cars", data="abc", content_type="text/plain", headers=admin_headers)

    assert response.status_code == 400


def test_invalid_create_saves_nothing(client, admin_headers, cars, valid_car):
    client.post("/api/cars", json={**valid_car, "year": 1800}, headers=admin_headers)

    assert client.get("/api/cars").get_json()["total"] == 10


# --- urejanje ---


def test_admin_updates_car(client, admin_headers, cars, valid_car):
    response = client.put(f"/api/cars/{cars[0]}", json=valid_car, headers=admin_headers)

    assert response.status_code == 200
    assert response.get_json()["model"] == "Leon"
    assert client.get(f"/api/cars/{cars[0]}").get_json()["model"] == "Leon"


def test_update_missing_car_returns_404(client, admin_headers, valid_car):
    response = client.put("/api/cars/9999", json=valid_car, headers=admin_headers)

    assert response.status_code == 404


def test_update_requires_all_fields(client, admin_headers, cars):
    response = client.put(f"/api/cars/{cars[0]}", json={"model": "Arona"}, headers=admin_headers)

    assert response.status_code == 400
    assert "brand" in response.get_json()["errors"]


def test_invalid_update_changes_nothing(client, admin_headers, cars, valid_car):
    client.put(f"/api/cars/{cars[0]}", json={**valid_car, "year": 1800}, headers=admin_headers)

    assert client.get(f"/api/cars/{cars[0]}").get_json()["model"] == "A4"


# --- brisanje ---


def test_admin_deletes_car(client, admin_headers, cars):
    response = client.delete(f"/api/cars/{cars[0]}", headers=admin_headers)

    assert response.status_code == 204
    assert response.data == b""
    assert client.get(f"/api/cars/{cars[0]}").status_code == 404
    assert client.get("/api/cars").get_json()["total"] == 9


def test_delete_missing_car_returns_404(client, admin_headers):
    response = client.delete("/api/cars/9999", headers=admin_headers)

    assert response.status_code == 404
