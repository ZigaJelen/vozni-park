from flask import Flask

from .commands import register_commands
from .config import Config
from .errors import register_error_handlers
from .extensions import cache, cors, db, jwt, migrate
from .routes import register_blueprints


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    cache.init_app(app)
    # CORS velja samo za API in samo za naslov frontenda
    cors.init_app(app, resources={r"/api/*": {"origins": app.config["CORS_ORIGINS"]}})

    register_error_handlers(app)
    register_blueprints(app)
    register_commands(app)

    # Modele uvozimo, da jih Flask-Migrate zazna pri ustvarjanju migracij
    from . import models  # noqa: F401

    return app
