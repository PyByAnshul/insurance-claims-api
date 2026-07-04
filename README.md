# Insurance Claims API

A FastAPI project for uploading insurance data from CSV files, validating and storing that data, calculating claim payouts, and exposing reporting endpoints over a SQLite-backed database.




https://github.com/user-attachments/assets/d01338c0-7242-4d90-9fc7-2dd7f37f1236



Project Working Video - https://youtu.be/-g1j7Z3xZEw

## Features

- Upload `customers`, `policies`, and `claims` CSV files in one request
- Clean and validate CSV columns and field formats before insert
- Reject duplicates and broken references between customers, policies, and claims
- Calculate final payouts using business rules
- Search claims with filters and sorting
- Retrieve top customers by payout
- Generate a state-wise payout report
- Expose a health check endpoint with database connectivity and uptime

## Tech Stack

- FastAPI
- SQLAlchemy 2
- Pydantic 2
- Pandas
- SQLite
- Alembic

## Project Structure

```text
app/
  api/            # Route handlers
  core/           # Config, logging, exceptions
  models/         # SQLAlchemy models and DB session
  repositories/   # Database access layer
  schemas/        # Pydantic request/response models
  services/       # Business logic
  utils/          # CSV cleaning helpers
migrations/       # Alembic migrations
run.py            # Local dev entrypoint
requirements.txt
```

## Setup

### 1. Create and activate a virtual environment

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 2. Install dependencies

```powershell
pip install -r requirements.txt
```

### 3. Configure environment variables

Create a `.env` file from `.env.example`.

```env
DATABASE_URL=sqlite:///./insurance_claims.db
APP_NAME=Insurance Claims API
LOG_LEVEL=INFO
```

### 4. Run the API

```powershell
python run.py
```

The API will start on `http://127.0.0.1:8000`.

## API Docs

- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

## Main Endpoints

### `POST /upload`

Upload three CSV files together:

- `customer_file`
- `policy_file`
- `claims_file`

Response includes:

- `total_records`
- `inserted`
- `rejected`
- `errors`

Example:

```powershell
curl -X POST "http://127.0.0.1:8000/upload" `
  -F "customer_file=@customers.csv" `
  -F "policy_file=@policies.csv" `
  -F "claims_file=@claims.csv"
```

### `GET /claims/{claim_id}`

Returns claim details plus related customer and policy information.

### `GET /claims`

Supported query parameters:

- `city`
- `state`
- `cause`
- `date_from`
- `date_to`
- `min_payout`
- `max_payout`
- `sort_by` = `claim_id | loss_date | final_payout | loss_amount`
- `sort_order` = `asc | desc`

### `GET /customers/top`

Query parameter:

- `n` = number of top customers to return, from `1` to `100`

### `GET /reports/state`

Returns per-state totals for:

- total claims
- average payout
- maximum payout
- total payout

### `GET /health`

Returns API health, database connection status, and uptime.

## CSV Requirements

### Customers CSV

Required columns:

- `customer_id`
- `name`
- `age`
- `city`
- `state`

Validation highlights:

- missing required columns are rejected
- rows with empty required values are removed
- `age` must be numeric and greater than `0`
- duplicate `customer_id` values are removed during cleaning and rejected if already in the database

### Policies CSV

Required columns:

- `policy_id`
- `customer_id`
- `policy_issue_date`
- `coverage_limit`
- `deductible`
- `state`

Validation highlights:

- `policy_issue_date` must be a valid date
- `coverage_limit` and `deductible` must be numeric
- each policy must reference an existing customer

### Claims CSV

Required columns:

- `claim_id`
- `policy_id`
- `loss_date`
- `loss_amount`
- `cause`

Validation highlights:

- `loss_date` must be a valid date
- `loss_amount` must be numeric
- each claim must reference an existing policy

## Payout Rules

The final payout is calculated using these rules:

1. Base payout = `min(loss_amount, coverage_limit) - deductible`
2. Payout cannot go below `0`
3. If customer age is below `18`, payout is reduced by `50%`
4. If claim cause is `flood` and policy state is `CA`, payout is reduced by `10%`
5. Claims are flagged as potential fraud when the related customer already has more than `5` claims

Claims are rejected when:

- `loss_amount` is negative
- `loss_date` is in the future
- `loss_date` is before the policy issue date

## Database and Migrations

This project uses SQLite by default and creates tables at startup with SQLAlchemy metadata. Alembic is also included for schema migrations.

Useful commands:

```powershell
alembic upgrade head
alembic revision --autogenerate -m "describe change"
```

## Notes

- The default local database file is `insurance_claims.db`
- Logging is request-based and includes method, path, status code, and response time
- The health endpoint reports connectivity by executing a simple database query


