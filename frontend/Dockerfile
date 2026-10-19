# 1. stopnja: gradnja aplikacije (Node). V končno sliko ne pride.
FROM node:22-alpine AS build
WORKDIR /app

# Odvisnosti posebej, da se ob spremembi kode ne nameščajo znova
COPY package.json package-lock.json ./
RUN npm ci

COPY . .
# Naslov API-ja se vgradi v JavaScript ob gradnji
ARG VITE_API_URL=http://localhost:8000/api
ENV VITE_API_URL=$VITE_API_URL
RUN npm run build

# 2. stopnja: Apache streže samo statične datoteke iz dist/
FROM debian:trixie-slim
RUN apt-get update && apt-get install -y --no-install-recommends apache2 \
    && rm -rf /var/lib/apt/lists/* \
    && ln -sf /dev/stdout /var/log/apache2/access.log \
    && ln -sf /dev/stderr /var/log/apache2/error.log

# Odstrani Debianovo privzeto stran in kopiraj zgrajeno aplikacijo
RUN rm -rf /var/www/html/*
COPY --from=build /app/dist /var/www/html
COPY apache.conf /etc/apache2/sites-available/000-default.conf

EXPOSE 80
CMD ["apache2ctl", "-D", "FOREGROUND"]
