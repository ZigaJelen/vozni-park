"""
Registracija vseh blueprintov pod skupno predpono /api.
"""
from . import auth, cars, health

BLUEPRINTS = (health.bp, auth.bp, cars.bp)


def register_blueprints(app):
    for bp in BLUEPRINTS:
        app.register_blueprint(bp, url_prefix="/api")
