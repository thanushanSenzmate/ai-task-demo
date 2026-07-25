# Architecture

## Overview

AI Task Manager Demo is a session-authenticated task management REST API with a single-page web UI, built with Flask using the application-factory pattern. Three blueprints (`auth`, `tasks`, `health`) expose JSON endpoints; a Bootstrap-based SPA served at `/` consumes them. Data is stored in SQLite via Flask-SQLAlchemy. The app ships as a Docker image running gunicorn as a non-root user, with CI on GitHub Actions.

## Stack

| Layer | Technology | Version |
|-------|-----------|---------|
| Language | Python | 3.11 |
| Framework | Flask | 3.1.3 |
| ORM | Flask-SQLAlchemy | 3.1.1 |
| WSGI utilities | Werkzeug | 3.1.6 |
| Database | SQLite | (file: `instance/tasks.db`) |
| Frontend | Vanilla JS + Bootstrap (CDN) | 5.3.3 |
| WSGI server | gunicorn | 23.0.0 |
| Testing | pytest / pytest-cov | 9.0.3 / 6.0.0 |
| Security scanning | bandit, pip-audit, gitleaks | 1.8.3 / 2.8.0 / action v2 |
| Container | Docker (python:3.11-slim) | — |
| CI/CD | GitHub Actions | — |

## Directory Structure

```
workshop/
├── wsgi.py                  # Entry point; creates app, dev server if run directly
├── requirements.txt         # Pinned dependencies (security-audited)
├── Dockerfile               # python:3.11-slim, non-root user, HEALTHCHECK
├── .dockerignore
├── .github/
│   └── workflows/ci.yml     # test + security + docker build jobs
├── app/
│   ├── __init__.py          # App factory, DB init, JSON error handlers, seed user
│   ├── models.py            # User and Task SQLAlchemy models
│   ├── templates/
│   │   └── index.html       # Single-page UI (login + task dashboard)
│   └── routes/
│       ├── __init__.py      # login_required decorator, current_user_id helper
│       ├── auth.py          # /login /logout /profile
│       ├── tasks.py         # /tasks CRUD
│       └── health.py        # /health
├── tests/
│   ├── conftest.py          # App/client fixtures (in-memory SQLite, seeded admin)
│   ├── test_api.py          # Endpoint happy-path and auth tests
│   └── test_validation.py   # Input-validation and error-handling regression tests
└── docs/                    # Project documentation (this folder)
```

## Key Flows

### User Authentication

1. Browser loads `/` → `index.html`; page calls `GET /profile` to restore an existing session, otherwise shows the login form.
2. `POST /login` with JSON `{username, password}` → `app/routes/auth.py:login`.
3. Input validated (JSON body present, both fields non-empty strings).
4. `User` looked up by username; password checked against `password_hash` (Werkzeug PBKDF2 via `check_password_hash`).
5. On success `session["user_id"]` is set in a signed cookie (`SECRET_KEY` from env, falls back to dev key).
6. Subsequent requests pass through the `login_required` decorator (`app/routes/__init__.py`) which rejects missing sessions with JSON 401.
7. `POST /logout` clears the session cookie.

### Task CRUD

1. All `/tasks*` routes require a session (`login_required`).
2. Ownership is enforced on single-task routes via `_get_owned_task` — a task belonging to another user returns 404 (not 403, avoiding existence leaks).
3. Writes validate types and lengths (title ≤ 200 chars, `completed` must be boolean) before committing.
4. Responses serialise through `Task.to_dict()`.

### Error Handling

- Malformed/missing JSON bodies → JSON 400 (parsed with `get_json(silent=True)`).
- Unknown routes / wrong methods / server errors → JSON 404 / 405 / 500 via app-level error handlers in `app/__init__.py`.
- Duplicate username on profile update → caught `IntegrityError`, rolled back, JSON 409.

## Configuration

| Setting | Source | Default |
|---------|--------|---------|
| `SECRET_KEY` | `SECRET_KEY` env var | `dev-secret-key` (dev only) |
| `SQLALCHEMY_DATABASE_URI` | hardcoded | `sqlite:///tasks.db` (in `instance/`) |
| `FLASK_DEBUG` | env var (`wsgi.py` direct run) | `0` |
| Test mode | `create_app(testing=True)` | in-memory SQLite |

A default user `admin` / `password123` is seeded at startup (skipped in test mode; tests seed their own).

## Deployment

```bash
# Local development
pip install -r requirements.txt
python wsgi.py                        # http://localhost:5000

# Docker
docker build -t task-demo .
docker run -d -p 5000:5000 -e SECRET_KEY=<strong-random-value> task-demo
```

The container runs gunicorn as non-root user `appuser` and reports health via a `HEALTHCHECK` hitting `GET /health` every 30 s.

### CI Pipeline (`.github/workflows/ci.yml`)

Three parallel jobs on every push/PR:

1. **test** — `pytest --cov=app`
2. **security** — gitleaks (official action), `bandit -r app/`, `pip-audit --requirement requirements.txt`
3. **docker** — `docker build`

## Known Limitations

- Flask signed-cookie sessions cannot be invalidated server-side; a captured pre-logout cookie replays successfully (tracked in GitHub issue #15).
- SQLite is single-file storage inside the container — data is lost when the container is removed unless a volume is mounted.
