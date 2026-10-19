"""
Nastavitve aplikacije.

Vse vrednosti se preberejo iz spremenljivk okolja (v Dockerju jih nastavi
docker-compose iz datoteke .env), zato v kodi ni gesel ali skrivnosti.
"""
import os
from datetime import timedelta

from sqlalchemy.engine import URL

class Config:
    SQLALCHEMY_DATABASE_URI = URL.create(
        "mysql+pymysql",
        username=os.environ.get("DB_USERNAME"),
        password=os.environ.get("DB_PASSWORD"),
        host=os.environ.get("DB_HOST", "localhost"),
        port=int(os.environ.get("DB_PORT", 3306)),
        database=os.environ.get("DB_DATABASE"),
        query={"charset": "utf8mb4"},
    )
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        # MySQL/MariaDB zapre nedejavne povezave, zato jih obnovimo prej.
        "pool_recycle": 280,
    }

    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)

    # Predpomnjenje: Memcached, skupen obema procesoma mod_wsgi
    CACHE_TYPE = "MemcachedCache"
    CACHE_MEMCACHED_SERVERS = [os.environ.get("MEMCACHED_SERVER", "localhost:11211")]
    CACHE_KEY_PREFIX = "avtomobili:"
    CACHE_DEFAULT_TIMEOUT = 60  # sekunde

    # CORS: naslov frontenda, ki sme klicati API
    CORS_ORIGINS = os.environ.get("CORS_ORIGINS", "http://localhost:80")
