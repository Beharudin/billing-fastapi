Core Billing (FastAPI) — README

This repository provides a multi-tenant billing system built with FastAPI, SQLAlchemy, Celery, and optional Stripe integration. It supports:

- Plan management (admin)
- Subscriptions (tenant)
- Usage metering
- Invoice generation
- Recording payments

This README explains how to run the project, the available endpoints, and recommended production steps.

Quick start (Docker)
--------------------
1. Copy `.env.example` to `.env` and set values:

```bash
cp .env.example .env
# edit .env with DATABASE_URL, POSTGRES_PASSWORD, JWT_SECRET, etc.
```

2. Start Docker Compose:

```bash
docker compose up --build
```

The API will be available at `http://localhost:8000`.

Local development (venv)
-----------------------
1. Create and activate a virtualenv:

```powershell
python -m venv .venv
.venv\\Scripts\\activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Create DB tables (development mode):

```bash
python -c "from core.database import Base, engine; Base.metadata.create_all(bind=engine)"
```

4. Run the API:

```bash
uvicorn main:app --reload
```

Environment variables
---------------------
The application reads configuration from `.env` using Pydantic `BaseSettings`.

Required/important values:
- `DATABASE_URL` — e.g. `postgresql://postgres:postgres@db:5432/postgres`
- `JWT_SECRET` — secret for signing JWTs
- `REDIS_URL` — Redis URL for Celery broker/backend

Optional (Stripe/mailer):
- `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET`
- `MAIL_USERNAME`, `MAIL_PASSWORD`, `MAIL_FROM`

Tenant (user) endpoints
-----------------------
Auth (`/auth`):
- POST `/auth/register` — register a new user
- POST `/auth/login` — login and receive access token

Billing (`/billing`):
- GET `/billing/plans` — list available plans
- POST `/billing/subscribe` — `{ "price_id": "<plan-id>" }` — create subscription + initial invoice
- POST `/billing/usage` — record usage `{ "feature": "api_calls", "quantity": 10, "subscription_id": "..." }`
- GET `/billing/usage` — list tenant usage events
- POST `/billing/generate-invoice` — generate invoice for tenant
- GET `/billing/invoices` — list tenant invoices
- POST `/billing/pay` — `{ "invoice_id":"...", "amount_cents": 1234 }` — record payment and mark invoice paid
- GET `/billing/subscriptions` — list tenant subscriptions
- POST `/billing/cancel-subscription` — `{ "subscription_id":"..." }` — cancel subscription

Admin endpoints (`/admin`) — require admin role
------------------------------------------------
- GET `/admin/revenue` — total succeeded payments
- POST `/admin/plans` — create plan
- GET `/admin/plans` — list plans
- PUT `/admin/plans/{plan_id}` — update plan
- DELETE `/admin/plans/{plan_id}` — delete plan
- GET `/admin/users` — list users
- POST `/admin/users/{user_id}/role` — update user role

Models overview
---------------
- `users`: app users (fields: id, email, password, role, tenant_id)
- `tenants`: tenant records (if used)
- `plans`: admin-created plans (name, price_cents, interval)
- `subscriptions`: tenant subscriptions
- `usage_events`: recorded usage
- `invoices`: invoices generated from plans + usage
- `payments`: payments recorded against invoices

Database migrations
-------------------
Use Alembic for migrations rather than `create_all` in production. Example:

```bash
pip install alembic
alembic init alembic
# configure alembic.ini to use DATABASE_URL
alembic revision --autogenerate -m "Initial"
alembic upgrade head
```

Quick Alembic usage (recommended)
---------------------------------
Ensure `DATABASE_URL` is set in your `.env` (or environment) so Alembic uses the same DB as the app. The repo `alembic/env.py` already reads `DATABASE_URL` from the app settings.

Bash / macOS / Linux:

```bash
# install alembic if needed
pip install alembic

# if this repo already contains alembic/ (it does), skip init
# generate an autogenerate revision from current models
alembic revision --autogenerate -m "initial"

# apply migrations
alembic upgrade head
```

PowerShell (Windows):

```powershell
# ensure env vars are loaded (from .env or set manually)
$env:DATABASE_URL = "postgresql://postgres:password@db:5432/postgres"

pip install alembic
alembic revision --autogenerate -m "initial"
alembic upgrade head
```

Notes:
- If you already have `alembic/` initialized in the repo, skip `alembic init alembic`.
- Run migrations in CI/CD or deployment steps rather than using `Base.metadata.create_all` in production.
- If `alembic revision --autogenerate` produces unexpected changes, inspect the generated revision before applying.

Running Celery workers
----------------------
Workers use `REDIS_URL` as broker and backend. Start via Docker Compose or locally:

```bash
celery -A workers.celery_app.celery worker --loglevel=info
```

Bootstrap admin (dev)
---------------------
To create an initial admin user from env variables:

```bash
export ADMIN_EMAIL=admin@example.com
export ADMIN_PASSWORD=changeme
python scripts/bootstrap_admin.py
```

Production process manager
--------------------------
Run the app with Gunicorn + Uvicorn workers in production:

```bash
gunicorn -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:8000 --workers 4
```

Tests and validation
--------------------
- Add unit tests around `generate_invoice()` and `pay_invoice()` to ensure billing correctness.
- Add linting and type-checking (mypy) in CI.

Production notes
----------------
- Keep secrets in a secret manager, not checked into source.
- Use Alembic for schema migrations.
- Add healthchecks and make startup resilient to DB/Redis delays.
- Use a robust process manager (Gunicorn with Uvicorn workers) or platform-managed ASGI.
- Add logging, monitoring, and alerts for billing-critical failures.

Need help?
-----------
I can:
- Add example `curl` requests or a Postman collection.
- Create Alembic migration files for the current models.
- Add an admin bootstrap script to create an initial admin user.

