# ClassicModels API (Week 2 Assignment)

## Overview

This project is a FastAPI service that exposes CRUD and relationship endpoints
for the ClassicModels sample database. It provides a clean REST interface over
customers, products, product lines, offices, employees, orders, order details,
and payments, plus basic table-count statistics.

## Key Features

- Full CRUD for core ClassicModels entities.
- Relationship endpoints (customer orders, employee reports, product order details, and more).
- Statistics endpoints for quick table counts.
- Automatic OpenAPI docs via Swagger UI and ReDoc.
- Structured logging to both stdout and a rotating log file.

## Tech Stack

- FastAPI, Uvicorn
- SQLAlchemy ORM
- Pydantic v2
- PostgreSQL
- Docker and Docker Compose
- Dynaconf and python-dotenv for configuration

## Project Structure

```
assignment/
	app/
		main.py              # FastAPI app entry point
		database.py          # SQLAlchemy setup and DB session
		models.py            # ORM models
		routers/             # API routes
		crud/                # DB access layer
		schema/              # Pydantic schemas
		logger.py            # Logging configuration
	configs/
		settings.yaml        # Optional Dynaconf settings (empty by default)
	seed.sql               # Schema and sample data
	Dockerfile
	docker-compose.yml
	requirements.txt
	.env                   # Local environment variables
```

## Setup

### Prerequisites

- Python 3.12
- PostgreSQL 16 (or Docker)
- pip

### Environment Variables

Create a `.env` file in `assignment/` (or update the existing one) with:

```
POSTGRES_USER=your_user
POSTGRES_PASSWORD=your_password
POSTGRES_DB=your_db
POSTGRES_PORT=5433
POSTGRES_HOST=localhost
DATABASE_URL=postgresql://your_user:your_password@localhost:5433/your_db
```

`DATABASE_URL` is required. The app will fail fast if it is missing.

### Database Initialization

Load the schema and sample data from `seed.sql`:

```
psql "$DATABASE_URL" -f seed.sql
```

If you use Docker Compose, either copy `seed.sql` to `init.sql` or update
`docker-compose.yml` to mount `seed.sql` into `/docker-entrypoint-initdb.d/`.

### Run Locally (without Docker)

```
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Run with Docker Compose

Set `DATABASE_URL` to point at the `db` service inside Docker, for example:

```
DATABASE_URL=postgresql://your_user:your_password@db:5432/your_db
```

Then start the stack:

```
docker compose up --build
```

## Usage

- Base URL: `http://localhost:8000`
- Health check: `GET /`
- Swagger UI: `GET /docs`
- ReDoc: `GET /redoc`

## API Resources (Base Paths)

Each resource supports standard CRUD operations unless noted.

- Customers: `/customers`
  - `/customers/{customerNumber}`
  - `/customers/{customerNumber}/orders`
  - `/customers/{customerNumber}/payments`
- Products: `/products`
  - `/products/{productCode}`
  - `/products/{productCode}/orderdetails`
- Product Lines: `/productlines`
  - `/productlines/{productLine}`
  - `/productlines/{productLine}/products`
- Offices: `/offices`
  - `/offices/{officeCode}`
  - `/offices/{officeCode}/employees`
- Employees: `/employees`
  - `/employees/{employeeNumber}`
  - `/employees/{employeeNumber}/customers`
  - `/employees/{employeeNumber}/reports`
- Orders: `/orders`
  - `/orders/{orderNumber}`
  - `/orders/{orderNumber}/orderdetails`
  - `/orders/customer/{customerNumber}`
- Order Details: `/orderdetails`
  - `/orderdetails/{orderNumber}/{productCode}`
  - `/orderdetails/order/{orderNumber}`
  - `/orderdetails/product/{productCode}`
- Payments: `/payments`
  - `/payments/{customerNumber}/{checkNumber}`
  - `/payments/customer/{customerNumber}`

### Statistics Endpoints

- `/customers/count`
- `/orders/count`
- `/products/count`
- `/employees/count`
- `/offices/count`
- `/payments/count`
- `/orderdetails/count`
- `/productlines/count`

## Logging

Logs are written to stdout and to `app.log` (rotating, 1 MB each, 5 backups).

## License

See `LICENSE`.
