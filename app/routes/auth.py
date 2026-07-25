from flask import Blueprint, request, jsonify, session
from sqlalchemy.exc import IntegrityError

from app import db
from app.models import User
from app.routes import login_required, current_user_id

auth_bp = Blueprint("auth", __name__)

MAX_USERNAME_LENGTH = 80


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"success": False, "error": "JSON request body required"}), 400

    username = data.get("username", "")
    password = data.get("password", "")

    if not isinstance(username, str) or not isinstance(password, str):
        return jsonify({"success": False, "error": "Username and password must be strings"}), 400

    if not username or not password:
        return jsonify({"success": False, "error": "Username and password required"}), 400

    user = User.query.filter_by(username=username).first()
    if not user or not user.check_password(password):
        return jsonify({"success": False, "error": "Invalid credentials"}), 401

    session["user_id"] = user.id
    return jsonify({"success": True, "token": "session"})


@auth_bp.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"success": True})


@auth_bp.route("/profile", methods=["GET"])
@login_required
def get_profile():
    user = db.session.get(User, current_user_id())
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify(user.to_dict())


@auth_bp.route("/profile", methods=["PUT"])
@login_required
def update_profile():
    user = db.session.get(User, current_user_id())
    if not user:
        return jsonify({"error": "User not found"}), 404

    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "JSON request body required"}), 400

    if "username" in data:
        username = data["username"]
        if not isinstance(username, str) or not username.strip():
            return jsonify({"error": "Username must be a non-empty string"}), 400
        if len(username) > MAX_USERNAME_LENGTH:
            return jsonify({"error": f"Username must be at most {MAX_USERNAME_LENGTH} characters"}), 400
        user.username = username.strip()

    if "password" in data:
        password = data["password"]
        if not isinstance(password, str) or not password:
            return jsonify({"error": "Password must be a non-empty string"}), 400
        user.set_password(password)

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Username already taken"}), 409

    return jsonify(user.to_dict())
