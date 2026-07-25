from flask import Blueprint, request, jsonify

from app import db
from app.models import Task
from app.routes import login_required, current_user_id

tasks_bp = Blueprint("tasks", __name__)

MAX_TITLE_LENGTH = 200


def _validate_title(title):
    """Return an error message if the title is invalid, otherwise None."""
    if not isinstance(title, str) or not title.strip():
        return "Title must be a non-empty string"
    if len(title) > MAX_TITLE_LENGTH:
        return f"Title must be at most {MAX_TITLE_LENGTH} characters"
    return None


def _get_owned_task(task_id):
    task = db.session.get(Task, task_id)
    if not task or task.user_id != current_user_id():
        return None
    return task


@tasks_bp.route("/tasks", methods=["GET"])
@login_required
def list_tasks():
    tasks = Task.query.filter_by(user_id=current_user_id()).all()
    return jsonify([t.to_dict() for t in tasks])


@tasks_bp.route("/tasks/<int:task_id>", methods=["GET"])
@login_required
def get_task(task_id):
    task = _get_owned_task(task_id)
    if not task:
        return jsonify({"error": "Task not found"}), 404
    return jsonify(task.to_dict())


@tasks_bp.route("/tasks", methods=["POST"])
@login_required
def create_task():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "JSON request body required"}), 400

    error = _validate_title(data.get("title"))
    if error:
        return jsonify({"error": error}), 400

    description = data.get("description", "")
    if not isinstance(description, str):
        return jsonify({"error": "Description must be a string"}), 400

    task = Task(
        title=data["title"].strip(),
        description=description,
        user_id=current_user_id(),
    )
    db.session.add(task)
    db.session.commit()
    return jsonify(task.to_dict()), 201


@tasks_bp.route("/tasks/<int:task_id>", methods=["PUT"])
@login_required
def update_task(task_id):
    task = _get_owned_task(task_id)
    if not task:
        return jsonify({"error": "Task not found"}), 404

    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "JSON request body required"}), 400

    if "title" in data:
        error = _validate_title(data["title"])
        if error:
            return jsonify({"error": error}), 400
        task.title = data["title"].strip()

    if "description" in data:
        if not isinstance(data["description"], str):
            return jsonify({"error": "Description must be a string"}), 400
        task.description = data["description"]

    if "completed" in data:
        if not isinstance(data["completed"], bool):
            return jsonify({"error": "Completed must be a boolean"}), 400
        task.completed = data["completed"]

    db.session.commit()
    return jsonify(task.to_dict())


@tasks_bp.route("/tasks/<int:task_id>", methods=["DELETE"])
@login_required
def delete_task(task_id):
    task = _get_owned_task(task_id)
    if not task:
        return jsonify({"error": "Task not found"}), 404
    db.session.delete(task)
    db.session.commit()
    return jsonify({"success": True})
