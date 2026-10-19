# Avtomobili

Spletna aplikacija za pregled in upravljanje avtomobilov.

- **Backend:** Python, Flask, SQLAlchemy, Flask-Migrate, Flask-JWT-Extended, Flask-Caching, MariaDB 12.3, Memcached, Apache (mod_wsgi)
- **Frontend:** React 19, TypeScript, Vite, Bootstrap, TanStack Query, React Router, i18next (slovenščina in angleščina), Apache
- **Zagon:** Docker Compose

## Zagon

1. Pripravi nastavitve:

   ```bash
   cp .env.example .env
   ```

   (v PowerShellu: `Copy-Item .env.example .env`)

2. (Neobvezno, za produkcijo) V `.env` zamenjaj `DB_PASSWORD`, `DB_ROOT_PASSWORD`, `JWT_SECRET_KEY` in `ADMIN_PASSWORD`.
   Ključ za JWT ustvariš z `python -c "import secrets; print(secrets.token_hex(32))"`.

3. Zaženi:

   ```bash
   docker compose up -d --build
   ```

4. Odpri:
   - aplikacija: http://localhost
   - API: http://localhost:8000/api/health

Ob zagonu backend sam izvede migracije, naloži vzorčne avtomobile (če je `SEED_SAMPLE_DATA=true`) in ustvari administratorja (če sta nastavljena `ADMIN_USERNAME` in `ADMIN_PASSWORD`). Prijava je na http://localhost/login. S privzetimi vrednostmi iz `.env.example` se prijaviš kot `admin` z geslom `change-me`.

### Razvojni način

```bash
docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d
```

Backend teče z `flask run --debug` nad priklopljeno mapo `backend/`, frontend pa kot Vite razvojni strežnik. Spremembe kode se vidijo takoj, brez ponovne gradnje.

## Nastavitve (`.env`)

| Spremenljivka | Pomen |
| --- | --- |
| `DB_DATABASE`, `DB_USERNAME`, `DB_PASSWORD`, `DB_ROOT_PASSWORD` | Baza in uporabnika MariaDB |
| `JWT_SECRET_KEY` | Skrivni ključ za podpis žetonov |
| `FRONTEND_URL`, `FRONTEND_PORT` | Naslov in vrata, na katerih odpreš aplikacijo |
| `BACKEND_URL`, `BACKEND_PORT` | Naslov in vrata API-ja |
| `ADMIN_USERNAME`, `ADMIN_PASSWORD` | Neobvezno: administrator, ki se ustvari ob zagonu |
| `SEED_SAMPLE_DATA` | `true` naloži vzorčne avtomobile (samo če je tabela prazna) |

`FRONTEND_URL` mora biti natančno naslov, na katerem odpreš aplikacijo, sicer brskalnik zavrne klice API-ja (CORS). Če spremeniš vrata, popravi tudi naslov. `BACKEND_URL` se vgradi v frontend ob gradnji, zato po spremembi zaženi `docker compose up -d --build`.

## Uporabni ukazi

```bash
docker compose exec backend flask create-admin   # nov administrator (vpraša po imenu in geslu)
docker compose exec backend flask seed           # vzorčni avtomobili
docker compose logs -f backend                   # dnevnik backenda
docker compose down                              # ustavi
docker compose down -v                           # ustavi in izbriše bazo
```

## Testi

Testi backenda (pytest) tečejo v Dockerju proti pravi MariaDB 12.3, ki hrani podatke samo v pomnilniku. Shema se ustvari z istimi migracijami kot v produkciji, pred vsakim testom se tabele izpraznijo. Ločen sklad (`vozni-park-test`) ne posega v tvojo bazo.

```bash
docker compose -f docker-compose.test.yml run --rm --build tests
docker compose -f docker-compose.test.yml down
```

## API

Vse poti imajo predpono `/api`. Zaščiteni klici zahtevajo glavo `Authorization: Bearer <access_token>`.

| Metoda | Pot | Dostop | Opis |
| --- | --- | --- | --- |
| GET | `/health` | javno | 200, če strežnik deluje in je baza dosegljiva, sicer 503 |
| POST | `/auth/login` | javno | `{"username", "password"}` → `{"access_token", "user"}` |
| GET | `/auth/me` | prijavljen | podatki o prijavljenem uporabniku |
| GET | `/cars` | javno | seznam avtomobilov |
| GET | `/cars/<id>` | javno | en avtomobil |
| POST | `/cars` | administrator | doda avtomobil (201) |
| PUT | `/cars/<id>` | administrator | zamenja podatke avtomobila |
| DELETE | `/cars/<id>` | administrator | izbriše avtomobil (204) |
| GET | `/brands` | javno | abecedni seznam znamk |

Parametri za `GET /cars` (vsi neobvezni):

| Parameter | Pomen |
| --- | --- |
| `brand` | točno ujemanje znamke (ne razlikuje velikih in malih črk ter šumnikov) |
| `price_min`, `price_max` | meji cene, vključno |
| `sort` | `id` (privzeto), `brand`, `year` ali `price` |
| `order` | `asc` (privzeto) ali `desc` |
| `page`, `per_page` | stran (privzeto 1) in velikost strani (privzeto 10, največ 100) |

```bash
curl "http://localhost:8000/api/cars?brand=Audi&price_max=30000&sort=price&order=desc"
```

Odgovor:

```json
{
  "items": [{"id": 1, "brand": "Audi", "model": "A4", "year": 2019, "price": 21900.0,
             "fuel_type": "diesel", "doors": 4, "description": "..."}],
  "page": 1, "per_page": 10, "total": 2, "pages": 1
}
```

Napake so vedno JSON z `error` (ime napake) in `message` (opis), npr. `{"error": "Not Found", "message": "Avtomobil ne obstaja."}`. Pri 400 zaradi neveljavnih podatkov je dodan še `errors` s sporočili po poljih: `{"error": "Bad Request", "message": "Neveljavni podatki.", "errors": {"year": "Letnik mora biti celo število."}}`.
## Zgradba

```
backend/    Flask API (app/), migracije (migrations/), Dockerfile, Apache
frontend/   React aplikacija (src/), Dockerfile, Apache
docker-compose.yml        produkcija
docker-compose.dev.yml    dopolnilo za razvoj
docker-compose.test.yml   testi
```
