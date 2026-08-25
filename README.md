# CallStats

A small web app I wrote to keep track of what our fire department actually does over a year:
calls, exercises, youth exercises, members and their qualifications — and some statistics on top
of it, because the yearly report was getting annoying to put together by hand.

Nothing fancy: a Vue frontend, a FastAPI backend, PostgreSQL underneath. It runs as a single
Docker container plus a database.

## What's in it

- **Calls** — when the alarm went off, how long it took, which keywords (Stichwörter) applied,
  who was there, whether it was aborted, and a free-text note.
- **Keywords** — the list of call keywords, grouped (fire, technical help, ...).
- **Exercises and youth exercises** — date, topic, participants, instructors.
- **Members** — the roster, entry and retirement dates, qualifications, plus a per-member
  activity view showing which calls they attended.
- **Statistics** — charts for calls per day (rolling window), calls per keyword group, monthly
  breakdowns, a year summary with crew hours, and per-member participation shares.

There are two roles. `admin` can see and edit everything; `member` only gets the call list,
the member detail pages and the statistics. It's a club app, not a bank — the roles exist to
keep people from accidentally deleting the roster, not to defend against anyone.

## Running it

You need Docker. From the project root:

```bash
docker compose up
```

That builds the image (frontend gets compiled and is served by the backend), starts PostgreSQL
and puts the app on <http://localhost:8888>.

Log in with `admin` / `admin` or `member` / `member`. **Change those before you put this
anywhere other than your own laptop**, along with the token secret:

```bash
ADMIN_PASSWORD=... MEMBER_PASSWORD=... TOKEN_SECRET=... docker compose up -d
```

### Environment variables

| Variable | Default | What it does |
| --- | --- | --- |
| `DB_HOST`, `DB_PORT` | `database`, `5432` | Where PostgreSQL lives |
| `DB_USERNAME`, `DB_PASSWORD` | `postgres`, `postgres` | Database credentials |
| `DB_DATABASE` | `callstats` | Database name |
| `DB_SCHEMA` | `call_stats` | Schema the app creates and works in |
| `ADMIN_PASSWORD` | `admin` | Password for the admin account |
| `MEMBER_PASSWORD` | `member` | Password for the member account |
| `TOKEN_SECRET` | `change-me-in-production` | HMAC secret for login tokens |
| `TOKEN_EXPIRY_SECONDS` | `86400` | How long a login lasts |
| `CORS_ORIGINS` | `*` | Comma-separated allowed origins |

The database schema, the tables and the SQL functions used by the statistics are created on
startup. There are no migrations — if I change an entity I usually just drop the schema and
start over, which is fine for the amount of data this thing holds. Keep a `pg_dump` around if
your data matters.

A ready-built image is published to GHCR on every push to `main` (see
`.github/workflows/build-and-publish.yml`), so on a server you can point `compose.yml` at
`ghcr.io/<owner>/callstats` instead of building locally.

## Development

The comfortable way is the dev compose file, which runs the backend with `--reload` and the
Vite dev server with hot reload:

```bash
docker compose -f compose.dev.yml up
```

Frontend on <http://localhost:5174>, backend on <http://localhost:8888>, API docs at
<http://localhost:8888/docs>. Vite proxies `/api` to the backend, so both halves talk to each
other without CORS games.

Without Docker (there's a `shell.nix` with Node 24 and Python 3.14, direnv picks it up):

```bash
cd backend && pipenv sync
pipenv run uvicorn --app-dir src main:app --reload

cd frontend && npm install && npm run dev
```

You'll still need a PostgreSQL somewhere; `docker compose -f compose.dev.yml up database` is
the lazy option.

### Layout

```
backend/src/
  entities/   SQLModel models — these are both the tables and the API schemas
  services/   one module per resource, each exporting a FastAPI router
  data/       engine, session dependency, custom types, functions.sql
  web/        router composition, everything lives under /api
frontend/src/
  views/      pages, lazy-loaded by the router
  components/ the reusable bits, generic ones under components/base
  api/        axios wrappers, one file per resource
  interfaces/ the TypeScript side of the backend models
```

Two things worth knowing before you touch the code:

- Dates and times go over the API as unix timestamps. The backend converts them with a custom
  `EpochDate` type, the frontend has helpers in `src/scripts`.
- List endpoints return a `Page` object (`page`, `size`, `pages`, `entries`), not a bare array.

### Tests

There are two test files (`backend/src/services/test_calls.py`, `test_members.py`). They are
plain `unittest` cases and they talk to a real database instead of mocking anything, so run
them against the dev stack:

```bash
docker compose -f compose.dev.yml run --rm app pipenv run python -m unittest discover -s src/services -t src
```

pytest isn't in the Pipfile, so `python -m unittest` is the path of least resistance. Coverage
is thin either way. It's on the list.

## Caveats

- The auth is homemade: two shared accounts and an HMAC-signed token in localStorage. Good
  enough behind a VPN or a reverse proxy with TLS, not good enough on the open internet.
- No audit log — you can't tell who entered or deleted a call.
- The UI is in a mix of English and German, because the labels come from what people actually
  say in the fire station and I never got around to real i18n.
