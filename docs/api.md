# API Reference

This document is the authoritative specification for all REST APIs.

Every Coding Agent and Testing Agent should refer to this file before implementing or testing endpoints.

---

## Authentication

POST /login

Description

Authenticate a user.

Request

```json
{
    "username": "admin",
    "password": "password123"
}
```

Response

```json
{
    "success": true,
    "token": "session"
}
```

---

POST /logout

---

## User

GET /profile

PUT /profile

---

## Tasks

GET /tasks

GET /tasks/{id}

POST /tasks

PUT /tasks/{id}

DELETE /tasks/{id}

---

## Health

GET /health
