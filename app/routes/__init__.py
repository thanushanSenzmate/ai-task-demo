from functools import wraps

from flask import jsonify, session


def login_required(f):
    """Reject the request with 401 JSON if no user is logged in."""

    @wraps(f)
    def wrapper(*args, **kwargs):
        if not session.get("user_id"):
            return jsonify({"error": "Unauthorized"}), 401
        return f(*args, **kwargs)

    return wrapper


def current_user_id():
    return session.get("user_id")
