FROM debian:trixie-slim AS base

# Apache, mod_wsgi (preveden za sistemski Python 3.13) in venv
RUN apt-get update && apt-get install -y --no-install-recommends \
        apache2 libapache2-mod-wsgi-py3 python3-venv \
    && rm -rf /var/lib/apt/lists/* \
    && ln -sf /dev/stdout /var/log/apache2/access.log \
    && ln -sf /dev/stderr /var/log/apache2/error.log

WORKDIR /opt/backend
ENV PATH="/opt/venv/bin:$PATH" \
    FLASK_APP=app

# Odvisnosti posebej, da se ob spremembi kode ne nameščajo znova
COPY requirements.txt .
RUN python3 -m venv /opt/venv \
    && pip install --no-cache-dir -r requirements.txt

COPY . .
COPY apache.conf /etc/apache2/sites-available/000-default.conf

# Slika za teste (docker-compose.test.yml): osnova in pytest
FROM base AS test
COPY requirements-dev.txt .
RUN pip install --no-cache-dir -r requirements-dev.txt
CMD ["pytest"]

# Produkcijska slika. Je zadnja stopnja, zato jo zgradi navaden `docker compose build`.
FROM base AS production
EXPOSE 80
ENTRYPOINT ["sh", "entrypoint.sh"]
CMD ["apache2ctl", "-D", "FOREGROUND"]
