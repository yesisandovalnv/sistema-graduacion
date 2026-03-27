---
name: sistema-graduacion-instructions
description: "Workspace instructions for sistema-graduacion project. Restricts Docker operations to explicit requests only."
---

# Sistema de Graduación - Workspace Guidelines

## 🚫 Docker Policy

**CRITICAL:** Only modify Docker configuration when explicitly requested by the user.

- ❌ Do NOT touch `Dockerfile.backend`, `Dockerfile.frontend`, `docker-compose.yml`, or `entrypoint.sh` unless the user explicitly asks
- ❌ Do NOT run `docker compose build`, `docker compose up`, or Docker commands without user instruction
- ✅ DO verify Docker status with `docker compose ps` or `docker compose logs` only when debugging real issues
- ✅ DO ask the user before making any Docker changes

## 📋 Safe Default Operations

Unless otherwise instructed, prioritize these safer operations:

1. **Code changes** in Python/JavaScript files → Always safe
2. **Configuration updates** in settings files → Generally safe
3. **Read-only diagnostics** (logs, status, analysis) → Always safe
4. **Database operations** (migrations, fixtures) → Only when explicitly requested

## 🔄 Before Docker Changes

If you suspect a Docker issue:

1. Check the logs: `docker compose logs backend --tail 30`
2. Report findings to the user
3. **Wait for explicit permission** before rebuilding or modifying

## 📌 Current System Status

- Backend: Django + Gunicorn (working)
- Frontend: React + Nginx (port 80)
- Database: PostgreSQL (port 5432)
- Admin credentials: `admin / password`

---

**Remember:** Docker changes are only for the user to decide. Your role is to inform, not to intervene.
