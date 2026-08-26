# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

CallStats is a full-stack application for managing emergency service (fire department) calls, members, exercises, and qualifications. It consists of a Vue 3 frontend and a Python FastAPI backend with PostgreSQL.

## Development Commands

### Frontend (in `frontend/`)
```bash
npm install        # Install dependencies
npm run dev        # Vite dev server
npm run build      # TypeScript check + production build
npm run preview    # Preview production build
```

### Backend
```bash
pipenv sync        # Install Python dependencies
```

### Docker (from project root)
```bash
docker compose up  # Starts PostgreSQL + app
```

### Tests
```bash
# Via Docker Compose (spins up DB):
docker compose run app python -m pytest
```
Test files are in `backend/services/test_calls.py` and `backend/services/test_members.py`.

## Architecture

### Frontend (`frontend/`)
- **Framework:** Vue 3 with Composition API (`<script setup>`), TypeScript, Vite, TailwindCSS 4
- **Layers:**
  - `src/views/` - Page components (lazy-loaded via router)
  - `src/components/` - Reusable UI; base components in `components/base/`
  - `src/api/` - Axios-based service modules per feature
  - `src/interfaces/` - TypeScript type definitions
  - `src/scripts/` - Utility functions (datetime, math)
  - `src/events/` - EventBus for global error handling
- **API base URL:** Resolved from `window.__BASE_URL__` > env var > fallback `/api`
- **Routing:** Root redirects to `/calls`; main routes: Calls, Exercise, Youth, Members

### Backend (`backend/`)
- **Framework:** FastAPI (sync handlers), SQLModel ORM, PostgreSQL via psycopg
- **Layers:**
  - `web/` - App initialization and router composition (all routes under `/api/`)
  - `services/` - Business logic and endpoint handlers
  - `entities/` - SQLModel models (DB tables + Pydantic schemas)
  - `data/` - DB engine, session management, custom types
  - `services/extra/` - Cross-cutting: errors, pagination
- **Key entities:** Member, Call, Subject, Exercise, YouthExercise, Qualification (with junction tables for many-to-many relationships)

### Key Conventions
- **Date/Time:** Unix timestamps in the API, converted by custom `EpochDate` type in backend
- **Pagination:** Generic `Page[T]` model with `page`, `size`, `pages`, `entries` fields
- **Error handling:** Custom exceptions (`NotFoundError` 404, `ExistsError` 409, `IdChangeError` 400) in backend; EventBus error emission in frontend
- **Response models:** Services use `.convert()` static methods to transform ORM objects to response schemas
- **DB sessions:** Injected via FastAPI's `Depends(get_session)`

## Environment

- **Dev environment:** Nix shell (shell.nix) provides Node.js 24 + Python 3.14; direnv auto-loads
- **Backend config:** `.env` with DB_USERNAME, DB_PASSWORD, DB_DATABASE, DB_SCHEMA, DB_PORT
- **Frontend config:** `.env` with VITE_BASE_URL
- **TypeScript:** Strict mode with noUnusedLocals and noUnusedParameters enabled
