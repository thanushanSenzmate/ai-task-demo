# API Reference

This document is the authoritative specification for all REST APIs.

Every Coding Agent and Testing Agent should refer to this file before implementing or testing endpoints.

---

## Base URL

Relative — the API and UI are served from the same origin (e.g. `http://localhost:5000`).

## Authentication

Session cookie. `POST /login` sets a signed session cookie; subsequent requests must include it. Protected endpoints return `401 {"error": "Unauthorized"}` without a valid session.

Default seeded credentials: `admin` / `password123`.

---

## Endpoints

### Authentication

#### `POST /login`

Authenticate a user and start a session.

- **Auth**: None
- **Body**: `{"username": "admin", "password": "password123"}`
- **Response** (200): `{"success": true, "token": "session"}`
- **Errors**:
  - 400 — missing/malformed JSON body, missing fields, or non-string values: `{"success": false, "error": "..."}`
  - 401 — invalid credentials: `{"success": false, "error": "Invalid credentials"}`

#### `POST /logout`

Clear the current session.

- **Auth**: None (idempotent)
- **Response** (200): `{"success": true}`

---

### User

#### `GET /profile`

Return the logged-in user.

- **Auth**: Required
- **Response** (200): `{"id": 1, "username": "admin"}`
- **Errors**: 401

#### `PUT /profile`

Update username and/or password.

- **Auth**: Required
- **Body** (any subset): `{"username": "newname", "password": "newpass"}`
- **Validation**:
  - `username` — non-empty string, ≤ 80 chars, trimmed, must be unique
  - `password` — non-empty string
- **Response** (200): updated profile `{"id": 1, "username": "newname"}`
- **Errors**: 400 (validation), 401, 409 (`{"error": "Username already taken"}`)

---

### Tasks

All task endpoints require auth and operate only on the caller's own tasks. Accessing another user's task returns 404.

**Task object**: `{"id": 1, "title": "...", "description": "...", "completed": false, "user_id": 1}`

#### `GET /tasks`

- **Response** (200): array of Task objects (empty array if none)

#### `GET /tasks/{id}`

- **Response** (200): Task object
- **Errors**: 401, 404 (`{"error": "Task not found"}`)

#### `POST /tasks`

- **Body**: `{"title": "Buy milk", "description": "optional"}`
- **Validation**: `title` non-empty string ≤ 200 chars (trimmed); `description` must be a string if present
- **Response** (201): created Task object
- **Errors**: 400, 401

#### `PUT /tasks/{id}`

- **Body** (any subset): `{"title": "...", "description": "...", "completed": true}`
- **Validation**: same as create; `completed` must be a boolean
- **Response** (200): updated Task object
- **Errors**: 400, 401, 404

#### `DELETE /tasks/{id}`

- **Response** (200): `{"success": true}`
- **Errors**: 401, 404

---

### Health

#### `GET /health`

- **Auth**: None
- **Response** (200): `{"status": "healthy"}`

Used by the Docker `HEALTHCHECK` and monitoring.

---

### UI

#### `GET /`

Serves the single-page web interface (`app/templates/index.html`).

---

## Error Format

All API errors are JSON:

| Status | Body |
|--------|------|
| 400 | `{"error": "<validation message>"}` (login also includes `"success": false`) |
| 401 | `{"error": "Unauthorized"}` |
| 404 | `{"error": "Not found"}` / `{"error": "Task not found"}` |
| 405 | `{"error": "Method not allowed"}` |
| 409 | `{"error": "Username already taken"}` |
| 500 | `{"error": "Internal server error"}` |

## Rate Limits

None.
