"""
Obravnava napak: vsi odgovori z napako so JSON, nikoli HTML.

Oblika odgovora je povsod enaka:
    {"error": "Not Found", "message": "Avtomobil ne obstaja."}
"""
from flask import jsonify
from werkzeug.exceptions import HTTPException

from .extensions import jwt


def register_error_handlers(app):
    @app.errorhandler(HTTPException)
    def handle_http_error(error):
        return jsonify(error=error.name, message=error.description), error.code

    # Napake pri preverjanju JWT žetona (flask-jwt-extended jih sicer vrne v svoji obliki)
    @jwt.unauthorized_loader
    def handle_missing_token(reason):
        return jsonify(error="Unauthorized", message="Za dostop se je treba prijaviti."), 401

    @jwt.invalid_token_loader
    def handle_invalid_token(reason):
        return jsonify(error="Unauthorized", message="Žeton ni veljaven."), 401

    @jwt.expired_token_loader
    def handle_expired_token(jwt_header, jwt_payload):
        return jsonify(error="Unauthorized", message="Žeton je potekel. Prijavite se znova."), 401

