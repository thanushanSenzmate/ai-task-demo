# Docker Guide

This document is the source of truth for building and running the application.

Agents should follow this document when generating Docker artifacts.

---

## Build

```bash
docker build -t task-demo .
```

---

## Run

```bash
docker run -p 5000:5000 task-demo
```

---

## Stop

```bash
docker stop <container>
```

---

## Logs

```bash
docker logs <container>
```

---

## Acceptance

The application should be reachable at

http://localhost:5000
