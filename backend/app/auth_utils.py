from functools import wraps

from flask import abort
from flask_jwt_extended import get_jwt, verify_jwt_in_request


def admin_required(fn):
    """Pot dovoli samo prijavljenemu uporabniku z administratorskimi pravicami."""

    @wraps(fn)
    def wrapper(*args, **kwargs):
        # Vrže 401, če žetona ni ali ni veljaven (obravnava ga errors.py)
        verify_jwt_in_request()
        if not get_jwt().get("is_admin"):
            abort(403, description="Za to dejanje so potrebne administratorske pravice.")
        return fn(*args, **kwargs)

    return wrapper
