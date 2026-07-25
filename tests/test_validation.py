"""Regression tests for code-review fixes."""


def _login(client, username="admin", password="password123"):
    return client.post("/login", json={"username": username, "password": password})


def test_login_without_json_content_type_returns_json_400(client):
    resp = client.post("/login", data="not json")
    assert resp.status_code == 400
    assert resp.get_json()["success"] is False


def test_login_non_string_credentials(client):
    resp = client.post("/login", json={"username": 123, "password": ["x"]})
    assert resp.status_code == 400


def test_unknown_route_returns_json_404(client):
    resp = client.get("/nonexistent")
    assert resp.status_code == 404
    assert resp.get_json()["error"] == "Not found"


def test_wrong_method_returns_json_405(client):
    resp = client.get("/login")
    assert resp.status_code == 405
    assert resp.get_json()["error"] == "Method not allowed"


def test_update_profile_duplicate_username_returns_409(client, app):
    from app import db
    from app.models import User

    with app.app_context():
        other = User(username="other")
        other.set_password("pass")
        db.session.add(other)
        db.session.commit()

    _login(client)
    resp = client.put("/profile", json={"username": "other"})
    assert resp.status_code == 409
    assert "taken" in resp.get_json()["error"]


def test_update_profile_empty_username_rejected(client):
    _login(client)
    resp = client.put("/profile", json={"username": "  "})
    assert resp.status_code == 400


def test_update_profile_empty_password_rejected(client):
    _login(client)
    resp = client.put("/profile", json={"password": ""})
    assert resp.status_code == 400


def test_update_profile_username_too_long_rejected(client):
    _login(client)
    resp = client.put("/profile", json={"username": "x" * 81})
    assert resp.status_code == 400


def test_create_task_title_too_long_rejected(client):
    _login(client)
    resp = client.post("/tasks", json={"title": "x" * 201})
    assert resp.status_code == 400


def test_create_task_non_string_title_rejected(client):
    _login(client)
    resp = client.post("/tasks", json={"title": 42})
    assert resp.status_code == 400


def test_create_task_whitespace_title_rejected(client):
    _login(client)
    resp = client.post("/tasks", json={"title": "   "})
    assert resp.status_code == 400


def test_create_task_non_string_description_rejected(client):
    _login(client)
    resp = client.post("/tasks", json={"title": "ok", "description": 99})
    assert resp.status_code == 400


def test_update_task_non_boolean_completed_rejected(client):
    _login(client)
    task_id = client.post("/tasks", json={"title": "t"}).get_json()["id"]
    resp = client.put(f"/tasks/{task_id}", json={"completed": "yes"})
    assert resp.status_code == 400


def test_task_title_is_trimmed(client):
    _login(client)
    resp = client.post("/tasks", json={"title": "  padded  "})
    assert resp.get_json()["title"] == "padded"


def test_index_page_served(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert b"AI Task Manager" in resp.data


def test_task_isolation_between_users(client, app):
    from app import db
    from app.models import User

    with app.app_context():
        other = User(username="bob")
        other.set_password("bobpass")
        db.session.add(other)
        db.session.commit()

    _login(client)
    task_id = client.post("/tasks", json={"title": "admin task"}).get_json()["id"]
    client.post("/logout")

    _login(client, "bob", "bobpass")
    resp = client.get(f"/tasks/{task_id}")
    assert resp.status_code == 404
    resp = client.delete(f"/tasks/{task_id}")
    assert resp.status_code == 404
