from flask import Blueprint, request, jsonify, session

from app import db
from app.models import Task

tasks_bp = Blueprint("tasks", __name__)


def _require_auth():
    user_id = session.get("user_id")
    if not user_id:
        return None
    return user_id


@tasks_bp.route("/tasks", methods=["GET"])
def list_tasks():
    user_id = _require_auth()
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401
    tasks = Task.query.filter_by(user_id=user_id).all()
    return jsonify([t.to_dict() for t in tasks])


@tasks_bp.route("/tasks/<int:task_id>", methods=["GET"])
def get_task(task_id):
    user_id = _require_auth()
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401
    task = db.session.get(Task, task_id)
    if not task or task.user_id != user_id:
        return jsonify({"error": "Task not found"}), 404
    return jsonify(task.to_dict())


@tasks_bp.route("/tasks", methods=["POST"])
def create_task():
    user_id = _require_auth()
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401
    data = request.get_json()
    if not data or not data.get("title"):
        return jsonify({"error": "Title is required"}), 400
    task = Task(
        title=data["title"],
        description=data.get("description", ""),
        user_id=user_id,
    )
    db.session.add(task)
    db.session.commit()
    return jsonify(task.to_dict()), 201


@tasks_bp.route("/tasks/<int:task_id>", methods=["PUT"])
def update_task(task_id):
    user_id = _require_auth()
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401
    task = db.session.get(Task, task_id)
    if not task or task.user_id != user_id:
        return jsonify({"error": "Task not found"}), 404
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body required"}), 400
    if "title" in data:
        task.title = data["title"]
    if "description" in data:
        task.description = data["description"]
    if "completed" in data:
        task.completed = data["completed"]
    db.session.commit()
    return jsonify(task.to_dict())


@tasks_bp.route("/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    user_id = _require_auth()
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401
    task = db.session.get(Task, task_id)
    if not task or task.user_id != user_id:
        return jsonify({"error": "Task not found"}), 404
    db.session.delete(task)
    db.session.commit()
    return jsonify({"success": True})
