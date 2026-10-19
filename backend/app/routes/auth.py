"""
Prijava in podatki o prijavljenem uporabniku.

Odjave na strežniku ni: JWT žeton nima stanja, zato se uporabnik odjavi tako,
da frontend žeton zbriše. Žeton sam poteče po JWT_ACCESS_TOKEN_EXPIRES.
"""
import flask_jwt_extended
from flask import Blueprint, abort, jsonify, request
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required

from ..extensions import db
from ..models import User

bp = Blueprint("auth", __name__)


@bp.post("/auth/login")
def login():
    """POST /api/auth/login: preveri uporabniško ime in geslo ter vrne JWT žeton."""
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        data = {}
    username = data.get("username")
    password = data.get("password")
    if not (isinstance(username, str) and isinstance(password, str) and username and password):
        abort(400, description="Vnesite uporabniško ime in geslo.")

    user = db.session.scalar(db.select(User).where(User.username == username))
    # Isto sporočilo za napačno ime in napačno geslo, da ne razkrijemo, kateri uporabniki obstajajo.
    if user is None or not user.check_password(password):
        abort(401, description="Napačno uporabniško ime ali geslo.")

    # Identiteta mora biti niz; is_admin vpišemo v žeton za @admin_required.
    token = create_access_token(identity=str(user.id), additional_claims={"is_admin": user.is_admin})
    return jsonify(access_token=token, user=user.to_dict())


@bp.get("/auth/me")
@jwt_required()
def me():
    """GET /api/auth/me: podatki o prijavljenem uporabniku (frontend ga uporabi za preverjanje žetona)."""
    user = db.session.get(User, int( get_jwt_identity()))
    if user is None:
        abort(401, description="Uporabnik ne obstaja več.")

    return jsonify(user.to_dict())
