#!/bin/sh
# Zagonski skript backenda: pripravi bazo, nato zažene glavni ukaz kontejnerja
# (Apache v produkciji, `flask run` v razvoju).
set -e

echo "==> Migracije baze (flask db upgrade)"
flask db upgrade

if [ "${SEED_SAMPLE_DATA:-true}" = "true" ]; then
    echo "==> Vzorčni avtomobili (flask seed)"
    flask seed
fi

if [ -n "$ADMIN_USERNAME" ] && [ -n "$ADMIN_PASSWORD" ]; then
    echo "==> Administrator '$ADMIN_USERNAME' (flask create-admin)"
    # Če uporabnik že obstaja, ukaz javi napako; zagona zaradi tega ne ustavimo.
    flask create-admin --username "$ADMIN_USERNAME" --password "$ADMIN_PASSWORD" || true
fi

echo "==> Zagon aplikacije"
exec "$@"
