# Database Schema

## Engine

SQLite via Flask-SQLAlchemy 3.1.1.

- Production/dev: file at `instance/tasks.db` (created automatically)
- Tests: in-memory (`sqlite:///:memory:`)

Tables are created with `db.create_all()` at application startup — there is **no migration tool** (no Alembic). Schema changes require recreating the database or manual ALTERs.

## Tables

### `user`

Defined in `app/models.py` (`User`).

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PK, autoincrement | User ID |
| username | VARCHAR(80) | UNIQUE, NOT NULL | Login name |
| password_hash | VARCHAR(256) | NOT NULL | Werkzeug PBKDF2 hash (never plaintext) |

### `task`

Defined in `app/models.py` (`Task`).

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PK, autoincrement | Task ID |
| title | VARCHAR(200) | NOT NULL | Task title (trimmed, validated ≤ 200 chars at API layer) |
| description | TEXT | DEFAULT `""` | Optional free text |
| completed | BOOLEAN | DEFAULT `false` | Completion flag |
| user_id | INTEGER | FK → `user.id`, NOT NULL | Owner |

## Relationships

- **User 1 → N Task** via `task.user_id`.
- ORM: `Task.user` relationship with backref `User.tasks` (lazy-loaded).
- No cascade rules defined — deleting a user with tasks would violate the FK; user deletion is not exposed by the API.

## Indexes

Only implicit indexes:

- Primary keys (`user.id`, `task.id`)
- Unique constraint on `user.username`

`task.user_id` has **no explicit index**; acceptable at demo scale. <!-- TODO: add index if task volume grows -->

## Serialisation

Both models expose `to_dict()` used by the API layer:

- `User.to_dict()` → `{id, username}` — deliberately excludes `password_hash`
- `Task.to_dict()` → `{id, title, description, completed, user_id}`

## Seed Data

`_seed_default_user()` in `app/__init__.py` runs at startup (skipped in test mode) and creates `admin` / `password123` if absent. Test fixtures in `tests/conftest.py` seed the same user for the in-memory database.
