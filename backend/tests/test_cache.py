"""Testi predpomnjenja: GET /api/cars in /api/brands se predpomnita, ob spremembi podatkov pa izpraznita."""
import pytest


def is_hit(response):
    """Odgovor iz predpomnilnika ima glavo hit_cache."""
    return "hit_cache" in response.headers


@pytest.mark.parametrize("path", ["/api/cars", "/api/brands"])
def test_second_request_is_served_from_cache(client, cars, path):
    first = client.get(path)
    second = client.get(path)

    assert not is_hit(first)
    assert is_hit(second)
    assert second.get_json() == first.get_json()


def test_each_query_string_has_its_own_entry(client, cars):
    client.get("/api/cars?brand=Audi")

    assert not is_hit(client.get("/api/cars?brand=BMW"))
    assert is_hit(client.get("/api/cars?brand=Audi"))


def test_errors_are_not_cached(client, cars):
    first = client.get("/api/cars?sort=bad")
    second = client.get("/api/cars?sort=bad")

    assert first.status_code == second.status_code == 400
    assert not is_hit(second)


def test_single_car_is_not_cached(client, cars):
    client.get(f"/api/cars/{cars[0]}")

    assert not is_hit(client.get(f"/api/cars/{cars[0]}"))


def test_create_clears_cache(client, cars, admin_headers, valid_car):
    client.get("/api/cars")
    client.get("/api/brands")

    client.post("/api/cars", json=valid_car, headers=admin_headers)

    cars_after = client.get("/api/cars")
    assert not is_hit(cars_after)
    assert cars_after.get_json()["total"] == 11
    assert "Seat" in client.get("/api/brands").get_json()


def test_update_clears_cache(client, cars, admin_headers, valid_car):
    client.get("/api/cars?brand=Audi")

    client.put(f"/api/cars/{cars[0]}", json=valid_car, headers=admin_headers)  # Audi A4 postane Seat Leon

    response = client.get("/api/cars?brand=Audi")
    assert not is_hit(response)
    assert [car["model"] for car in items(response)] == ["Q3"]


def test_delete_clears_cache(client, cars, admin_headers):
    client.get("/api/cars")

    client.delete(f"/api/cars/{cars[0]}", headers=admin_headers)

    response = client.get("/api/cars")
    assert not is_hit(response)
    assert response.get_json()["total"] == 9


def test_rejected_writes_keep_cache(client, cars, admin_headers, valid_car):
    client.get("/api/cars")

    client.post("/api/cars", json=valid_car)  # brez prijave: 401
    client.post("/api/cars", json={**valid_car, "year": 1800}, headers=admin_headers)  # neveljavno: 400

    assert is_hit(client.get("/api/cars"))


def items(response):
    return response.get_json()["items"]
