from flask import Blueprint, jsonify
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from ..extensions import db

bp = Blueprint("health", __name__)


@bp.get("/health")
def health():
    """GET /api/health: 200, če strežnik deluje in je baza dosegljiva, sicer 503."""
    try:
        db.session.execute(text("SELECT 1"))
    except SQLAlchemyError:
        return jsonify(status="error", database="unavailable"), 503
    return jsonify(status="ok", database="ok")
