def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.get_json()["status"] == "healthy"


def test_login_success(client):
    resp = client.post("/login", json={"username": "admin", "password": "password123"})
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["success"] is True
    assert data["token"] == "session"


def test_login_invalid_credentials(client):
    resp = client.post("/login", json={"username": "admin", "password": "wrong"})
    assert resp.status_code == 401
    assert resp.get_json()["success"] is False


def test_login_missing_fields(client):
    resp = client.post("/login", json={})
    assert resp.status_code == 400


def test_logout(client):
    client.post("/login", json={"username": "admin", "password": "password123"})
    resp = client.post("/logout")
    assert resp.status_code == 200
    assert resp.get_json()["success"] is True


def test_get_profile_authenticated(client):
    client.post("/login", json={"username": "admin", "password": "password123"})
    resp = client.get("/profile")
    assert resp.status_code == 200
    assert resp.get_json()["username"] == "admin"


def test_get_profile_unauthorized(client):
    resp = client.get("/profile")
    assert resp.status_code == 401


def test_update_profile(client):
    client.post("/login", json={"username": "admin", "password": "password123"})
    resp = client.put("/profile", json={"username": "admin2"})
    assert resp.status_code == 200
    assert resp.get_json()["username"] == "admin2"


def test_create_task(client):
    client.post("/login", json={"username": "admin", "password": "password123"})
    resp = client.post("/tasks", json={"title": "Test task", "description": "A task"})
    assert resp.status_code == 201
    data = resp.get_json()
    assert data["title"] == "Test task"
    assert data["description"] == "A task"
    assert data["completed"] is False


def test_create_task_missing_title(client):
    client.post("/login", json={"username": "admin", "password": "password123"})
    resp = client.post("/tasks", json={})
    assert resp.status_code == 400


def test_list_tasks(client):
    client.post("/login", json={"username": "admin", "password": "password123"})
    client.post("/tasks", json={"title": "Task 1"})
    client.post("/tasks", json={"title": "Task 2"})
    resp = client.get("/tasks")
    assert resp.status_code == 200
    assert len(resp.get_json()) == 2


def test_get_task(client):
    client.post("/login", json={"username": "admin", "password": "password123"})
    create = client.post("/tasks", json={"title": "My task"})
    task_id = create.get_json()["id"]
    resp = client.get(f"/tasks/{task_id}")
    assert resp.status_code == 200
    assert resp.get_json()["title"] == "My task"


def test_get_task_not_found(client):
    client.post("/login", json={"username": "admin", "password": "password123"})
    resp = client.get("/tasks/999")
    assert resp.status_code == 404


def test_update_task(client):
    client.post("/login", json={"username": "admin", "password": "password123"})
    create = client.post("/tasks", json={"title": "Original"})
    task_id = create.get_json()["id"]
    resp = client.put(f"/tasks/{task_id}", json={"title": "Updated", "completed": True})
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["title"] == "Updated"
    assert data["completed"] is True


def test_delete_task(client):
    client.post("/login", json={"username": "admin", "password": "password123"})
    create = client.post("/tasks", json={"title": "To delete"})
    task_id = create.get_json()["id"]
    resp = client.delete(f"/tasks/{task_id}")
    assert resp.status_code == 200
    resp = client.get("/tasks")
    assert len(resp.get_json()) == 0


def test_tasks_unauthorized(client):
    resp = client.get("/tasks")
    assert resp.status_code == 401
    resp = client.post("/tasks", json={"title": "x"})
    assert resp.status_code == 401
